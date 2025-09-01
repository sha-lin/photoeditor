class ImageProcessingError(Exception):
    """Custom exception for image processing errors"""
    pass

class UnsupportedImageFormat(ImageProcessingError):
    """Raised when image format is not supported"""
    pass

class ImageTooLarge(ImageProcessingError):
    """Raised when image file is too large"""
    pass

class WatermarkRemovalFailed(ImageProcessingError):
    """Raised when watermark removal fails"""
    pass