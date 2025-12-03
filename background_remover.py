"""Background removal module for solid color backgrounds."""

import cv2
import numpy as np
from PIL import Image
from config import BACKGROUND_COLORS, COLOR_TOLERANCE


class BackgroundRemover:
    """Handles removal of solid color backgrounds from images."""

    def __init__(self, tolerance=COLOR_TOLERANCE):
        self.tolerance = tolerance
        self.bg_colors = BACKGROUND_COLORS

    def remove_color_background(self, image, color_name=None, custom_color=None):
        """Remove a solid color background from the image.

        Args:
            image: numpy array of the image (BGR format)
            color_name: Name of the color to remove (white, green, blue, black)
            custom_color: Custom RGB tuple to remove (overrides color_name)

        Returns:
            Image with transparent background (BGRA format)
        """
        # Convert to RGB for processing
        if len(image.shape) == 2:  # Grayscale
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

        # Determine target color
        if custom_color:
            target_color = np.array(custom_color, dtype=np.uint8)
        elif color_name and color_name.lower() in self.bg_colors:
            target_color = np.array(self.bg_colors[color_name.lower()], dtype=np.uint8)
        else:
            # Auto-detect dominant background color
            target_color = self._detect_background_color(image)

        # Convert BGR to RGB for consistency
        target_color_bgr = target_color[::-1] if len(target_color) == 3 else target_color

        # Create mask for the background color
        lower_bound = np.clip(target_color_bgr - self.tolerance, 0, 255)
        upper_bound = np.clip(target_color_bgr + self.tolerance, 0, 255)

        mask = cv2.inRange(image, lower_bound, upper_bound)

        # Invert mask (we want to keep the foreground, not background)
        mask_inv = cv2.bitwise_not(mask)

        # Create BGRA image with transparency
        bgra = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        bgra[:, :, 3] = mask_inv

        return bgra

    def _detect_background_color(self, image):
        """Detect the dominant background color by sampling edges.

        Args:
            image: numpy array of the image (BGR format)

        Returns:
            Detected background color as numpy array (BGR)
        """
        height, width = image.shape[:2]

        # Sample pixels from edges (likely to be background)
        edge_samples = []

        # Top edge
        edge_samples.extend(image[0, :].tolist())
        # Bottom edge
        edge_samples.extend(image[height-1, :].tolist())
        # Left edge
        edge_samples.extend(image[:, 0].tolist())
        # Right edge
        edge_samples.extend(image[:, width-1].tolist())

        # Calculate median color (more robust than mean)
        edge_samples = np.array(edge_samples)
        median_color = np.median(edge_samples, axis=0).astype(np.uint8)

        return median_color

    def refine_edges(self, image_bgra):
        """Refine edges to remove color fringing and improve quality.

        Args:
            image_bgra: Image with alpha channel (BGRA format)

        Returns:
            Image with refined edges
        """
        # Apply slight blur to alpha channel to smooth edges
        alpha = image_bgra[:, :, 3]
        alpha_blurred = cv2.GaussianBlur(alpha, (3, 3), 0)

        # Threshold to maintain crisp edges
        _, alpha_thresholded = cv2.threshold(alpha_blurred, 128, 255, cv2.THRESH_BINARY)

        image_bgra[:, :, 3] = alpha_thresholded

        return image_bgra

    def remove_with_ai(self, image, method="rembg"):
        """Remove background using AI-based method.

        This is more accurate but slower than color-based removal.

        Args:
            image: numpy array of the image (BGR format)
            method: AI method to use - "rembg" or "rmbg" (BRIA RMBG-2.0)

        Returns:
            Image with transparent background (BGRA format)
        """
        if method == "rmbg":
            # Use BRIA RMBG-2.0 model
            try:
                from rmbg_remover import RMBGRemover
                remover = RMBGRemover()
                return remover.remove_background(image)
            except ImportError as e:
                print(f"Warning: RMBG-2.0 dependencies not installed: {e}")
                print("Falling back to rembg...")
                method = "rembg"

        # Use rembg (default)
        try:
            from rembg import remove
            from PIL import Image as PILImage

            # Convert cv2 image to PIL
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = PILImage.fromarray(rgb_image)

            # Remove background
            output = remove(pil_image)

            # Convert back to cv2 format
            result = np.array(output)
            bgra = cv2.cvtColor(result, cv2.COLOR_RGBA2BGRA)

            return bgra
        except ImportError:
            print("Warning: rembg not installed. Using color-based removal instead.")
            return self.remove_color_background(image)
