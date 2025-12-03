#!/usr/bin/env python3
"""AI Tools Image Purifier - Remove watermarks and backgrounds from images."""

import argparse
import sys
from pathlib import Path
from image_processor import ImageProcessor

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if it exists
except ImportError:
    pass  # python-dotenv not installed, use system env vars only


def main():
    parser = argparse.ArgumentParser(
        description="Remove AI tool watermarks and backgrounds from images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Remove watermarks from all images in a directory
  python main.py input_folder -w

  # Remove watermarks and white background (color-based, fast)
  python main.py input_folder -w -b white

  # Remove background using AI (rembg - free, slower, good quality)
  python main.py input_folder -b white --use-ai

  # Remove background using RMBG-2.0 (state-of-the-art, best quality)
  python main.py input_folder -b white --use-ai --ai-model rmbg

  # Remove watermarks with aggressive mode (crops bottom)
  python main.py input_folder -w --aggressive

  # Process single image
  python main.py image.png -w -o output.png

  # Auto-detect and remove background
  python main.py input_folder -b auto

  # Process recursively through subdirectories
  python main.py input_folder -w -b white -r
        """
    )

    parser.add_argument(
        "input",
        help="Input image file or directory"
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file or directory (default: creates 'output' folder)"
    )

    parser.add_argument(
        "-w", "--watermark",
        action="store_true",
        help="Remove AI tool watermarks (Gemini, Sora, DALL-E, etc.)"
    )

    parser.add_argument(
        "-b", "--background",
        metavar="COLOR",
        help="Remove solid color background. Options: white, green, blue, black, auto"
    )

    parser.add_argument(
        "--aggressive",
        action="store_true",
        help="Use aggressive watermark removal (also crops bottom region)"
    )

    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Process subdirectories recursively"
    )

    parser.add_argument(
        "--use-ai",
        action="store_true",
        help="Use AI-based background removal instead of color-based"
    )

    parser.add_argument(
        "--ai-model",
        choices=["rembg", "rmbg"],
        default="rembg",
        help="AI model to use: rembg (default, U2-Net) or rmbg (BRIA RMBG-2.0, state-of-the-art)"
    )

    args = parser.parse_args()

    # Validate input
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input path '{args.input}' does not exist")
        sys.exit(1)

    # Check if at least one operation is specified
    if not args.watermark and not args.background:
        print("Error: Please specify at least one operation:")
        print("  -w/--watermark: Remove watermarks")
        print("  -b/--background: Remove background")
        print("\nUse -h for help")
        sys.exit(1)

    # Validate background color
    valid_bg_colors = {'white', 'green', 'blue', 'black', 'auto'}
    if args.background and args.background.lower() not in valid_bg_colors:
        print(f"Error: Invalid background color '{args.background}'")
        print(f"Valid options: {', '.join(valid_bg_colors)}")
        sys.exit(1)

    bg_color = args.background.lower() if args.background else None
    if bg_color == 'auto':
        bg_color = None  # Auto-detect

    # Create processor
    processor = ImageProcessor()

    print("=" * 60)
    print("AI Tools Image Purifier")
    print("=" * 60)
    print(f"Input: {input_path}")
    print(f"Remove watermarks: {args.watermark}")
    print(f"Remove background: {args.background or 'No'}")
    if args.use_ai and args.background:
        model_name = "BRIA RMBG-2.0" if args.ai_model == "rmbg" else "rembg (U2-Net)"
        print(f"Background method: AI-based ({model_name})")
    elif args.background:
        print("Background method: Color-based")
    if args.aggressive:
        print("Mode: Aggressive (with bottom crop)")
    print("=" * 60)
    print()

    # Process single file or directory
    if input_path.is_file():
        # Single file processing
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = input_path.parent / "output" / input_path.name

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Change extension to PNG if removing background
        if args.background and output_path.suffix.lower() != '.png':
            output_path = output_path.with_suffix('.png')

        success = processor.process_image(
            input_path,
            output_path,
            remove_watermark=args.watermark,
            remove_background=bool(args.background),
            bg_color=bg_color,
            aggressive=args.aggressive,
            use_ai=args.use_ai,
            ai_method=args.ai_model
        )

        if success:
            print(f"\n[SUCCESS] Image processed successfully")
        else:
            print(f"\n[FAILED] Failed to process image")
            sys.exit(1)

    else:
        # Directory processing
        output_dir = args.output if args.output else None

        successful, failed = processor.process_directory(
            input_path,
            output_dir=output_dir,
            remove_watermark=args.watermark,
            remove_background=bool(args.background),
            bg_color=bg_color,
            aggressive=args.aggressive,
            recursive=args.recursive,
            use_ai=args.use_ai,
            ai_method=args.ai_model
        )

        print("=" * 60)
        print(f"Processing complete!")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print("=" * 60)

        if failed > 0:
            sys.exit(1)


if __name__ == "__main__":
    main()
