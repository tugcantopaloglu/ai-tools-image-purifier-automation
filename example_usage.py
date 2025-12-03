#!/usr/bin/env python3
"""Example usage of the Image Processor API."""

from image_processor import ImageProcessor
from pathlib import Path


def example_1_remove_watermark():
    """Example 1: Remove watermark from a single image."""
    print("Example 1: Remove watermark from single image")
    print("-" * 50)

    processor = ImageProcessor()

    processor.process_image(
        input_path="sample_images/gemini_image.png",
        output_path="output/clean_image.png",
        remove_watermark=True,
        remove_background=False
    )

    print("\n")


def example_2_remove_background():
    """Example 2: Remove white background from an image."""
    print("Example 2: Remove white background")
    print("-" * 50)

    processor = ImageProcessor()

    processor.process_image(
        input_path="sample_images/white_bg_image.png",
        output_path="output/transparent_image.png",
        remove_watermark=False,
        remove_background=True,
        bg_color="white"
    )

    print("\n")


def example_3_both_operations():
    """Example 3: Remove both watermark and background."""
    print("Example 3: Remove watermark and green background")
    print("-" * 50)

    processor = ImageProcessor()

    processor.process_image(
        input_path="sample_images/ai_image_greenscreen.png",
        output_path="output/clean_transparent.png",
        remove_watermark=True,
        remove_background=True,
        bg_color="green"
    )

    print("\n")


def example_4_batch_processing():
    """Example 4: Process entire directory."""
    print("Example 4: Batch process directory")
    print("-" * 50)

    processor = ImageProcessor()

    successful, failed = processor.process_directory(
        input_dir="sample_images",
        output_dir="output/batch",
        remove_watermark=True,
        remove_background=True,
        bg_color=None,  # Auto-detect
        aggressive=False,
        recursive=False
    )

    print(f"Processed: {successful} successful, {failed} failed")
    print("\n")


def example_5_aggressive_mode():
    """Example 5: Aggressive watermark removal."""
    print("Example 5: Aggressive watermark removal")
    print("-" * 50)

    processor = ImageProcessor()

    processor.process_image(
        input_path="sample_images/stubborn_watermark.png",
        output_path="output/aggressively_cleaned.png",
        remove_watermark=True,
        remove_background=False,
        aggressive=True
    )

    print("\n")


if __name__ == "__main__":
    print("=" * 50)
    print("Image Processor Examples")
    print("=" * 50)
    print("\n")

    # Create output directory
    Path("output").mkdir(exist_ok=True)

    # Run examples (comment out those you don't want to run)
    try:
        example_1_remove_watermark()
    except Exception as e:
        print(f"Example 1 failed: {e}\n")

    try:
        example_2_remove_background()
    except Exception as e:
        print(f"Example 2 failed: {e}\n")

    try:
        example_3_both_operations()
    except Exception as e:
        print(f"Example 3 failed: {e}\n")

    try:
        example_4_batch_processing()
    except Exception as e:
        print(f"Example 4 failed: {e}\n")

    try:
        example_5_aggressive_mode()
    except Exception as e:
        print(f"Example 5 failed: {e}\n")

    print("=" * 50)
    print("Examples complete!")
    print("=" * 50)
