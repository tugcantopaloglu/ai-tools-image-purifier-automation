#!/usr/bin/env python3
"""Test script to verify installation and imports."""

import sys


def test_imports():
    """Test if all required packages can be imported."""
    print("Testing imports...")
    errors = []

    # Test OpenCV
    try:
        import cv2
        print(f"✓ OpenCV version: {cv2.__version__}")
    except ImportError as e:
        errors.append(f"✗ OpenCV (cv2) not found: {e}")

    # Test NumPy
    try:
        import numpy as np
        print(f"✓ NumPy version: {np.__version__}")
    except ImportError as e:
        errors.append(f"✗ NumPy not found: {e}")

    # Test Pillow
    try:
        from PIL import Image
        import PIL
        print(f"✓ Pillow version: {PIL.__version__}")
    except ImportError as e:
        errors.append(f"✗ Pillow not found: {e}")

    # Test rembg (optional)
    try:
        import rembg
        print(f"✓ rembg installed (optional)")
    except ImportError:
        print("⚠ rembg not installed (optional - for AI-based background removal)")

    return errors


def test_modules():
    """Test if project modules can be imported."""
    print("\nTesting project modules...")
    errors = []

    try:
        from config import WATERMARK_CONFIGS
        print("✓ config.py")
    except Exception as e:
        errors.append(f"✗ config.py: {e}")

    try:
        from watermark_remover import WatermarkRemover
        print("✓ watermark_remover.py")
    except Exception as e:
        errors.append(f"✗ watermark_remover.py: {e}")

    try:
        from background_remover import BackgroundRemover
        print("✓ background_remover.py")
    except Exception as e:
        errors.append(f"✗ background_remover.py: {e}")

    try:
        from image_processor import ImageProcessor
        print("✓ image_processor.py")
    except Exception as e:
        errors.append(f"✗ image_processor.py: {e}")

    return errors


def main():
    """Run all tests."""
    print("=" * 60)
    print("AI Tools Image Purifier - Installation Test")
    print("=" * 60)
    print()

    # Test imports
    import_errors = test_imports()

    # Test modules
    module_errors = test_modules()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    all_errors = import_errors + module_errors

    if not all_errors:
        print("✓ All tests passed! Installation successful.")
        print("\nYou can now use the tool:")
        print("  python main.py --help")
        return 0
    else:
        print("✗ Some tests failed:\n")
        for error in all_errors:
            print(f"  {error}")
        print("\nPlease install missing dependencies:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
