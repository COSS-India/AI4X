import os
import sys
from pathlib import Path
from faster_whisper import WhisperModel
from indicnlp.transliterate.unicode_transliterate import UnicodeIndicTransliterator
from indicnlp import common
from indicnlp.normalize.indic_normalize import IndicNormalizerFactory

INDIAN_LANG_CODES = {
    "Assamese": "as", "Bangla": "bn", "Boro": "brx", "Dogri": "doi", "Goan-Konkani": "gom", "Gujarati": "gu",
    "Hindi": "hi", "Kannada": "kn", "Kashmiri": "ks", "Maithili": "mai", "Malayalam": "ml", "Manipuri": "mni",
    "Marathi": "mr", "Nepali": "ne", "Oriya": "or", "Panjabi": "pa", "Sanskrit": "sa", "Santali": "sat",
    "Sindhi": "sd", "Tamil": "ta", "Telugu": "te", "Urdu": "ur", "English": "en"
}

TRANSLITERABLE_LANG_CODES = {
    "as", "bn", "brx", "gu", "hi", "kn", "ml", "mr", "ne",
    "or", "pa", "sa", "sd", "ta", "te", "ur"
}

def print_utf8(label: str, content: str):
    sys.stdout.buffer.write(f"{label}: {content}\n".encode("utf-8"))
    sys.stdout.flush()

def main():
    if len(sys.argv) != 3:
        print_utf8("ERROR", "Usage: python transcribe.py <wav_file_path> <language_name>")
        sys.exit(1)

    wav_path = Path(sys.argv[1])
    language_name = sys.argv[2].strip()

    if not wav_path.is_file():
        print_utf8("ERROR", f"WAV file not found: {wav_path}")
        sys.exit(1)

    if language_name not in INDIAN_LANG_CODES:
        print_utf8("ERROR", f"Unsupported language name: {language_name}")
        sys.exit(1)

    lang_code = INDIAN_LANG_CODES[language_name]

    project_root = Path(__file__).resolve().parents[3]
    model_path = project_root / "resources" / "faster-whisper-large-v2"
    indic_nlp_path = project_root / "resources" / "indic_nlp_resources"

    if not model_path.exists():
        print_utf8("ERROR", f"Model not found at: {model_path}")
        sys.exit(1)

    if not indic_nlp_path.exists():
        print_utf8("ERROR", f"Indic NLP resources not found at: {indic_nlp_path}")
        sys.exit(1)

    common.set_resources_path(str(indic_nlp_path))

    try:
        model = WhisperModel(str(model_path), compute_type="int8")
        segments, info = model.transcribe(str(wav_path), language=lang_code, beam_size=5)
        transcript = " ".join([seg.text for seg in segments]).strip()

        print_utf8("LANGUAGE", lang_code)
        print_utf8("TRANSCRIPTION", transcript)

        if lang_code in TRANSLITERABLE_LANG_CODES:
            normalizer = IndicNormalizerFactory().get_normalizer(lang_code)
            normalized_text = normalizer.normalize(transcript)
            transliterated = UnicodeIndicTransliterator.transliterate(normalized_text, lang_code, "native")
            print_utf8("TRANSLITERATED", transliterated)
        else:
            print_utf8("TRANSLITERATED", transcript)

    except Exception as e:
        print_utf8("ERROR", str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
