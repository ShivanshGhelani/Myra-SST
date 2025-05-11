from pathlib import Path
import shutil
import logging
from fastapi import UploadFile
from config.settings import AUDIO_DIR, SUPPORTED_FORMATS

# Configure logging
logger = logging.getLogger(__name__)

class FileHandler:
    @staticmethod
    async def save_upload_file(upload_file: UploadFile) -> Path:
        """Save uploaded file to audio directory and return the path"""
        file_path = None
        try:
            # Ensure audio directory exists
            AUDIO_DIR.mkdir(exist_ok=True)
            
            # Create file path
            file_path = AUDIO_DIR / upload_file.filename
            logger.info(f"Saving uploaded file to: {file_path}")
            
            # Save uploaded file
            with file_path.open("wb") as buffer:
                try:
                    shutil.copyfileobj(upload_file.file, buffer)
                except Exception as e:
                    logger.error(f"Error while writing file: {str(e)}")
                    raise IOError(f"Failed to write upload file: {str(e)}")
            
            if not file_path.exists():
                raise IOError("File was not saved successfully")
                
            logger.info("File saved successfully")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving upload file: {str(e)}", exc_info=True)
            # Clean up partial file if it exists
            if file_path and file_path.exists():
                try:
                    file_path.unlink()
                except Exception as cleanup_error:
                    logger.error(f"Error cleaning up failed upload: {str(cleanup_error)}")
            raise
        finally:
            try:
                upload_file.file.close()
            except Exception as e:
                logger.warning(f"Error closing upload file: {str(e)}")
    
    @staticmethod
    def validate_audio_format(filename: str) -> bool:
        """Validate if the file format is supported"""
        if not filename:
            logger.warning("Empty filename provided for validation")
            return False
            
        is_valid = filename.lower().endswith(SUPPORTED_FORMATS)
        if not is_valid:
            logger.warning(f"Unsupported audio format: {filename}")
        return is_valid