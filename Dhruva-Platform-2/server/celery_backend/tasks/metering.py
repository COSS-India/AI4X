import base64
import io
import logging
import math
from typing import List, Optional

import soundfile as sf
from bson import ObjectId
from sqlalchemy.orm import Session

# Constant multipiers to calculate cost equivalents later
from .constants import (
    ASR_CPU_MULTIPLIER,
    ASR_GPU_MULTIPLIER,
    ASR_RAM_MULTIPLIER,
    NER_CPU_MULTIPLIER,
    NER_GPU_MULTIPLIER,
    NER_RAM_MULTIPLIER,
    NER_TOKEN_CALCULATION_MULTIPLIER,
    NMT_CPU_MULTIPLIER,
    NMT_GPU_MULTIPLIER,
    NMT_RAM_MULTIPLIER,
    NMT_TOKEN_CALCULATION_MULTIPLIER,
    TTS_CPU_MULTIPLIER,
    TTS_GPU_MULTIPLIER,
    TTS_RAM_MULTIPLIER,
    TTS_TOKEN_CALCULATION_MULTIPLIER,
)
from .database import AppDatabase
from .metering_database import ApiKey, engine

db = AppDatabase()


def get_audio_length(audio) -> float:
    file_handle = io.BytesIO(audio)
    data, sampling_rate = sf.read(file_handle)
    return data.shape[0] / sampling_rate


def calculate_asr_usage(data) -> int:
    total_usage = 0
    for d in data:
        audio = base64.b64decode(d["audioContent"])
        length = get_audio_length(audio)
        total_usage += math.ceil(
            length * ASR_GPU_MULTIPLIER * ASR_CPU_MULTIPLIER * ASR_RAM_MULTIPLIER
        )

    return total_usage


def calculate_translation_usage(data) -> int:
    # ** Note: **
    # Can't use respective tokenizers of different models since
    # the number of endpoints / models might grow to a large number
    # Using a standard tokenizer for all languages will require one
    # supporting all languages. Which is itself not accurate.
    # Hence using number of characters
    total_usage = 0
    for d in data:
        total_usage += (
            len(d["source"])
            * NMT_TOKEN_CALCULATION_MULTIPLIER
            * NMT_GPU_MULTIPLIER
            * NMT_CPU_MULTIPLIER
            * NMT_RAM_MULTIPLIER
        )

    return total_usage


def calculate_tts_usage(data: List) -> int:
    total_usage = 0
    for d in data:
        total_usage += (
            len(d["source"])
            * TTS_TOKEN_CALCULATION_MULTIPLIER
            * TTS_GPU_MULTIPLIER
            * TTS_CPU_MULTIPLIER
            * TTS_RAM_MULTIPLIER
        )

    return total_usage


def calculate_ner_usage(data: List) -> int:
    # ** Note: **
    # Can't use respective tokenizers of different models since
    # the number of endpoints / models might grow to a large number
    # Using a standard tokenizer for all languages will require one
    # supporting all languages. Which is itself not accurate.
    # Hence using number of characters
    total_usage = 0
    for d in data:
        total_usage += (
            len(d["source"])
            * NER_TOKEN_CALCULATION_MULTIPLIER
            * NER_GPU_MULTIPLIER
            * NER_CPU_MULTIPLIER
            * NER_RAM_MULTIPLIER
        )

    return total_usage


def write_to_db(
    api_key_id: str, inference_units: int, service_id: str, usage_type: str
):
    """Write usage data to PostgreSQL and TimescaleDB"""
    from db.postgresql_models import ApiKey as PostgreSQLApiKey, User as PostgreSQLUser
    from uuid import UUID

    # Get PostgreSQL session
    pg_session = db

    try:
        # Try to find API key by UUID first (new format)
        try:
            api_key_uuid = UUID(api_key_id)
            api_key = pg_session.query(PostgreSQLApiKey).filter(
                PostgreSQLApiKey.id == api_key_uuid
            ).first()
        except ValueError:
            # If not UUID, try to find by api_key string
            api_key = pg_session.query(PostgreSQLApiKey).filter(
                PostgreSQLApiKey.api_key == api_key_id
            ).first()

        if not api_key:
            print(f"No API key found for: {api_key_id}")
            return

        # Get user information
        user = pg_session.query(PostgreSQLUser).filter(
            PostgreSQLUser.id == api_key.user_id
        ).first()

        if not user:
            print("Invalid user id for API key")
            return

        # Write to TimescaleDB for time-series analytics
        with Session(engine) as timescale_session:
            api_key_record = ApiKey(
                api_key_id=str(api_key.id),
                api_key_name=api_key.name,
                user_id=str(user.id),
                user_email=user.email,
                inference_service_id=service_id,
                task_type=usage_type,
                usage=inference_units,
            )

            timescale_session.add(api_key_record)
            timescale_session.commit()

        # Update PostgreSQL API key usage counters
        try:
            api_key.usage += inference_units
            api_key.hits += 1
            pg_session.commit()
            print(f"Updated PostgreSQL usage: +{inference_units} units, +1 hit for API key {api_key_id}")
        except Exception as e:
            print(f"Error updating PostgreSQL usage counters: {e}")
            pg_session.rollback()

    except Exception as e:
        print(f"Error in write_to_db: {e}")
        pg_session.rollback()


def meter_usage(
    api_key_id: Optional[str], input_data: List, usage_type: str, service_id: str
):
    """Meters usage and writes to PostgreSQL and TimescaleDB"""
    if not api_key_id:
        return

    inference_units = 0
    if usage_type == "asr":
        inference_units = calculate_asr_usage(input_data)
    elif usage_type == "translation" or usage_type == "transliteration":
        inference_units = calculate_translation_usage(input_data)
    elif usage_type == "tts":
        inference_units = calculate_tts_usage(input_data)

    logging.info(f"inference units: {inference_units}")
    write_to_db(api_key_id, inference_units, service_id, usage_type)
