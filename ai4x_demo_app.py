import psycopg2
import psycopg2.extras
import statistics
import time
import uuid
import numpy as np
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from services.nmt_service import NMTService
from services.llm_service import LLMService
from services.tts_service import TTSService
from services.weather_service import WeatherService
from metrics import prometheus_latest_text, metrics_collector
from config import Config
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Response
from fastapi.middleware.cors import CORSMiddleware
import threading
import asyncio

from prometheus_client import Gauge

# --- Prometheus core ---
# from prometheus_client import Counter, Histogram, Gauge

# ----------------------------
# Database connection
# ----------------------------
DB_CONFIG = {
    "user": "ai4xadmin",
    "password": "password123#",  # replace with your actual password or use env var
    "host": "ai4x.postgres.database.azure.com",
    "port": 5432,
    "database": "ai4xdemo"
}

nmt_service = NMTService()
llm_service = LLMService()
tts_service = TTSService()
weather_service = WeatherService()

TABLE_NAME = "ai4x_demo_requests_log_v6"

# ----------------------------
# Customer Tiers and Rate Limits
# ----------------------------
# Customer tier definitions with rate limits and usage quotas
CUSTOMER_TIERS = {
    "Basic": {
        "api_rate_limit_per_minute": 50,
        "llm_tokens_quota_per_month": 50000,      # 50K tokens per month
        "nmt_chars_quota_per_month": 100000,      # 100K characters per month
        "tts_chars_quota_per_month": 25000,       # 25K characters per month
        "description": "Basic tier for small organizations"
    },
    "Standard": {
        "api_rate_limit_per_minute": 100,
        "llm_tokens_quota_per_month": 150000,     # 150K tokens per month
        "nmt_chars_quota_per_month": 300000,      # 300K characters per month
        "tts_chars_quota_per_month": 75000,       # 75K characters per month
        "description": "Standard tier for medium organizations"
    },
    "Premium": {
        "api_rate_limit_per_minute": 150,
        "llm_tokens_quota_per_month": 500000,     # 500K tokens per month
        "nmt_chars_quota_per_month": 1000000,     # 1M characters per month
        "tts_chars_quota_per_month": 250000,      # 250K characters per month
        "description": "Premium tier for large organizations"
    }
}

# ----------------------------
# Customers and Apps Catalog
# ----------------------------
# Ten representative Indian public/govt-style customers with domain, onboarding dates, and tiers
CUSTOMERS = [
    {"name": "AgriSmart",        "domain": "agriculture",        "onboarding_date": "2023-01-15", "tier": "Basic"},
    {"name": "EduServe",         "domain": "education",          "onboarding_date": "2023-07-01", "tier": "Standard"},
    {"name": "SwasthyaCare",     "domain": "healthcare",         "onboarding_date": "2024-02-10", "tier": "Premium"},
    {"name": "BankSeva",         "domain": "banking",            "onboarding_date": "2024-09-05", "tier": "Premium"},
    {"name": "JanaSeva",         "domain": "citizen_services",   "onboarding_date": "2022-11-20", "tier": "Standard"},
    {"name": "UIDAI Connect",    "domain": "identity",           "onboarding_date": "2025-08-01", "tier": "Premium"},
    {"name": "RailConnect",      "domain": "transport",          "onboarding_date": "2024-12-01", "tier": "Standard"},
    {"name": "KrishiMitra",      "domain": "agriculture",        "onboarding_date": "2025-06-12", "tier": "Basic"},
    {"name": "ShikshaSetu",      "domain": "education",          "onboarding_date": "2022-05-18", "tier": "Basic"},
    {"name": "NagarPalika",      "domain": "municipal",          "onboarding_date": "2025-09-01", "tier": "Standard"}
]

# Three common reference applications used by all customers
APP_NAMES = [
    "UIDAI Support",
    "Banking Chat Support",
    "Citizen Services Helpdesk"
]

# ----------------------------
# Utility Functions
# ----------------------------
# ----------------------------
# Rate Limiting and Quota Management
# ----------------------------
import time
from collections import defaultdict
from datetime import datetime, timedelta

# In-memory storage for usage tracking
# In production, this should be moved to a database
usage_tracking = defaultdict(lambda: {
    "llm_tokens": 0,
    "nmt_chars": 0,
    "tts_chars": 0,
    "month": datetime.now().month,
    "year": datetime.now().year
})

def get_customer_domain(customer_name: str) -> str:
    """Get domain for a customer from the CUSTOMERS list."""
    for customer in CUSTOMERS:
        if customer["name"] == customer_name:
            return customer["domain"]
    return "unknown"

def get_customer_tier(customer_name: str) -> str:
    """Get tier for a customer from the CUSTOMERS list."""
    for customer in CUSTOMERS:
        if customer["name"] == customer_name:
            return customer["tier"]
    return "Basic"  # Default to Basic tier



def update_usage_metrics_for_customer(customer_name: str):
    """Update Prometheus usage metrics for a customer."""
    tier = get_customer_tier(customer_name)
    customer_usage = usage_tracking[customer_name]
    
    # Update Prometheus metrics (no rate limit tracking)
    metrics_collector.update_customer_usage(
        customer=customer_name,
        tier=tier,
        rate_limit_usage=0,  # Not tracking rate limits anymore
        llm_usage=customer_usage["llm_tokens"],
        nmt_usage=customer_usage["nmt_chars"],
        tts_usage=customer_usage["tts_chars"]
    )

def detect_language_from_text(text: str) -> str:
    text_lower = text.lower().strip()
    if any('\u0900' <= char <= '\u097F' for char in text): return "hi"
    if any('\u0B80' <= char <= '\u0BFF' for char in text): return "ta"
    if any('\u0C00' <= char <= '\u0C7F' for char in text): return "te"
    if any('\u0980' <= char <= '\u09FF' for char in text): return "bn"
    if any('\u0D00' <= char <= '\u0D7F' for char in text): return "ml"
    if any('\u0C80' <= char <= '\u0CFF' for char in text): return "kn"
    if any('\u0A80' <= char <= '\u0AFF' for char in text): return "gu"
    if any(word in text for word in ['का', 'आहे', 'मी', 'तू', 'ते', 'हे', 'या', 'ना']): return "mr"
    if any('\u0A00' <= char <= '\u0A7F' for char in text): return "pa"
    if any(word in text_lower for word in ['namaste', 'kaise', 'hai', 'mein', 'aap', 'kya', 'haan', 'nahi', 'dhanyawad']): return "hi"
    if any(word in text_lower for word in ['vanakkam', 'eppadi', 'irukkirathu', 'nandri', 'enna', 'illai', 'aam']): return "ta"
    return "en"

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            requestId TEXT PRIMARY KEY,
            customerName TEXT,
            customerApp TEXT,
            langdetectionLatency TEXT,
            nmtLatency TEXT,
            llmLatency TEXT,
            backNMTLatency TEXT,
            ttsLatency TEXT,
            overallPipelineLatency TEXT,
            nmtUsage TEXT,
            llmUsage TEXT,
            backNMTUsage TEXT,
            ttsUsage TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

init_db()

# Initialize system metrics
# Active tenants equals the number of configured customers
metrics_collector.set_active_tenants(len(CUSTOMERS))
metrics_collector.set_service_count("total", 3)  # NMT, LLM, TTS, ASR
metrics_collector.set_service_count("nmt", 1)
metrics_collector.set_service_count("llm", 1)
metrics_collector.set_service_count("tts", 1)
metrics_collector.set_service_count("asr", 1)

# Define simple pipelines per customer (all use NMT+LLM; some add TTS)
PIPELINES = {
    c["name"]: (["NMT", "LLM", "TTS"] if c["domain"] in ("citizen_services", "identity", "transport", "municipal") else ["NMT", "LLM"])  # speech added for public-facing domains
    for c in CUSTOMERS
}

# ----------------------------
# FastAPI app
# ----------------------------
app = FastAPI()
# Instrumentator().instrument(app).expose(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background task to update metrics
async def update_metrics_periodically():
    """Update system metrics every 30 seconds"""
    while True:
        try:
            # Update dynamic metrics (QoS, SLA, performance scores)
            # All metrics are now calculated from real request data
            metrics_collector.update_dynamic_metrics()
            
            # Update usage metrics for all customers
            for customer_info in CUSTOMERS:
                customer_name = customer_info["name"]
                update_usage_metrics_for_customer(customer_name)
            
        except Exception as e:
            print(f"Error updating metrics: {e}")
        
        await asyncio.sleep(30)  # Update every 30 seconds

@app.on_event("startup")
async def startup_event():
    """Start background tasks on app startup"""
    # Register customer metadata (domain, onboarding date, timestamp) in Prometheus
    from datetime import datetime
    for c in CUSTOMERS:
        dt = datetime.fromisoformat(c["onboarding_date"]).replace(tzinfo=timezone.utc)
        tier = c["tier"]
        tier_config = CUSTOMER_TIERS[tier]
        
        metrics_collector.register_customer(
            customer=c["name"],
            domain=c["domain"],
            onboarding_date=c["onboarding_date"],
            onboard_unix_ts=dt.timestamp(),
            tier=tier
        )
        
        # Set static quota limits for each customer
        metrics_collector.set_customer_quotas(
            customer=c["name"],
            tier=tier,
            rate_limit=tier_config["api_rate_limit_per_minute"],
            llm_quota=tier_config["llm_tokens_quota_per_month"],
            nmt_quota=tier_config["nmt_chars_quota_per_month"],
            tts_quota=tier_config["tts_chars_quota_per_month"]
        )
        
        # Initialize usage metrics to 0
        metrics_collector.update_customer_usage(
            customer=c["name"],
            tier=tier,
            rate_limit_usage=0,
            llm_usage=0,
            nmt_usage=0,
            tts_usage=0
        )
    
    asyncio.create_task(update_metrics_periodically())

# Add metrics endpoint
@app.get("/metrics")
def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=prometheus_latest_text(), media_type="text/plain")



class PipelineInput(BaseModel):
    customerName: str
    customerAppName: str
    input: Dict[str, str]

# ----------------------------
# Pipeline Endpoint
# ----------------------------
@app.post("/pipeline")
def run_pipeline(payload: PipelineInput):
    usage = {"NMT": None, "LLM": None, "TTS": None, "backNMT": None}
    customer = payload.customerName
    appname = payload.customerAppName
    # Normalize to our canonical customer names
    pipeline = PIPELINES.get(customer) or PIPELINES.get(customer.strip())
    if not pipeline:
        raise HTTPException(status_code=400, detail=f"No pipeline defined for customer {customer}")

    input_text = payload.input.get("text", "")
    target_language = payload.input.get("language", "en")

    request_id = str(uuid.uuid4())
    latencies = {}
    pipeline_output = {}

    success = True
    response_data = None
    
    # Track success status of each service
    service_success = {"NMT": False, "LLM": False, "BackNMT": False, "TTS": False}

    domain = get_customer_domain(customer)
    with metrics_collector.request_timer(customer, appname, "/pipeline", domain, "pipeline") as rid:
        try:
            # ---- Language Detection ----
            start = time.time()
            source_language = detect_language_from_text(input_text)
            latencies["LangDetection"] = f"{int((time.time() - start) * 1000)}ms"

            current_output = input_text

            # ---- NMT ----
            if "NMT" in pipeline:
                # Start component timing manually to control success tracking
                metrics_collector.start_component(rid, "NMT")
                try:
                    usage["NMT"] = str(len(current_output))
                    nmt_result = nmt_service.translate_text(current_output, source_language, target_language, customer, appname)
                    
                    # Capture and track actual resource usage for this NMT request
                    import psutil
                    cpu_usage = psutil.cpu_percent(interval=None)
                    memory_usage = psutil.virtual_memory().percent
                    metrics_collector.track_request_resource_usage("nmt", customer, appname, "/pipeline", 
                                                                 cpu_usage, memory_usage)
                    
                    latencies["NMT"] = f"{int((time.time() - start) * 1000)}ms"
                    pipeline_output["NMT"] = nmt_result.get("translated_text", current_output)
                    current_output = nmt_result.get("translated_text", current_output)
                    # Track success and only log metrics if NMT was successful
                    service_success["NMT"] = nmt_result.get("success", False)
                    
                    # End component with correct success status
                    metrics_collector.end_component(rid, "NMT", success=service_success["NMT"])
                    
                    if service_success["NMT"]:
                        metrics_collector.nmt_chars(customer, appname, source_language, target_language, len(nmt_result["translated_text"]))
                except Exception as e:
                    # Handle unexpected exceptions
                    metrics_collector.end_component(rid, "NMT", success=False)
                    raise

            # ---- LLM ----
            if "LLM" in pipeline:
                # Start component timing manually to control success tracking
                metrics_collector.start_component(rid, "LLM")
                try:
                    llm_result = llm_service.process_query(current_output, customer, appname)
                    
                    # Capture and track actual resource usage for this LLM request
                    cpu_usage = psutil.cpu_percent(interval=None)
                    memory_usage = psutil.virtual_memory().percent
                    metrics_collector.track_request_resource_usage("llm", customer, appname, "/pipeline", 
                                                                 cpu_usage, memory_usage)
                    
                    latencies["LLM"] = f"{int((time.time() - start) * 1000)}ms"
                    pipeline_output["LLM"] = llm_result.get("response", "")
                    response_data = llm_result.get("response", "")
                    usage["LLM"] = str(llm_result.get("total_tokens", 0))
                    # Track success and only log metrics if LLM was successful
                    service_success["LLM"] = llm_result.get("success", False)
                    
                    # End component with correct success status
                    metrics_collector.end_component(rid, "LLM", success=service_success["LLM"])
                    
                    if service_success["LLM"]:
                        total_tokens = llm_result.get("total_tokens", 0)
                        metrics_collector.llm_tokens(customer, appname, "gemini-2.5-flash", total_tokens)
                except Exception as e:
                    # Handle unexpected exceptions
                    metrics_collector.end_component(rid, "LLM", success=False)
                    raise

                # Backward NMT
                metrics_collector.start_component(rid, "BackNMT")
                try:
                    llm_response = llm_result.get("response", "")
                    usage["backNMT"] = str(len(llm_response))
                    back_translation = nmt_service.translate_text(
                        text=llm_response,
                        source_lang="en",
                        target_lang=source_language,
                        customer=customer,
                        app=appname
                    )
                    
                    # Capture and track actual resource usage for this BackNMT request
                    cpu_usage = psutil.cpu_percent(interval=None)
                    memory_usage = psutil.virtual_memory().percent
                    metrics_collector.track_request_resource_usage("nmt", customer, appname, "/pipeline", 
                                                                 cpu_usage, memory_usage)
                    
                    latencies["BackNMT"] = f"{int((time.time() - start) * 1000)}ms"
                    pipeline_output["BackNMT"] = back_translation.get("translated_text", llm_response)
                    # Track success and only log metrics if BackNMT was successful
                    service_success["BackNMT"] = back_translation.get("success", False)
                    
                    # End component with correct success status
                    metrics_collector.end_component(rid, "BackNMT", success=service_success["BackNMT"])
                    
                    if service_success["BackNMT"]:
                        metrics_collector.nmt_chars(customer, appname, "en", source_language, len(back_translation.get("translated_text", "")))
                    response_data = back_translation.get("translated_text", llm_response)
                except Exception as e:
                    # Handle unexpected exceptions
                    metrics_collector.end_component(rid, "BackNMT", success=False)
                    raise

            # ---- TTS ----
            if "TTS" in pipeline:
                # Start component timing manually to control success tracking
                metrics_collector.start_component(rid, "TTS")
                try:
                    usage["TTS"] = str(len(response_data))
                    tts_result = tts_service.text_to_speech(response_data, source_language, gender="female", customer=customer, app=appname)
                    
                    # Capture and track actual resource usage for this TTS request
                    cpu_usage = psutil.cpu_percent(interval=None)
                    memory_usage = psutil.virtual_memory().percent
                    metrics_collector.track_request_resource_usage("tts", customer, appname, "/pipeline", 
                                                                 cpu_usage, memory_usage)
                    
                    latencies["TTS"] = f"{int((time.time() - start) * 1000)}ms"
                    pipeline_output["TTS"] = tts_result.get("audio_content", "")
                    # Track success and only log metrics if TTS was successful
                    service_success["TTS"] = tts_result.get("success", False)
                    
                    # End component with correct success status
                    metrics_collector.end_component(rid, "TTS", success=service_success["TTS"])
                    
                    if service_success["TTS"]:
                        metrics_collector.tts_chars(customer, appname, source_language, len(response_data))
                    response_data = tts_result.get("audio_content", "")
                except Exception as e:
                    # Handle unexpected exceptions
                    metrics_collector.end_component(rid, "TTS", success=False)
                    raise

            # ---- DB Logging ----
            # Only log metrics for successful services
            conn = get_connection()
            cur = conn.cursor()
            
            # Only log metrics for services that were successful
            cur.execute(f"""
                INSERT INTO {TABLE_NAME} 
                (requestId, customerName, customerApp, langdetectionLatency, nmtLatency, llmLatency, backNMTLatency, ttsLatency, overallPipelineLatency,
                nmtUsage, llmUsage, backNMTUsage, ttsUsage, timestamp)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                request_id, customer, appname,
                latencies.get("LangDetection", None),
                latencies.get("NMT", None) if service_success["NMT"] else None,
                latencies.get("LLM", None) if service_success["LLM"] else None,
                latencies.get("BackNMT", None) if service_success["BackNMT"] else None,
                latencies.get("TTS", None) if service_success["TTS"] else None,
                latencies.get("pipelineTotal", None),
                str(usage.get("NMT", None)) if service_success["NMT"] else None,
                str(usage.get("LLM", None)) if service_success["LLM"] else None,
                str(usage.get("backNMT", None)) if service_success["BackNMT"] else None,
                str(usage.get("TTS", None)) if service_success["TTS"] else None,
                datetime.now(timezone.utc)
            ))
            conn.commit()
            cur.close()
            conn.close()
            
            # Update usage metrics in Prometheus after successful request
            update_usage_metrics_for_customer(customer)

        except Exception as e:
            success = False
            # Get information about which components failed
            failed_components = metrics_collector.get_request_component_failures(rid)
            error_detail = str(e)
            if failed_components:
                error_detail = f"{str(e)} (Failed components: {', '.join(failed_components)})"
            raise HTTPException(status_code=500, detail=error_detail)

    # Check if any components failed even if no exception was raised
    failed_components = metrics_collector.get_request_component_failures(rid)
    if failed_components:
        success = False

    return {
        "requestId": request_id,
        "status": "success" if success else "error",
        "pipelineOutput": pipeline_output,
        "responseData": response_data if success else None,
        "latency": latencies,
        "usage": usage,
        "failedComponents": failed_components if failed_components else None,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# ----------------------------
# Metrics & DB Endpoints
# ----------------------------
# @app.get("/metrics/system")
# def get_system_metrics():
#     CPU_USAGE.set(psutil.cpu_percent())
#     MEMORY_USAGE.set(psutil.virtual_memory().percent)
#     memory = psutil.virtual_memory()
#     return {
#         "cpu_usage_percent": psutil.cpu_percent(),
#         "memory_usage_bytes": memory.used,
#         "memory_usage_percent": memory.percent,
#         "memory_total_bytes": memory.total,
#         "memory_available_bytes": memory.available
#     }

# (customers endpoints remain same as in your code)

@app.get("/customers")
def get_all_customers():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(f"SELECT * FROM {TABLE_NAME}")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/customers/{customerName}")
def get_customer_by_name(customerName: str):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(f"SELECT * FROM {TABLE_NAME} WHERE customerName = %s", (customerName,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@app.get("/customer_aggregates")
def get_customer_aggregates(customerName: str):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute(f"""
        SELECT customerName, customerApp,
               langdetectionLatency, nmtLatency, llmLatency, backNMTLatency, ttsLatency, overallPipelineLatency,
               nmtUsage, llmUsage, backNMTUsage, ttsUsage
        FROM {TABLE_NAME}
        WHERE customerName = %s
    """, (customerName,))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return {"customerName": customerName, "aggregates": []}

    # Group data by customerApp
    grouped = {}
    for row in rows:
        app_key = row["customerapp"]
        if app_key not in grouped:
            grouped[app_key] = {k: [] for k in [
                "langdetectionlatency", "nmtlatency", "llmlatency", "backnmtlatency", "ttslatency", "overallpipelinelatency",
                "nmtusage", "llmusage", "backnmtusage", "ttsusage"
            ]}
        for col in grouped[app_key]:
            val = row.get(col)
            if val is None:
                grouped[app_key][col].append(None)
            else:
                try:
                    # Remove "ms" suffix if exists, convert to float
                    if isinstance(val, str) and val.endswith("ms"):
                        num = float(val.replace("ms", "").strip())
                    else:
                        num = float(val)
                    grouped[app_key][col].append(num)
                except Exception:
                    grouped[app_key][col].append(None)

    # Helpers for mean and percentiles
    def safe_mean(values):
        nums = [v for v in values if v is not None]
        return float(np.mean(nums)) if nums else None

    def safe_percentile(values, q):
        nums = [v for v in values if v is not None]
        return float(np.percentile(nums, q)) if nums else None

    # Compute aggregates per app
    aggregates = []
    for app_key, metrics in grouped.items():
        aggregates.append({
            "customerName": customerName,
            "customerApp": app_key,

            # Mean
            "avg_langdetectionLatency": safe_mean(metrics["langdetectionlatency"]),
            "avg_nmtLatency": safe_mean(metrics["nmtlatency"]),
            "avg_llmLatency": safe_mean(metrics["llmlatency"]),
            "avg_backNMTLatency": safe_mean(metrics["backnmtlatency"]),
            "avg_ttsLatency": safe_mean(metrics["ttslatency"]),
            "avg_overallPipelineLatency": safe_mean(metrics["overallpipelinelatency"]),
            "avg_nmtUsage": safe_mean(metrics["nmtusage"]),
            "avg_llmUsage": safe_mean(metrics["llmusage"]),
            "avg_backNMTUsage": safe_mean(metrics["backnmtusage"]),
            "avg_ttsUsage": safe_mean(metrics["ttsusage"]),

            # Percentiles
            "p90_langdetectionLatency": safe_percentile(metrics["langdetectionlatency"], 90),
            "p95_langdetectionLatency": safe_percentile(metrics["langdetectionlatency"], 95),
            "p99_langdetectionLatency": safe_percentile(metrics["langdetectionlatency"], 99),

            "p90_nmtLatency": safe_percentile(metrics["nmtlatency"], 90),
            "p95_nmtLatency": safe_percentile(metrics["nmtlatency"], 95),
            "p99_nmtLatency": safe_percentile(metrics["nmtlatency"], 99),

            "p90_llmLatency": safe_percentile(metrics["llmlatency"], 90),
            "p95_llmLatency": safe_percentile(metrics["llmlatency"], 95),
            "p99_llmLatency": safe_percentile(metrics["llmlatency"], 99),

            "p90_backNMTLatency": safe_percentile(metrics["backnmtlatency"], 90),
            "p95_backNMTLatency": safe_percentile(metrics["backnmtlatency"], 95),
            "p99_backNMTLatency": safe_percentile(metrics["backnmtlatency"], 99),

            "p90_ttsLatency": safe_percentile(metrics["ttslatency"], 90),
            "p95_ttsLatency": safe_percentile(metrics["ttslatency"], 95),
            "p99_ttsLatency": safe_percentile(metrics["ttslatency"], 99),

            "p90_overallPipelineLatency": safe_percentile(metrics["overallpipelinelatency"], 90),
            "p95_overallPipelineLatency": safe_percentile(metrics["overallpipelinelatency"], 95),
            "p99_overallPipelineLatency": safe_percentile(metrics["overallpipelinelatency"], 99),
        })

    return {
        "customerName": customerName,
        "aggregates": aggregates
    }



@app.get("/metrics/requests")
def get_request_metrics():
    """
    Returns request volume and API call counts:
    - Total number of API calls
    - API calls split by service (TTS, NMT, LLM, backNMT)
    - Customer-wise counts (total + per service)
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Fetch all requests
    cur.execute(f"""
        SELECT customerName, 
               (nmtLatency IS NOT NULL) AS hasNMT,
               (llmLatency IS NOT NULL) AS hasLLM,
               (ttsLatency IS NOT NULL) AS hasTTS,
               (backNMTLatency IS NOT NULL) AS hasBackNMT
        FROM {TABLE_NAME}
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    total_requests = len(rows)
    service_counts = {"NMT": 0, "LLM": 0, "TTS": 0, "backNMT": 0}
    customer_requests = {}

    for row in rows:
        cust = row["customername"]

        # Initialize per-customer dict if first time
        if cust not in customer_requests:
            customer_requests[cust] = {
                "total": 0,
                "by_service": {"NMT": 0, "LLM": 0, "TTS": 0, "backNMT": 0}
            }

        # Increment totals
        customer_requests[cust]["total"] += 1

        if row["hasnmt"]:
            service_counts["NMT"] += 1
            customer_requests[cust]["by_service"]["NMT"] += 1
        if row["hasllm"]:
            service_counts["LLM"] += 1
            customer_requests[cust]["by_service"]["LLM"] += 1
        if row["hastts"]:
            service_counts["TTS"] += 1
            customer_requests[cust]["by_service"]["TTS"] += 1
        if row["hasbacknmt"]:
            service_counts["backNMT"] += 1
            customer_requests[cust]["by_service"]["backNMT"] += 1

    return {
        "total_requests": total_requests,
        "requests_by_service": service_counts,
        "requests_by_customer": customer_requests
    }



@app.get("/metrics/data_processed")
def get_data_processed_metrics():
    """
    Returns data processed metrics:
    - NMT = total characters translated
    - TTS = total characters synthesized
    - LLM = total input tokens
    - backNMT = total characters back-translated
    Both total and customer-wise
    """
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute(f"""
        SELECT customerName,
               nmtUsage, llmUsage, ttsUsage, backNMTUsage
        FROM {TABLE_NAME}
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    totals = {"NMT_chars": 0, "LLM_tokens": 0, "TTS_chars": 0, "backNMT_chars": 0}
    customers = {}

    for row in rows:
        cust = row["customername"]
        if cust not in customers:
            customers[cust] = {"NMT_chars": 0, "LLM_tokens": 0, "TTS_chars": 0, "backNMT_chars": 0}

        def add_safe(val):
            try:
                return int(val) if val not in (None, "None") else 0
            except:
                return 0

        nmt = add_safe(row["nmtusage"])
        llm = add_safe(row["llmusage"])
        tts = add_safe(row["ttsusage"])
        backnmt = add_safe(row["backnmtusage"])

        customers[cust]["NMT_chars"] += nmt
        customers[cust]["LLM_tokens"] += llm
        customers[cust]["TTS_chars"] += tts
        customers[cust]["backNMT_chars"] += backnmt

        totals["NMT_chars"] += nmt
        totals["LLM_tokens"] += llm
        totals["TTS_chars"] += tts
        totals["backNMT_chars"] += backnmt

    return {
        "totals": totals,
        "byCustomer": customers
    }

# ----------------------------
# Pydantic Models for Individual Services
# ----------------------------
class NMTInput(BaseModel):
    customerName: str
    customerAppName: str
    text: str
    target_language: str = "en"

class TTSInput(BaseModel):
    customerName: str
    customerAppName: str
    text: str
    language: str = "en"
    gender: str = "female"

class LLMInput(BaseModel):
    customerName: str
    customerAppName: str
    text: str

# ----------------------------
# Individual Service Endpoints
# ----------------------------
@app.post("/nmt/translate")
def nmt_translate(payload: NMTInput):
    """NMT translation endpoint with automatic language detection"""
    customer = payload.customerName
    appname = payload.customerAppName
    text = payload.text
    target_lang = payload.target_language
    
    domain = get_customer_domain(customer)
    with metrics_collector.request_timer(customer, appname, "/nmt/translate", domain, "nmt") as rid:
        try:
            # Track service request
            metrics_collector.service_request("nmt", customer, appname)
            
            # Auto-detect source language
            source_lang = detect_language_from_text(text)
            
            # Start component timing manually to control success tracking
            metrics_collector.start_component(rid, "NMT")
            try:
                result = nmt_service.translate_text(text, source_lang, target_lang, customer, appname)
                
                # Capture and track actual resource usage for this NMT request
                import psutil
                cpu_usage = psutil.cpu_percent(interval=None)
                memory_usage = psutil.virtual_memory().percent
                metrics_collector.track_request_resource_usage("nmt", customer, appname, "/nmt/translate", 
                                                             cpu_usage, memory_usage)
                
                # End component with correct success status
                service_success = result.get("success", False)
                metrics_collector.end_component(rid, "NMT", success=service_success)
            except Exception as e:
                # Handle unexpected exceptions
                metrics_collector.end_component(rid, "NMT", success=False)
                raise
            
            # Track metrics if successful
            if result.get("success", False):
                translated_text = result.get("translated_text", "")
                metrics_collector.nmt_chars(customer, appname, source_lang, target_lang, len(translated_text))
                
                return {
                    "success": True,
                    "translated_text": translated_text,
                    "detected_source_language": source_lang,
                    "target_language": target_lang,
                    "character_count": len(translated_text)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Translation failed"),
                    "translated_text": text,  # Return original text as fallback
                    "detected_source_language": source_lang,
                    "target_language": target_lang
                }
                
        except Exception as e:
            # Get information about which components failed
            failed_components = metrics_collector.get_request_component_failures(rid)
            error_detail = f"NMT service error: {str(e)}"
            if failed_components:
                error_detail = f"{error_detail} (Failed components: {', '.join(failed_components)})"
            raise HTTPException(status_code=500, detail=error_detail)
    
    # Check if any components failed even if no exception was raised
    failed_components = metrics_collector.get_request_component_failures(rid)
    if failed_components:
        return {
            "success": False,
            "error": f"Component failures: {', '.join(failed_components)}",
            "translated_text": text,  # Return original text as fallback
            "detected_source_language": source_lang,
            "target_language": target_lang,
            "failedComponents": failed_components
        }

@app.post("/tts/speak")
def tts_speak(payload: TTSInput):
    """TTS speech synthesis endpoint"""
    customer = payload.customerName
    appname = payload.customerAppName
    text = payload.text
    language = payload.language
    gender = payload.gender
    
    domain = get_customer_domain(customer)
    with metrics_collector.request_timer(customer, appname, "/tts/speak", domain, "tts") as rid:
        try:
            # Track service request
            metrics_collector.service_request("tts", customer, appname)
            
            # Start component timing manually to control success tracking
            metrics_collector.start_component(rid, "TTS")
            try:
                result = tts_service.text_to_speech(text, language, gender, customer, appname)
                
                # Capture and track actual resource usage for this TTS request
                import psutil
                cpu_usage = psutil.cpu_percent(interval=None)
                memory_usage = psutil.virtual_memory().percent
                metrics_collector.track_request_resource_usage("tts", customer, appname, "/tts/speak", 
                                                             cpu_usage, memory_usage)
                
                # End component with correct success status
                service_success = result.get("success", False)
                metrics_collector.end_component(rid, "TTS", success=service_success)
            except Exception as e:
                # Handle unexpected exceptions
                metrics_collector.end_component(rid, "TTS", success=False)
                raise
            
            # Track metrics if successful
            if result.get("success", False):
                audio_content = result.get("audio_content", "")
                metrics_collector.tts_chars(customer, appname, language, len(text))
                
                return {
                    "success": True,
                    "audio_content": audio_content,
                    "language": language,
                    "gender": gender,
                    "character_count": len(text)
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "TTS synthesis failed"),
                    "audio_content": None,
                    "language": language,
                    "gender": gender
                }
                
        except Exception as e:
            # Get information about which components failed
            failed_components = metrics_collector.get_request_component_failures(rid)
            error_detail = f"TTS service error: {str(e)}"
            if failed_components:
                error_detail = f"{error_detail} (Failed components: {', '.join(failed_components)})"
            raise HTTPException(status_code=500, detail=error_detail)
    
    # Check if any components failed even if no exception was raised
    failed_components = metrics_collector.get_request_component_failures(rid)
    if failed_components:
        return {
            "success": False,
            "error": f"Component failures: {', '.join(failed_components)}",
            "audio_content": None,
            "language": language,
            "gender": gender,
            "failedComponents": failed_components
        }

@app.post("/llm/generate")
def llm_generate(payload: LLMInput):
    """LLM text generation endpoint"""
    customer = payload.customerName
    appname = payload.customerAppName
    text = payload.text
    
    domain = get_customer_domain(customer)
    with metrics_collector.request_timer(customer, appname, "/llm/generate", domain, "llm") as rid:
        try:
            # Track service request
            metrics_collector.service_request("llm", customer, appname)
            
            # Start component timing manually to control success tracking
            metrics_collector.start_component(rid, "LLM")
            try:
                result = llm_service.process_query(text, customer, appname)
                
                # Capture and track actual resource usage for this LLM request
                import psutil
                cpu_usage = psutil.cpu_percent(interval=None)
                memory_usage = psutil.virtual_memory().percent
                metrics_collector.track_request_resource_usage("llm", customer, appname, "/llm/generate", 
                                                             cpu_usage, memory_usage)
                
                # End component with correct success status
                service_success = result.get("success", False)
                metrics_collector.end_component(rid, "LLM", success=service_success)
            except Exception as e:
                # Handle unexpected exceptions
                metrics_collector.end_component(rid, "LLM", success=False)
                raise
            
            # Track metrics if successful
            if result.get("success", False):
                response_text = result.get("response", "")
                total_tokens = result.get("total_tokens", 0)
                metrics_collector.llm_tokens(customer, appname, "gemini-2.0-flash", total_tokens)
                
                return {
                    "success": True,
                    "response": response_text,
                    "intent": result.get("intent", "general"),
                    "confidence": result.get("confidence", 0.0),
                    "parameters": result.get("parameters", {}),
                    "token_count": total_tokens
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "LLM generation failed"),
                    "response": "I'm sorry, I couldn't process your request.",
                    "intent": "general",
                    "confidence": 0.0
                }
                
        except Exception as e:
            # Get information about which components failed
            failed_components = metrics_collector.get_request_component_failures(rid)
            error_detail = f"LLM service error: {str(e)}"
            if failed_components:
                error_detail = f"{error_detail} (Failed components: {', '.join(failed_components)})"
            raise HTTPException(status_code=500, detail=error_detail)
    
    # Check if any components failed even if no exception was raised
    failed_components = metrics_collector.get_request_component_failures(rid)
    if failed_components:
        return {
            "success": False,
            "error": f"Component failures: {', '.join(failed_components)}",
            "response": "I'm sorry, I couldn't process your request.",
            "intent": "general",
            "confidence": 0.0,
            "failedComponents": failed_components
        }

# ----------------------------
# Customer Tier and Usage Management Endpoints
# ----------------------------
@app.get("/customers/{customerName}/tier-info")
def get_customer_tier_info(customerName: str):
    """Get customer tier information and current usage"""
    tier = get_customer_tier(customerName)
    tier_config = CUSTOMER_TIERS[tier]
    customer_usage = usage_tracking[customerName]
    
    return {
        "customer": customerName,
        "tier": tier,
        "tier_config": tier_config,
        "current_usage": {
            "llm_tokens": {
                "current": customer_usage["llm_tokens"],
                "limit": tier_config["llm_tokens_quota_per_month"],
                "remaining": max(0, tier_config["llm_tokens_quota_per_month"] - customer_usage["llm_tokens"])
            },
            "nmt_chars": {
                "current": customer_usage["nmt_chars"],
                "limit": tier_config["nmt_chars_quota_per_month"],
                "remaining": max(0, tier_config["nmt_chars_quota_per_month"] - customer_usage["nmt_chars"])
            },
            "tts_chars": {
                "current": customer_usage["tts_chars"],
                "limit": tier_config["tts_chars_quota_per_month"],
                "remaining": max(0, tier_config["tts_chars_quota_per_month"] - customer_usage["tts_chars"])
            }
        },
        "usage_period": {
            "month": customer_usage["month"],
            "year": customer_usage["year"]
        }
    }

@app.get("/tiers")
def get_all_tiers():
    """Get information about all available tiers"""
    return {
        "tiers": CUSTOMER_TIERS,
        "customers_by_tier": {
            tier: [c["name"] for c in CUSTOMERS if c["tier"] == tier]
            for tier in CUSTOMER_TIERS.keys()
        }
    }

@app.get("/customers/usage-summary")
def get_all_customers_usage():
    """Get usage summary for all customers"""
    summary = {}
    for customer_info in CUSTOMERS:
        customer_name = customer_info["name"]
        tier = customer_info["tier"]
        tier_config = CUSTOMER_TIERS[tier]
        customer_usage = usage_tracking[customer_name]
        
        summary[customer_name] = {
            "domain": customer_info["domain"],
            "tier": tier,
            "usage_percentages": {
                "llm_tokens": (customer_usage["llm_tokens"] / tier_config["llm_tokens_quota_per_month"]) * 100,
                "nmt_chars": (customer_usage["nmt_chars"] / tier_config["nmt_chars_quota_per_month"]) * 100,
                "tts_chars": (customer_usage["tts_chars"] / tier_config["tts_chars_quota_per_month"]) * 100
            },
            "current_usage": {
                "llm_tokens_this_month": customer_usage["llm_tokens"],
                "nmt_chars_this_month": customer_usage["nmt_chars"],
                "tts_chars_this_month": customer_usage["tts_chars"]
            }
        }
    
    return {"customers": summary}


@app.get('/test_system_metrics')
def test_system_metrics():
    import traceback
    import psutil
    try:
        print("Testing system metrics...")
        # Test CPU
        cpu = psutil.cpu_percent(interval=1)
        print(f"CPU: {cpu}%")
        # Test Memory
        memory = psutil.virtual_memory()
        print(f"Memory: {memory.percent}%")
        # Test setting metrics
        print("Setting CPU_USAGE_PERCENT metric...")
        metrics_collector.set_cpu_usage_percent(cpu, "test", "test-customer", "test-app", "/test")
        print("Setting MEMORY_USAGE_PERCENT metric...")
        metrics_collector.set_memory_usage_percent(memory.percent, "test", "test-customer", "test-app", "/test")
        return f"SUCCESS - CPU: {cpu}%, Memory: {memory.percent}% - Check /metrics now!"
    except NameError as e:
        error_msg = f"NameError - Metrics not defined: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return f"ERROR: {error_msg}\n\nTraceback:\n{traceback.format_exc()}"
    except ImportError as e:
        error_msg = f"ImportError - psutil not available: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return f"ERROR: {error_msg}\n\nTraceback:\n{traceback.format_exc()}"
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        return f"ERROR: {error_msg}\n\nTraceback:\n{traceback.format_exc()}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ai4x_demo_app:app", host="0.0.0.0", port=8000, reload=False)