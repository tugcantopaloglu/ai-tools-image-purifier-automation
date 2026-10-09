# AI Tools Image Purifier

A local Python CLI for detecting text-like regions near the bottom of images, applying inpainting, and removing solid color backgrounds. Optional AI background removal uses rembg or BRIA RMBG-2.0.

Watermark detection is a position and shape heuristic. It does not identify a provider's logo or verify watermark removal quality. Review outputs before relying on them, and process images you have permission to modify.

## Installation

Use Python 3.10 or newer and a virtual environment:

```bash
git clone https://github.com/tugcantopaloglu/ai-tools-image-purifier-automation.git
cd ai-tools-image-purifier-automation
python -m venv .venv
```

Activate `.venv` with `.venv\Scripts\activate` on Windows or `source .venv/bin/activate` on Linux/macOS. For the local color and watermark pipeline:

```bash
python -m pip install -r requirements-core.txt
```

To also install the optional AI dependencies:

```bash
python -m pip install -r requirements.txt
```

The full requirements include rembg, PyTorch, torchvision and transformers. These can take substantial disk space and have platform-specific requirements. The color pipeline does not need them.

## Usage

```bash
python main.py input_folder -w
python main.py input_folder -w -b white
python main.py input_folder -b green
python main.py input_folder -b auto
python main.py input_folder -w -b white -r
python main.py image.png -w -o cleaned.png
python main.py image.jpg -b white -o transparent.png
```

At least one of `-w/--watermark` or `-b/--background` is required. Supported background colors are `white`, `green`, `blue`, `black` and `auto`. `--aggressive` also crops the bottom 12 percent of the image.

A file input defaults to an `output` subdirectory beside that file. A directory input defaults to `input_folder/output`. `-o/--output` selects a file for a single input or a directory for a batch. Background removal uses a `.png` output to retain transparency.

Recursive processing preserves relative subdirectories and excludes the selected output tree, including outputs from earlier runs. Input files are retained; an output resolving to the source file is rejected. Batch output cannot be the input directory or its ancestor. If multiple inputs such as `photo.jpg` and `photo.png` would become the same `photo.png`, those inputs fail rather than overwrite each other. Existing files in a separate output directory can be replaced on a rerun.

## Optional AI background removal

```bash
python main.py image.png -b white --use-ai
python main.py image.png -b white --use-ai --ai-model rmbg
```

With `--use-ai`, the background color selects the operation but is not used as a color mask. AI models may download weights on first use; they can run offline only after the required files are cached. Hardware, memory and processing time depend on the chosen model and device.

RMBG-2.0 requires access to [the Hugging Face model repository](https://huggingface.co/briaai/RMBG-2.0). Review the model's current license and access terms. Set `HF_TOKEN` or `HUGGING_FACE_HUB_TOKEN` in your environment, or copy [.env.example](.env.example) to `.env` and set the token there. Keep `.env` out of version control.

The RMBG loader enables `trust_remote_code=True` and does not pin a model revision. It can execute model repository code when loading. Review and trust that repository before choosing this option. Offline fixture tests do not load either AI model or validate authentication. `setup_hf_token.py` is interactive and its existing dependency check does not verify model access.

If RMBG dependencies are unavailable, the background remover attempts rembg. If rembg is unavailable, it prints a warning and uses color detection. Other model/runtime errors fail processing. Check the console to confirm which method ran.

## Local verification

```bash
python test_installation.py
python -m unittest discover -s tests -v
```

The installation check verifies imports. Regression tests use small generated images to check named and auto-detected colors, transparency, output failures, source preservation, recursive reruns, filename collisions and the CLI. CI installs only core dependencies, runs these fixtures, scans the changed local pipeline with Bandit and audits core dependencies. AI inference, model downloads and credentials are not covered by these checks.

## Limitations

- Inpainting can alter foreground details and is not guaranteed to remove a watermark.
- Aggressive mode intentionally crops image content.
- Color matching can remove foreground pixels similar to the selected background.
- Alpha edge refinement can affect small details. Existing source alpha is retained when saving to a format that supports it.
- Processing uses 8-bit samples. Decoded 16-bit color and alpha channels are scaled to 8-bit; other sample depths are rejected. Source files retain their original depth.
- AI output quality, GPU execution and provider/model compatibility need separate testing.

## Project files

- `main.py`: CLI and argument validation
- `image_processor.py`: single-file and batch orchestration
- `watermark_remover.py`: region detection, inpainting and cropping
- `background_remover.py`: color masks and optional AI dispatch
- `rmbg_remover.py`: RMBG model loading and inference
- `requirements-core.txt`: local processing dependencies
- `requirements.txt`: core and optional AI dependencies
- `tests/test_local_pipeline.py`: local regression fixtures

## License

MIT License - feel free to use and modify as needed.
