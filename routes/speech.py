from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import logging
from core.speech_recognition import SpeechRecognizer
from core.file_handler import FileHandler

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
    """
    file_path = None
    try:
        if not file_handler.validate_audio_format(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload WAV, AIFF, MP3 or FLAC files only."
            )
        
        # Save the uploaded file
        file_path = await file_handler.save_upload_file(file)
        logger.info(f"File saved successfully at: {file_path}")
        
        # Transcribe the audio file with enhanced features
        result = speech_recognizer.transcribe_audio(file_path)
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
        # Clean up the temporary file
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Temporary file removed: {file_path}")
            except Exception as e:
                logger.error(f"Error removing temporary file: {str(e)}")