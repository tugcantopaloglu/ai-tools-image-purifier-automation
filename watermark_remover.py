"""Watermark detection and removal module."""

import cv2
import numpy as np
from config import WATERMARK_CONFIGS


class WatermarkRemover:
    """Handles detection and removal of AI tool watermarks."""

    def __init__(self):
        self.configs = WATERMARK_CONFIGS

    def detect_watermark_region(self, image):
        """Detect potential watermark regions in the image.

        Args:
            image: numpy array of the image (BGR format from cv2)

        Returns:
            List of bounding boxes (x, y, w, h) of detected watermark regions
        """
        height, width = image.shape[:2]
        detected_regions = []

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Check common watermark locations
        regions_to_check = [
            ("bottom_right", (int(width * 0.7), int(height * 0.85), width, height)),
            ("bottom_left", (0, int(height * 0.85), int(width * 0.3), height)),
            ("bottom", (int(width * 0.3), int(height * 0.9), int(width * 0.7), height)),
        ]

        for location, (x1, y1, x2, y2) in regions_to_check:
            roi = gray[y1:y2, x1:x2]

            # Look for text-like regions (watermarks are usually text)
            # Use edge detection to find text boundaries
            edges = cv2.Canny(roi, 50, 150)

            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                # Filter for text-like dimensions (horizontal, small height)
                if w > 20 and h > 5 and w > h * 2:
                    detected_regions.append((x1 + x, y1 + y, w, h))

        return detected_regions

    def inpaint_watermark(self, image, regions):
        """Remove watermark by inpainting detected regions.

        Args:
            image: numpy array of the image (BGR format)
            regions: List of (x, y, w, h) tuples for watermark locations

        Returns:
            Image with watermarks removed
        """
        if not regions:
            return image

        # Create mask for inpainting
        mask = np.zeros(image.shape[:2], dtype=np.uint8)

        for x, y, w, h in regions:
            # Expand region slightly to ensure complete coverage
            padding = 5
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image.shape[1] - x, w + 2 * padding)
            h = min(image.shape[0] - y, h + 2 * padding)

            mask[y:y+h, x:x+w] = 255

        # Use inpainting to remove watermark
        result = cv2.inpaint(image, mask, 3, cv2.INPAINT_TELEA)

        return result

    def remove_bottom_region(self, image, height_ratio=0.15):
        """Remove watermark by cropping bottom region of image.

        This is a simpler approach that crops the typical watermark area.

        Args:
            image: numpy array of the image
            height_ratio: Ratio of height to remove from bottom (default 0.15 = 15%)

        Returns:
            Cropped image with bottom region removed
        """
        height = image.shape[0]
        crop_height = int(height * (1 - height_ratio))
        return image[:crop_height, :]

    def smart_remove(self, image, aggressive=False):
        """Intelligently remove watermarks using detection and inpainting.

        Args:
            image: numpy array of the image (BGR format)
            aggressive: If True, also crop bottom region as fallback

        Returns:
            Image with watermarks removed
        """
        # First try to detect and inpaint specific watermark regions
        regions = self.detect_watermark_region(image)

        if regions:
            result = self.inpaint_watermark(image, regions)
        else:
            result = image.copy()

        # If aggressive mode, also crop bottom region
        if aggressive:
            result = self.remove_bottom_region(result, height_ratio=0.12)

        return result
