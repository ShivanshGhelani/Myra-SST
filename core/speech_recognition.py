import speech_recognition as sr
from pathlib import Path
from typing import Union, Dict
import logging
from config.settings import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE

# Configure logging
logger = logging.getLogger(__name__)

class SpeechRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Adjust recognition parameters for better accuracy
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

    def transcribe_audio(self, audio_file_path: Union[str, Path]) -> Dict[str, str]:
        """
        Transcribe an audio file to text in any language with confidence score.
        """
        try:
            with sr.AudioFile(str(audio_file_path)) as source:
                logger.info(f"Processing audio file: {audio_file_path}")
                try:
                    # Adjust for ambient noise before processing
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio_data = self.recognizer.record(source)
                except Exception as e:
                    logger.error(f"Error reading audio file: {str(e)}")
                    raise ValueError(f"Failed to process audio file: {str(e)}")
                
                # Try multiple recognition services in order of reliability
                services = [
                    (self.try_google_recognition, "Google Speech Recognition"),
                    (self.try_sphinx_recognition, "Sphinx (Offline)"),
                ]
                
                last_error = None
                for recognition_func, service_name in services:
                    try:
                        logger.info(f"Attempting transcription with {service_name}")
                        result = recognition_func(audio_data)
                        if result:
                            logger.info(f"Successfully transcribed using {service_name}")
                            return {
                                "text": result["text"],
                                "confidence": result.get("confidence", 0.0),
                                "service": service_name
                            }
                    except sr.UnknownValueError:
                        logger.warning(f"{service_name} could not understand the audio")
                        last_error = "Speech was not understood"
                        continue
                    except sr.RequestError as e:
                        logger.error(f"{service_name} service failed: {str(e)}")
                        last_error = f"Service error: {str(e)}"
                        continue
                    except Exception as e:
                        logger.error(f"Unexpected error with {service_name}: {str(e)}")
                        last_error = str(e)
                        continue

                error_msg = last_error or "Could not recognize speech using any available service"
                logger.error(f"All transcription services failed: {error_msg}")
                raise ValueError(error_msg)
                
        except Exception as e:
            logger.error(f"Error processing {audio_file_path}: {str(e)}", exc_info=True)
            raise

    def try_google_recognition(self, audio_data) -> Dict[str, any]:
        """Try Google Speech Recognition with multiple languages"""
        for lang in [DEFAULT_LANGUAGE] + [l for l in SUPPORTED_LANGUAGES if l != DEFAULT_LANGUAGE]:
            try:
                logger.debug(f"Attempting Google recognition with language: {lang}")
                text = self.recognizer.recognize_google(audio_data, language=lang, show_all=True)
                if text and isinstance(text, dict) and text.get('alternative'):
                    best_result = text['alternative'][0]
                    return {
                        "text": best_result['transcript'],
                        "confidence": best_result.get('confidence', 0.0),
                        "language": lang
                    }
            except sr.UnknownValueError:
                logger.debug(f"Google recognition failed for language {lang}: Speech not understood")
                continue
            except sr.RequestError as e:
                logger.error(f"Google recognition service error: {str(e)}")
                break
        return None

    def try_sphinx_recognition(self, audio_data) -> Dict[str, any]:
        """Fallback to offline Sphinx recognition"""
        try:
            logger.debug("Attempting Sphinx recognition")
            text = self.recognizer.recognize_sphinx(audio_data)
            return {
                "text": text,
                "confidence": 0.6,  # Default confidence for Sphinx
                "language": "en-US"
            }
        except Exception as e:
            logger.debug(f"Sphinx recognition failed: {str(e)}")
            return None