from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import logging
from typing import Union
from pathlib import Path

# Add debugging for imports
print("speech.py: Starting imports...")
try:
    from core.speech_recognition import SpeechRecognizer
    print("speech.py: Successfully imported SpeechRecognizer")
except Exception as e:
    print(f"speech.py: Failed to import SpeechRecognizer: {e}")
    SpeechRecognizer = None

try:
    from core.file_handler import FileHandler
    print("speech.py: Successfully imported FileHandler")
except Exception as e:
    print(f"speech.py: Failed to import FileHandler: {e}")
    FileHandler = None

try:
    from config.settings import USE_MEMORY_STORAGE
    print("speech.py: Successfully imported USE_MEMORY_STORAGE")
except Exception as e:
    print(f"speech.py: Failed to import USE_MEMORY_STORAGE: {e}")
    USE_MEMORY_STORAGE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
speech_recognizer = SpeechRecognizer()
file_handler = FileHandler()

@router.post("/transcribe")
async def transcribe_file(file: UploadFile):
    """
    Endpoint to transcribe an uploaded audio file
    Works with both file system and memory storage for Vercel compatibility
    """
    file_reference = None
    try:
        if not file_handler.validate_audio_format(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload WAV, AIFF, MP3 or FLAC files only."
            )
        
        # Save the uploaded file (to memory or disk based on environment)
        file_reference = await file_handler.save_upload_file(file)
        logger.info(f"File {'stored in memory' if USE_MEMORY_STORAGE else 'saved to disk'}")
        
        # Transcribe the audio file with enhanced features
        result = speech_recognizer.transcribe_audio(file_reference)
        logger.info("Transcription completed successfully")
        
        if result and result.get("text"):
            return JSONResponse(content={
                "text": result["text"],
                "confidence": result.get("confidence", 0),
                "service": result.get("service", "Unknown"),
                "success": True
            })
        else:
            raise HTTPException(status_code=400, detail="Could not transcribe the audio file")
            
    except HTTPException as he:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise he
    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the file (either from memory or disk)
        if file_reference:
            try:
                FileHandler.cleanup_file(file_reference)
                logger.info(f"Temporary {'memory' if isinstance(file_reference, str) else 'disk'} file cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up file: {str(e)}")