from pathlib import Path
import shutil
import logging
import os
import io
from typing import Union, BinaryIO, Tuple
from fastapi import UploadFile
from config.settings import AUDIO_DIR, SUPPORTED_FORMATS, USE_MEMORY_STORAGE

# Configure logging
logger = logging.getLogger(__name__)

class FileHandler:
    # In-memory storage for Vercel environment
    memory_files = {}
    
    @staticmethod
    async def save_upload_file(upload_file: UploadFile) -> Union[Path, str]:
        """
        Save uploaded file either to disk or to memory based on environment
        Returns either a Path object (for disk storage) or a string key (for memory storage)
        """
        file_path = None
        memory_key = None
        
        try:
            if USE_MEMORY_STORAGE:
                # Store in memory for Vercel's read-only filesystem
                memory_key = f"memory_file_{upload_file.filename}"
                
                logger.info(f"Using in-memory storage for: {upload_file.filename}")
                
                # Read file content into memory
                content = await upload_file.read()
                FileHandler.memory_files[memory_key] = content
                
                logger.info(f"File stored in memory with key: {memory_key}")
                return memory_key
            else:
                # Standard file system storage for non-Vercel environments
                try:
                    # Create directory if it doesn't exist
                    AUDIO_DIR.mkdir(exist_ok=True)
                    
                    # Create file path
                    file_path = AUDIO_DIR / upload_file.filename
                    logger.info(f"Saving uploaded file to: {file_path}")
                    
                    # Save uploaded file
                    with file_path.open("wb") as buffer:
                        shutil.copyfileobj(upload_file.file, buffer)
                    
                    if not file_path.exists():
                        raise IOError("File was not saved successfully")
                        
                    logger.info("File saved successfully to disk")
                    return file_path
                except Exception as e:
                    logger.error(f"Error saving to disk, falling back to memory: {str(e)}")
                    
                    # Fallback to memory if disk storage fails
                    if file_path and os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                        except:
                            pass
                    
                    # Reset file position and read content
                    await upload_file.seek(0)
                    content = await upload_file.read()
                    
                    # Store in memory
                    memory_key = f"memory_file_{upload_file.filename}"
                    FileHandler.memory_files[memory_key] = content
                    logger.info(f"Fallback: File stored in memory with key: {memory_key}")
                    return memory_key
            
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

    @staticmethod
    def get_memory_file(memory_key: str) -> io.BytesIO:
        """
        Retrieve an in-memory file as a file-like object.
        """
        if memory_key not in FileHandler.memory_files:
            raise FileNotFoundError(f"Memory file with key {memory_key} not found")
        return io.BytesIO(FileHandler.memory_files[memory_key])