"""
Middleware for Dhruva Observability Plugin

Handles request tracking, service detection, and metrics collection.
"""
import time
import jwt
import json
import base64
import io
import wave
from typing import Optional, Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from .config import PluginConfig
from .metrics import MetricsCollector


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking requests and collecting metrics."""
    
    def __init__(self, app, metrics_collector: Optional[MetricsCollector] = None, 
                 config: Optional[PluginConfig] = None):
        """Initialize middleware."""
        super().__init__(app)
        self.metrics_collector = metrics_collector or MetricsCollector()
        self.config = config or PluginConfig()
    
    async def dispatch(self, request: Request, call_next):
        """Process request through middleware."""
        if not self.config.enabled:
            return await call_next(request)
        
        start_time = time.time()
        
        # Extract metadata from request
        path = request.url.path
        method = request.method
        headers = request.headers
        
        # Extract customer and app (including from JWT token)
        customer, app = self._extract_customer_app(request)
        
        # Detect service type
        service_type = self._detect_service_type(path)
        
        # Extract real character count for TTS, translation, and ASR requests
        tts_characters = 0
        translation_characters = 0
        asr_audio_length = 0
        if service_type == "tts" and method == "POST":
            tts_characters = await self._extract_tts_characters(request)
        elif service_type == "translation" and method == "POST":
            translation_characters = await self._extract_translation_characters(request)
        elif service_type == "asr" and method == "POST":
            asr_audio_length = await self._extract_asr_audio_length(request)
        
        # Debug logging
        if self.config.debug:
            print(f"🔍 Request: {method} {path} -> Service: {service_type}, Customer: {customer}, App: {app}")
            if tts_characters > 0:
                print(f"📝 TTS Characters detected: {tts_characters}")
            if translation_characters > 0:
                print(f"📝 Translation Characters detected: {translation_characters}")
            if asr_audio_length > 0:
                print(f"🎵 ASR Audio length detected: {asr_audio_length:.2f} seconds")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Track request
        try:
            self.metrics_collector.track_request(
                customer=customer,
                app=app,
                method=method,
                endpoint=path,
                status_code=response.status_code,
                duration=duration,
                service_type=service_type
            )
            
            # Track additional metrics based on service type
            self._track_additional_metrics(customer, app, service_type, path, duration, tts_characters, translation_characters, asr_audio_length)
            
        except Exception as e:
            # Don't let metrics collection break the request
            if self.config.debug:
                print(f"⚠️ Metrics collection failed: {e}")

        return response
    
    def _decode_jwt_token(self, authorization_header: str) -> Optional[Dict[str, Any]]:
        """Decode JWT token from authorization header."""
        try:
            # Extract token from "Bearer <token>" format
            if not authorization_header.startswith("Bearer "):
                return None
            
            token = authorization_header[7:]  # Remove "Bearer " prefix
            
            # Decode without verification to get claims (for customer name extraction)
            # In production, you might want to verify the token with proper secret
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            
            return decoded_token
        except Exception as e:
            if self.config.debug:
                print(f"⚠️ JWT decoding failed: {e}")
            return None
    
    def _extract_customer_from_token(self, request: Request) -> str:
        """Extract customer name from JWT token in authorization header."""
        auth_header = request.headers.get("authorization", "")
        
        if auth_header:
            decoded_token = self._decode_jwt_token(auth_header)
            if decoded_token:
                # Extract customer name from 'name' field in token
                customer_name = decoded_token.get("name")
                if customer_name:
                    if self.config.debug:
                        print(f"🔑 Extracted customer from JWT: {customer_name}")
                    return customer_name
                
                # Fallback: try to extract from 'sub' field if 'name' is not available
                sub = decoded_token.get("sub")
                if sub:
                    if self.config.debug:
                        print(f"🔑 Using 'sub' field as customer: {sub}")
                    return sub
        
        return self.config.default_customer
    
    def _extract_customer_app(self, request: Request) -> tuple:
        """Extract customer and app from request headers and JWT token."""
        # First try to get customer from JWT token
        customer = self._extract_customer_from_token(request)
        
        # If not found in token, fallback to header
        if customer == self.config.default_customer:
            customer = request.headers.get("X-Customer-ID", customer)
        
        app = request.headers.get("X-App-ID", self.config.default_app)
        
        # Validate against allowed lists
        if not self.config.is_customer_allowed(customer):
            customer = self.config.default_customer
        if not self.config.is_app_allowed(app):
            app = self.config.default_app
            
        return customer, app
    
    def _detect_service_type(self, path: str) -> str:
        """Detect service type from URL path."""
        path_lower = path.lower()
        
        # Check for specific service patterns
        if any(pattern in path_lower for pattern in ["/translation", "/nmt", "/translate"]):
            return "translation"
        elif any(pattern in path_lower for pattern in ["/asr", "/transcribe", "/speech"]):
            return "asr"
        elif any(pattern in path_lower for pattern in ["/tts", "/synthesize", "/speak"]):
            return "tts"
        elif any(pattern in path_lower for pattern in ["/ner", "/entity", "/entities"]):
            return "ner"
        elif any(pattern in path_lower for pattern in ["/transliteration", "/xlit", "/transliterate"]):
            return "transliteration"
        elif any(pattern in path_lower for pattern in ["/llm", "/generate", "/chat", "/completion"]):
            return "llm"
        elif any(pattern in path_lower for pattern in ["/enterprise", "/health", "/metrics", "/config"]):
            return "enterprise"
        elif any(pattern in path_lower for pattern in ["/docs", "/openapi", "/redoc"]):
            return "documentation"
        else:
            return "unknown"
    
    def _track_additional_metrics(self, customer: str, app: str, service_type: str, path: str, duration: float, tts_characters: int = 0, translation_characters: int = 0, asr_audio_length: float = 0):
        """Track additional metrics based on service type."""
        try:
            # Track component latency
            self.metrics_collector.track_component_latency(
                customer=customer,
                app=app,
                component=service_type,
                duration=duration
            )
            
            # Track data processing based on service type
            if service_type == "llm":
                # Mock LLM token processing
                tokens = self._estimate_llm_tokens(path)
                self.metrics_collector.track_llm_tokens(
                    customer=customer,
                    app=app,
                    model="gpt-3.5-turbo",  # Mock model
                    tokens=tokens
                )
            elif service_type == "tts":
                # Track real TTS character count
                if tts_characters > 0:
                    self.metrics_collector.track_tts_characters(
                        customer=customer,
                        app=app,
                        language="en",  # Default language
                        characters=tts_characters
                    )
                    if self.config.debug:
                        print(f"📊 Tracked real TTS characters: {tts_characters}")
            elif service_type == "translation":
                # Track real translation character count
                if translation_characters > 0:
                    self.metrics_collector.track_nmt_characters(
                        customer=customer,
                        app=app,
                        source_lang="en",  # Default source language
                        target_lang="hi",  # Default target language
                        characters=translation_characters
                    )
                    if self.config.debug:
                        print(f"📊 Tracked real translation characters: {translation_characters}")
            elif service_type == "asr":
                # Track real ASR audio length
                if asr_audio_length > 0:
                    # Track as data processing (audio seconds)
                    self.metrics_collector.track_data_processing(
                        customer=customer,
                        app=app,
                        data_type="asr_audio_seconds",
                        amount=int(asr_audio_length)
                    )
                    if self.config.debug:
                        print(f"📊 Tracked real ASR audio length: {asr_audio_length:.2f} seconds")
            
            # Update SLA compliance (mock calculation)
            compliance = self._calculate_sla_compliance(service_type, duration)
            self.metrics_collector.update_sla_compliance(
                customer=customer,
                app=app,
                sla_type=f"{service_type}_availability",
                compliance_percent=compliance
            )
            
        except Exception as e:
            if self.config.debug:
                print(f"⚠️ Additional metrics tracking failed: {e}")
    
    def _estimate_llm_tokens(self, path: str) -> int:
        """Estimate LLM tokens based on path."""
        # Mock estimation - in real implementation, this would analyze request content
        return 100  # Mock value
    
    
    
    async def _extract_tts_characters(self, request: Request) -> int:
        """Extract real character count from TTS request body."""
        try:
            # Read the request body
            body = await request.body()
            if not body:
                return 0
            
            # Parse JSON request
            request_data = json.loads(body.decode('utf-8'))
            
            # Extract character count from TTS input
            total_characters = 0
            if 'input' in request_data:
                for input_item in request_data['input']:
                    if 'source' in input_item:
                        total_characters += len(input_item['source'])
            
            return total_characters
            
        except Exception as e:
            if self.config.debug:
                print(f"⚠️ Failed to extract TTS characters: {e}")
            return 0
    
    async def _extract_translation_characters(self, request: Request) -> int:
        """Extract real character count from translation request body."""
        try:
            # Read the request body
            body = await request.body()
            if not body:
                return 0
            
            # Parse JSON request
            request_data = json.loads(body.decode('utf-8'))
            
            # Extract character count from translation input
            total_characters = 0
            if 'input' in request_data:
                for input_item in request_data['input']:
                    if 'source' in input_item:
                        total_characters += len(input_item['source'])
            
            return total_characters
            
        except Exception as e:
            if self.config.debug:
                print(f"⚠️ Failed to extract translation characters: {e}")
            return 0
    
    async def _extract_asr_audio_length(self, request: Request) -> float:
        """Extract real audio length in seconds from ASR request body."""
        try:
            # Read the request body
            body = await request.body()
            if not body:
                return 0.0
            
            # Parse JSON request
            request_data = json.loads(body.decode('utf-8'))
            
            # Extract audio length from ASR input
            total_audio_length = 0.0
            if 'inputData' in request_data and 'audio' in request_data['inputData']:
                for audio_item in request_data['inputData']['audio']:
                    if 'audioContent' in audio_item:
                        # Decode base64 audio and calculate length
                        audio_length = self._calculate_audio_length_from_base64(audio_item['audioContent'])
                        total_audio_length += audio_length
            
            return total_audio_length
            
        except Exception as e:
            if self.config.debug:
                print(f"⚠️ Failed to extract ASR audio length: {e}")
            return 0.0
    
    def _calculate_audio_length_from_base64(self, base64_audio: str) -> float:
        """Calculate audio length in seconds from base64 encoded audio."""
        try:
            # Decode base64 audio
            audio_data = base64.b64decode(base64_audio)
            
            # Create a BytesIO object to read the audio data
            audio_buffer = io.BytesIO(audio_data)
            
            # Try to read as WAV file
            with wave.open(audio_buffer, 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / float(sample_rate)
                return duration
                
        except Exception as e:
            if self.config.debug:
                print(f"⚠️ Failed to calculate audio length: {e}")
            # Fallback: estimate based on data size (rough approximation)
            try:
                audio_data = base64.b64decode(base64_audio)
                # Rough estimate: 16-bit audio at 16kHz = 32KB per second
                estimated_duration = len(audio_data) / 32000
                return estimated_duration
            except:
                return 0.0
    
    def _calculate_sla_compliance(self, service_type: str, duration: float) -> float:
        """Calculate SLA compliance based on service type and duration."""
        # Mock SLA compliance calculation
        if service_type == "llm":
            return 99.5 if duration < 2.0 else 95.0
        elif service_type == "tts":
            return 99.8 if duration < 1.0 else 97.0
        elif service_type == "translation":
            return 99.9 if duration < 0.5 else 98.0
        else:
            return 99.0
