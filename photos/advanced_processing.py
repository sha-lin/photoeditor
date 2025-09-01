import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from sklearn.cluster import KMeans
import io
from django.core.files.base import ContentFile

class AdvancedImageProcessor:
    
    @staticmethod
    def smart_resize(image_path, max_width=1920, max_height=1080, maintain_aspect=True):
        """Smart resize with aspect ratio maintenance"""
        try:
            with Image.open(image_path) as img:
                original_width, original_height = img.size
                
                if maintain_aspect:
                    # Calculate aspect ratio
                    aspect_ratio = original_width / original_height
                    
                    if aspect_ratio > 1:  # Landscape
                        new_width = min(max_width, original_width)
                        new_height = int(new_width / aspect_ratio)
                    else:  # Portrait or square
                        new_height = min(max_height, original_height)
                        new_width = int(new_height * aspect_ratio)
                    
                    # Only resize if image is larger than target
                    if new_width < original_width or new_height < original_height:
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=85, optimize=True)
                output.seek(0)
                
                return ContentFile(output.getvalue())
        except Exception as e:
            print(f"Error in smart resize: {e}")
            return None
    
    @staticmethod
    def remove_watermark_by_color(image_path, color_threshold=30):
        """Remove watermark by detecting similar colors"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # Convert to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Reshape image to be a list of pixels
            pixels = img_rgb.reshape((-1, 3))
            
            # Use KMeans to find dominant colors
            kmeans = KMeans(n_clusters=5, random_state=42)
            kmeans.fit(pixels)
            
            # Get colors
            colors = kmeans.cluster_centers_.astype(int)
            
            # Find potential watermark colors (usually light colors)
            watermark_colors = []
            for color in colors:
                # Check if color is light (high brightness)
                brightness = np.mean(color)
                if brightness > 180:  # Light colors
                    watermark_colors.append(color)
            
            # Create mask for watermark colors
            mask = np.zeros(img_rgb.shape[:2], dtype=np.uint8)
            
            for color in watermark_colors:
                # Create color range
                lower = np.array([max(0, c - color_threshold) for c in color])
                upper = np.array([min(255, c + color_threshold) for c in color])
                
                # Create mask for this color
                color_mask = cv2.inRange(img_rgb, lower, upper)
                mask = cv2.bitwise_or(mask, color_mask)
            
            # Morphological operations to clean up mask
            kernel = np.ones((3, 3), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Apply inpainting
            result = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
            
            # Convert back to RGB and save
            result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(result_rgb)
            
            output = io.BytesIO()
            pil_image.save(output, format='JPEG', quality=90)
            output.seek(0)
            
            return ContentFile(output.getvalue())
            
        except Exception as e:
            print(f"Error in color-based watermark removal: {e}")
            return None
    
    @staticmethod
    def enhance_image_quality(image_path, enhance_contrast=True, enhance_sharpness=True, reduce_noise=True):
        """Enhance image quality after processing"""
        try:
            with Image.open(image_path) as img:
                # Enhance contrast
                if enhance_contrast:
                    enhancer = ImageEnhance.Contrast(img)
                    img = enhancer.enhance(1.2)  # Increase contrast by 20%
                
                # Enhance sharpness
                if enhance_sharpness:
                    enhancer = ImageEnhance.Sharpness(img)
                    img = enhancer.enhance(1.1)  # Increase sharpness by 10%
                
                # Reduce noise (apply slight blur then sharpen)
                if reduce_noise:
                    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
                    img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=120, threshold=2))
                
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=92, optimize=True)
                output.seek(0)
                
                return ContentFile(output.getvalue())
                
        except Exception as e:
            print(f"Error enhancing image quality: {e}")
            return None