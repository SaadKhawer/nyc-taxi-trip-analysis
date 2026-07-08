import os
import requests
import logging

def setup_logger(name: str) -> logging.Logger:
    """
    Setup a logger for a given module.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Prevent duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

logger = setup_logger(__name__)

def download_file(url: str, dest_path: str) -> None:
    """
    Download a file from a URL to a destination path.
    """
    if os.path.exists(dest_path):
        logger.info(f"File already exists at {dest_path}")
        return

    logger.info(f"Downloading {url} to {dest_path}")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(dest_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    logger.info(f"Download complete.")


# Verify that the downloaded file exists, is not empty, and log its size before further processing.
def validate_file(file_path: str) -> bool:
    """
    Validate that the file exists and verify its size.
    """
    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return False
        
    size_bytes = os.path.getsize(file_path)
    size_mb = size_bytes / (1024 * 1024)
    logger.info(f"File {file_path} exists. Size: {size_mb:.2f} MB")
    
    if size_bytes == 0:
        logger.error(f"File {file_path} is empty.")
        return False
        
    return True
