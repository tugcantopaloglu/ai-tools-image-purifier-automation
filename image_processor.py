"""Main image processing module."""

import cv2
import os
from pathlib import Path
from watermark_remover import WatermarkRemover
from background_remover import BackgroundRemover


class ImageProcessor:
    """Main class for processing images with watermark and background removal."""

    def __init__(self):
        self.watermark_remover = WatermarkRemover()
        self.background_remover = BackgroundRemover()

    def process_image(self, input_path, output_path, remove_watermark=True,
                     remove_background=False, bg_color=None, aggressive=False):
        """Process a single image.

        Args:
            input_path: Path to input image
            output_path: Path to save processed image
            remove_watermark: Whether to remove watermarks
            remove_background: Whether to remove background
            bg_color: Background color to remove (None for auto-detect)
            aggressive: Use aggressive watermark removal (crops bottom)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Read image
            image = cv2.imread(str(input_path))
            if image is None:
                print(f"Error: Could not read image {input_path}")
                return False

            original_shape = image.shape
            print(f"Processing: {Path(input_path).name} ({original_shape[1]}x{original_shape[0]})")

            # Remove watermark
            if remove_watermark:
                print("  - Removing watermark...")
                image = self.watermark_remover.smart_remove(image, aggressive=aggressive)

            # Remove background
            if remove_background:
                print(f"  - Removing background (color: {bg_color or 'auto-detect'})...")
                image = self.background_remover.remove_color_background(image, color_name=bg_color)
                image = self.background_remover.refine_edges(image)

            # Save image
            cv2.imwrite(str(output_path), image)
            print(f"  ✓ Saved to: {output_path}")

            return True

        except Exception as e:
            print(f"Error processing {input_path}: {str(e)}")
            return False

    def process_directory(self, input_dir, output_dir=None, remove_watermark=True,
                         remove_background=False, bg_color=None, aggressive=False,
                         recursive=False):
        """Process all images in a directory.

        Args:
            input_dir: Input directory path
            output_dir: Output directory path (default: input_dir/output)
            remove_watermark: Whether to remove watermarks
            remove_background: Whether to remove background
            bg_color: Background color to remove
            aggressive: Use aggressive watermark removal
            recursive: Process subdirectories recursively

        Returns:
            Tuple of (successful_count, failed_count)
        """
        input_path = Path(input_dir)

        if not input_path.exists():
            print(f"Error: Input directory {input_dir} does not exist")
            return 0, 0

        # Set up output directory
        if output_dir is None:
            output_path = input_path / "output"
        else:
            output_path = Path(output_dir)

        output_path.mkdir(parents=True, exist_ok=True)

        # Supported image formats
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}

        # Find all images
        if recursive:
            image_files = [f for f in input_path.rglob('*') if f.suffix.lower() in image_extensions]
        else:
            image_files = [f for f in input_path.glob('*') if f.suffix.lower() in image_extensions]

        if not image_files:
            print(f"No images found in {input_dir}")
            return 0, 0

        print(f"\nFound {len(image_files)} image(s) to process\n")

        successful = 0
        failed = 0

        for image_file in image_files:
            # Determine output path, preserving directory structure if recursive
            if recursive:
                rel_path = image_file.relative_to(input_path)
                output_file = output_path / rel_path
                output_file.parent.mkdir(parents=True, exist_ok=True)
            else:
                output_file = output_path / image_file.name

            # Change extension to PNG if removing background (for transparency)
            if remove_background and output_file.suffix.lower() != '.png':
                output_file = output_file.with_suffix('.png')

            success = self.process_image(
                image_file, output_file,
                remove_watermark=remove_watermark,
                remove_background=remove_background,
                bg_color=bg_color,
                aggressive=aggressive
            )

            if success:
                successful += 1
            else:
                failed += 1

            print()  # Blank line between files

        return successful, failed
