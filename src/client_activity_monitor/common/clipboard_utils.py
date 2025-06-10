import pyperclip
from pathlib import Path
from loguru import logger

def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to system clipboard.
    
    Args:
        text: Text to copy
        
    Returns:
        True if successful, False otherwise
    """
    try:
        pyperclip.copy(text)
        logger.info("Copied to clipboard successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to copy to clipboard: {e}")
        return False
        
def copy_file_path(filepath: Path) -> bool:
    """
    Copy file path to clipboard.
    
    Args:
        filepath: Path object to copy
        
    Returns:
        True if successful, False otherwise
    """
    return copy_to_clipboard(str(filepath.absolute()))