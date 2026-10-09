"""Main image processing module."""

import cv2
import os
import numpy as np
from pathlib import Path
from watermark_remover import WatermarkRemover
from background_remover import BackgroundRemover


class ImageProcessor:
    """Main class for processing images with watermark and background removal."""

    def __init__(self):
        """Initialize image processor."""
        self.watermark_remover = WatermarkRemover()
        self.background_remover = BackgroundRemover()

    def process_image(self, input_path, output_path, remove_watermark=True,
                     remove_background=False, bg_color=None, aggressive=False,
                     use_ai=False, ai_method="rembg"):
        """Process a single image.

        Args:
            input_path: Path to input image
            output_path: Path to save processed image
            remove_watermark: Whether to remove watermarks
            remove_background: Whether to remove background
            bg_color: Background color to remove (None for auto-detect)
            aggressive: Use aggressive watermark removal (crops bottom)
            use_ai: Use AI-based background removal instead of color-based
            ai_method: AI method to use - "rembg" or "rmbg" (BRIA RMBG-2.0)

        Returns:
            True if successful, False otherwise
        """
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)
            if remove_background:
                output_path = output_path.with_suffix('.png')
            if input_path.resolve() == output_path.resolve():
                print(f"Error: Output must differ from the source image: {input_path}")
                return False
            # Read image
            image = cv2.imread(str(input_path), cv2.IMREAD_UNCHANGED)
            if image is None:
                print(f"Error: Could not read image {input_path}")
                return False

            if image.dtype == np.uint16:
                image = (image / 257).round().astype(np.uint8)
            elif image.dtype != np.uint8:
                print(f"Error: Unsupported image sample type {image.dtype}: {input_path}")
                return False

            original_alpha = None
            if image.ndim == 2:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
            elif image.shape[2] == 4:
                original_alpha = image[:, :, 3].copy()
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

            original_shape = image.shape
            print(f"Processing: {Path(input_path).name} ({original_shape[1]}x{original_shape[0]})")

            # Remove watermark
            if remove_watermark:
                print("  - Removing watermark...")
                image = self.watermark_remover.smart_remove(image, aggressive=aggressive)

            # Remove background
            if remove_background:
                if use_ai:
                    method_name = "BRIA RMBG-2.0" if ai_method == "rmbg" else "rembg"
                    print(f"  - Removing background (AI-based: {method_name})...")
                    image = self.background_remover.remove_with_ai(image, method=ai_method)
                else:
                    print(f"  - Removing background (color: {bg_color or 'auto-detect'})...")
                    image = self.background_remover.remove_color_background(image, color_name=bg_color)
                    image = self.background_remover.refine_edges(image)

            # Save image
            if original_alpha is not None:
                alpha = original_alpha[:image.shape[0], :image.shape[1]]
                if image.shape[2] == 3:
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
                    image[:, :, 3] = alpha
                else:
                    image[:, :, 3] = cv2.min(image[:, :, 3], alpha)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            if not cv2.imwrite(str(output_path), image):
                print(f"Error: Could not save image {output_path}")
                return False
            print(f"  [OK] Saved to: {output_path}")

            return True

        except Exception as e:
            print(f"Error processing {input_path}: {str(e)}")
            return False

    def process_directory(self, input_dir, output_dir=None, remove_watermark=True,
                         remove_background=False, bg_color=None, aggressive=False,
                         recursive=False, use_ai=False, ai_method="rembg"):
        """Process all images in a directory.

        Args:
            input_dir: Input directory path
            output_dir: Output directory path (default: input_dir/output)
            remove_watermark: Whether to remove watermarks
            remove_background: Whether to remove background
            bg_color: Background color to remove
            aggressive: Use aggressive watermark removal
            recursive: Process subdirectories recursively
            use_ai: Use AI-based background removal
            ai_method: AI method to use - "rembg" or "rmbg" (BRIA RMBG-2.0)

        Returns:
            Tuple of (successful_count, failed_count)
        """
        input_path = Path(input_dir).resolve()

        if not input_path.is_dir():
            print(f"Error: Input directory {input_dir} does not exist")
            return 0, 0

        # Set up output directory
        if output_dir is None:
            output_path = input_path / "output"
        else:
            output_path = Path(output_dir).resolve()

        if output_path == input_path or output_path in input_path.parents:
            print("Error: Output directory must not be the input directory or its ancestor")
            return 0, 1

        output_path.mkdir(parents=True, exist_ok=True)

        # Supported image formats
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}

        # Find all images
        if recursive:
            image_files = [f for f in input_path.rglob('*') if f.suffix.lower() in image_extensions]
        else:
            image_files = [f for f in input_path.glob('*') if f.suffix.lower() in image_extensions]

        image_files = sorted(
            f for f in image_files
            if f.is_file() and output_path not in f.resolve().parents
        )

        if not image_files:
            print(f"No images found in {input_dir}")
            return 0, 0

        print(f"\nFound {len(image_files)} image(s) to process\n")

        successful = 0
        failed = 0

        output_counts = {}
        for image_file in image_files:
            rel_path = image_file.relative_to(input_path)
            target = output_path / rel_path
            if remove_background:
                target = target.with_suffix('.png')
            key = os.path.normcase(str(target))
            output_counts[key] = output_counts.get(key, 0) + 1

        for image_file in image_files:
            # Determine output path, preserving directory structure if recursive
            if recursive:
                rel_path = image_file.relative_to(input_path)
                output_file = output_path / rel_path
                output_file.parent.mkdir(parents=True, exist_ok=True)
            else:
                output_file = output_path / image_file.name

            # Change extension to PNG if removing background (for transparency)
            if remove_background:
                output_file = output_file.with_suffix('.png')

            if output_counts[os.path.normcase(str(output_file))] > 1:
                print(f"Error: Multiple source images would overwrite {output_file}")
                failed += 1
                continue

            success = self.process_image(
                image_file, output_file,
                remove_watermark=remove_watermark,
                remove_background=remove_background,
                bg_color=bg_color,
                aggressive=aggressive,
                use_ai=use_ai,
                ai_method=ai_method
            )

            if success:
                successful += 1
            else:
                failed += 1

            print()  # Blank line between files

        return successful, failed
