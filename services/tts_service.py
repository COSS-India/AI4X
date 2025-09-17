import requests
import json
import time
# import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class TTSService:
    def __init__(self):
        # Import metrics collector here to avoid circular imports
        from metrics import metrics_collector
        self.metrics_collector = metrics_collector
        self.tts_url = "https://api.dhruva.ekstep.ai/services/inference/tts"
        self.service_id = "ai4bharat/indic-tts-misc--gpu-t4"
        self.headers = {
            'Accept': '*/*',
            'User-Agent': 'Voice-Assistant-API',
            'Authorization': 'NvsNYWKA1GqQDvopXQZ6I7VzKAlv8LfGjcTNVyErIXzK_UPYfsKd0Wipespe2xvE',
            'Content-Type': 'application/json'
        }

    def _track_external_api_call(self, customer: str, app: str, status_code: int, duration: float, error_type: str = None):
        """Track external API call to Dhruva TTS service"""
        try:
            self.metrics_collector.track_external_api_call(
                external_service="dhruva",
                api_endpoint="tts", 
                customer=customer,
                app=app,
                status_code=status_code,
                duration=duration,
                error_type=error_type
            )
        except Exception as e:
            logger.warning(f"Failed to track external API call: {e}")
    
    def text_to_speech(self, text: str, language: str = "en", gender: str = "female", customer: str = "default", app: str = "default") -> Dict[str, Any]:
        """
        Convert text to speech using TTS API
        
        Args:
            text: Text to convert to speech
            language: Language code (e.g., 'en', 'ta', 'hi')
            gender: Voice gender ('male' or 'female')
            
        Returns:
            Dict containing TTS result with base64 audio
        """
        try:
            payload = {
                "taskType": "tts",
                "config": {
                    "language": {
                        "sourceLanguage": language
                    },
                    "gender": gender
                },
                "input": [
                    {
                        "source": text
                    }
                ]
            }

            
            # Make async request and track timing
            # loop = asyncio.get_event_loop()
            service_id = "ai4bharat/indic-tts-dravidian--gpu-t4" if language in ["ta", "te", "kn", "nl"] else "ai4bharat/indic-tts-indo-aryan--gpu-t4"
            start_time = time.time()
            response = requests.post(
                    f"{self.tts_url}?serviceId={service_id}",
                    headers=self.headers, 
                    json=payload, 
                    timeout=30
                )
            duration = time.time() - start_time
            
            # Track external API call
            self._track_external_api_call(customer, app, response.status_code, duration)
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract audio content
                if result.get("audio") and len(result["audio"]) > 0:
                    audio_content = result["audio"][0].get("audioContent", "")
                    
                    if audio_content:
                        logger.info(f"TTS successful for language: {language}")
                        return {
                            "success": True,
                            "audio_content": audio_content,
                            "config": result.get("config", {}),
                            "language": language,
                            "gender": gender,
                            "text": text
                        }
                
                return {
                    "success": False,
                    "error": "No audio content in TTS response",
                    "audio_content": None,
                    "language": language,
                    "gender": gender,
                    "text": text
                }
            else:
                logger.error(f"TTS API error: {response.status_code}")
                return {
                    "success": False,
                    "error": f"TTS API error: {response.status_code} - {response.text}",
                    "audio_content": None,
                    "language": language,
                    "gender": gender,
                    "text": text
                }
                
        except requests.exceptions.Timeout:
            logger.error(f"TTS API timeout for language: {language}")
            try:
                self.metrics_collector.track_external_api_timeout("dhruva", "tts", customer, app, 30.0)
            except:
                pass
            return {
                "success": False,
                "error": "TTS API timeout",
                "audio_content": None,
                "language": language,
                "gender": gender,
                "text": text
            }
        except requests.exceptions.ConnectionError:
            logger.error(f"TTS API connection error for language: {language}")
            try:
                self.metrics_collector.track_external_api_connection_error("dhruva", "tts", customer, app)
            except:
                pass
            return {
                "success": False,
                "error": "TTS API connection error",
                "audio_content": None,
                "language": language,
                "gender": gender,
                "text": text
            }
        except Exception as e:
            logger.error(f"TTS service error: {str(e)}")
            return {
                "success": False,
                "error": f"TTS service error: {str(e)}",
                "audio_content": None,
                "language": language,
                "gender": gender,
                "text": text
            }
    
    def batch_text_to_speech(self, texts: list, language: str = "en", gender: str = "female") -> Dict[str, Any]:
        """
        Convert multiple texts to speech
        
        Args:
            texts: List of texts to convert
            language: Language code
            gender: Voice gender
            
        Returns:
            Dict containing batch TTS results
        """
        try:
            payload = {
                "taskType": "tts",
                "config": {
                    "language": {
                        "sourceLanguage": language
                    },
                    "gender": gender
                },
                "input": [{"source": text} for text in texts]
            }
            service_id = "ai4bharat/indic-tts-dravidian--gpu-t4" if language in ["ta", "te", "kn", "nl"] else "ai4bharat/indic-tts-indo-aryan--gpu-t4"
            # loop = asyncio.get_event_loop()
            response = requests.post(
                    f"{self.tts_url}?serviceId={service_id}",
                    headers=self.headers, 
                    json=payload, 
                    timeout=60
                )
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get("audio"):
                    audio_contents = [item.get("audioContent", "") for item in result["audio"]]
                    
                    return {
                        "success": True,
                        "audio_contents": audio_contents,
                        "config": result.get("config", {}),
                        "language": language,
                        "gender": gender,
                        "texts": texts
                    }
            
            return {
                "success": False,
                "error": "Batch TTS failed",
                "audio_contents": [],
                "language": language,
                "gender": gender,
                "texts": texts
            }
            
        except Exception as e:
            logger.error(f"Batch TTS error: {str(e)}")
            return {
                "success": False,
                "error": f"Batch TTS error: {str(e)}",
                "audio_contents": [],
                "language": language,
                "gender": gender,
                "texts": texts
            }