# AI Tools Image Purifier

An automated tool to remove watermarks from AI-generated images (Gemini, Sora, DALL-E, Midjourney, etc.) and optionally remove solid color backgrounds while preserving the main image content.

## Features

- **Watermark Removal**: Intelligently detects and removes watermarks from popular AI tools
  - Google Gemini
  - OpenAI Sora
  - DALL-E
  - Midjourney
  - Stable Diffusion
  - And more...

- **Background Removal**: Remove solid color backgrounds
  - Predefined colors: white, green, blue, black
  - Auto-detection of background color
  - Preserves image quality and details

- **Batch Processing**: Process entire directories of images
- **Smart Detection**: Uses edge detection and inpainting to preserve image quality
- **Flexible Options**: CLI interface with multiple processing modes

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-tools-image-purifier-automation.git
cd ai-tools-image-purifier-automation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Commands

Remove watermarks from all images in a folder:
```bash
python main.py input_folder -w
```

Remove watermarks and white background:
```bash
python main.py input_folder -w -b white
```

Process a single image:
```bash
python main.py image.png -w -o output.png
```

Remove green screen background only:
```bash
python main.py input_folder -b green
```

Auto-detect and remove background:
```bash
python main.py input_folder -b auto
```

Aggressive watermark removal (also crops bottom region):
```bash
python main.py input_folder -w --aggressive
```

Process recursively through subdirectories:
```bash
python main.py input_folder -w -b white -r
```

### Command-Line Options

```
positional arguments:
  input                 Input image file or directory

optional arguments:
  -h, --help            Show help message
  -o, --output OUTPUT   Output file or directory (default: creates 'output' folder)
  -w, --watermark       Remove AI tool watermarks
  -b, --background COLOR
                        Remove solid color background (white/green/blue/black/auto)
  --aggressive          Use aggressive watermark removal (crops bottom region)
  -r, --recursive       Process subdirectories recursively
```

## How It Works

### Watermark Removal

The tool uses two approaches:

1. **Smart Detection**:
   - Scans common watermark locations (bottom corners and center)
   - Uses edge detection to identify text-like regions
   - Applies OpenCV inpainting to seamlessly remove detected watermarks

2. **Aggressive Mode** (optional):
   - Additionally crops the bottom 12-15% of the image where watermarks typically appear
   - Useful when detection misses subtle watermarks

### Background Removal

Two methods available:

1. **Color-based Removal**:
   - Identifies and removes pixels matching the specified color within a tolerance
   - Fast and efficient for solid color backgrounds
   - Edge refinement to prevent color fringing

2. **Auto-detection**:
   - Samples edge pixels to determine dominant background color
   - Automatically removes detected background

## Project Structure

```
ai-tools-image-purifier-automation/
├── main.py                  # CLI entry point
├── image_processor.py       # Main processing orchestrator
├── watermark_remover.py     # Watermark detection and removal
├── background_remover.py    # Background removal functionality
├── config.py                # Configuration and constants
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Examples

### Before and After

Input: Image with Gemini watermark in bottom-right corner
```bash
python main.py gemini_image.png -w -o clean_image.png
```

Input: AI-generated image with white background
```bash
python main.py ai_art.png -w -b white -o transparent_art.png
```

Input: Batch of images in folder
```bash
python main.py ./my_images -w -b auto
# Output will be in ./my_images/output/
```

## Requirements

- Python 3.7+
- OpenCV (cv2)
- NumPy
- Pillow
- rembg (optional, for AI-based background removal)

## Tips for Best Results

1. **Watermark Removal**:
   - Use standard mode first; try aggressive mode if watermarks remain
   - Works best with watermarks in bottom 15% of image
   - May not work well with watermarks overlapping main content

2. **Background Removal**:
   - Use specific color names when you know the background color
   - Use 'auto' for mixed or unknown background colors
   - Output will be PNG with transparency

3. **Batch Processing**:
   - Organize images in folders for easier batch processing
   - Use recursive mode (-r) for nested folder structures
   - Check the output folder after processing

## Limitations

- Watermark removal works best for watermarks in typical locations (corners, bottom)
- Complex or artistic watermarks may require manual editing
- Background removal works best with solid, uniform colors
- Processing time depends on image size and number of images

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - feel free to use and modify as needed.
