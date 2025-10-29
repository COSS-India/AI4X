from enum import Enum

from pydantic import BaseModel


class _ULCATaskType(str, Enum):
    ASR = "asr"
    TRANSLATION = "translation"
    TTS = "tts"
    TRANSLITERATION = "transliteration"
    NER = "ner"
    OCR = "ocr"
    TXT_LANG_DETECTION = "txt-lang-detection"
    AUDIO_LANG_DETECTION = "audio-lang-detection"
    SPEAKER_DIARIZATION = "speaker-diarization"
    LANGUAGE_DIARIZATION = "language-diarization"
    SPEAKER_VERIFICATION = "speaker-verification"
    TEXT_GENERATION = "text-generation"
    STS = "sts"  # TODO: Remove
    VAD = "vad"


# TODO: Depreciate soon
class _ULCATask(BaseModel):
    type: _ULCATaskType
