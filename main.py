#!/usr/bin/env python3
"""AI Tools Image Purifier - Remove watermarks and backgrounds from images."""

import argparse
import sys
from pathlib import Path
from image_processor import ImageProcessor


def main():
    parser = argparse.ArgumentParser(
        description="Remove AI tool watermarks and backgrounds from images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Remove watermarks from all images in a directory
  python main.py input_folder -w

  # Remove watermarks and white background
  python main.py input_folder -w -b white

  # Remove watermarks with aggressive mode (crops bottom)
  python main.py input_folder -w --aggressive

  # Process single image
  python main.py image.png -w -o output.png

  # Remove green screen background only
  python main.py input_folder -b green

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
            aggressive=args.aggressive
        )

        if success:
            print(f"\n✓ Successfully processed image")
        else:
            print(f"\n✗ Failed to process image")
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
            recursive=args.recursive
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
