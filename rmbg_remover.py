"""BRIA RMBG-2.0 background removal using Hugging Face transformers."""

import cv2
import numpy as np
from PIL import Image
import torch
from torchvision import transforms


class RMBGRemover:
    """Handles background removal using BRIA RMBG-2.0 model."""

    def __init__(self):
        """Initialize RMBG-2.0 background remover."""
        self.model = None
        self.device = None
        self.transform = None

    def _load_model(self):
        """Load RMBG-2.0 model from Hugging Face (lazy loading)."""
        if self.model is not None:
            return

        try:
            from transformers import AutoModelForImageSegmentation
            import os

            print("  - Loading RMBG-2.0 model (first run may take a few minutes)...")

            # Determine device
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            print(f"  - Using device: {self.device}")

            # Get Hugging Face token from environment
            hf_token = os.environ.get('HF_TOKEN') or os.environ.get('HUGGING_FACE_HUB_TOKEN')

            # Load model
            self.model = AutoModelForImageSegmentation.from_pretrained(
                'briaai/RMBG-2.0',
                trust_remote_code=True,
                token=hf_token
            ).eval().to(self.device)

            # Define preprocessing transform
            self.transform = transforms.Compose([
                transforms.Resize((1024, 1024)),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225]
                )
            ])

            print("  - Model loaded successfully!")

        except Exception as e:
            error_msg = str(e)
            if "gated repo" in error_msg or "access" in error_msg.lower():
                raise Exception(
                    f"Failed to load RMBG-2.0 model: {error_msg}\n\n"
                    "RMBG-2.0 requires Hugging Face authentication:\n"
                    "1. Create account at https://huggingface.co/join\n"
                    "2. Request access at https://huggingface.co/briaai/RMBG-2.0\n"
                    "3. Get your token at https://huggingface.co/settings/tokens\n"
                    "4. Set environment variable: set HF_TOKEN=your_token_here\n"
                    "   Or login via CLI: huggingface-cli login\n\n"
                    "Alternatively, use rembg (--use-ai without --ai-model rmbg)"
                )
            else:
                raise Exception(
                    f"Failed to load RMBG-2.0 model: {error_msg}\n"
                    "Make sure you have installed: pip install torch torchvision transformers"
                )

    def remove_background(self, image):
        """Remove background using RMBG-2.0 model.

        Args:
            image: numpy array of the image (BGR format from cv2)

        Returns:
            Image with transparent background (BGRA format)
        """
        # Load model if not already loaded
        self._load_model()

        # Convert BGR to RGB
        if len(image.shape) == 2:  # Grayscale
            image_rgb = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        else:
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convert to PIL Image
        pil_image = Image.fromarray(image_rgb)
        original_size = pil_image.size

        # Preprocess image
        input_tensor = self.transform(pil_image).unsqueeze(0).to(self.device)

        # Run inference
        with torch.no_grad():
            output = self.model(input_tensor)

            # Handle different output formats
            if isinstance(output, (list, tuple)):
                # If output is a list/tuple, take the first element
                output = output[0]

            # Apply sigmoid to get probabilities
            if len(output.shape) == 4:
                # Shape: [batch, channels, height, width]
                mask = torch.sigmoid(output[0, 0]).cpu().numpy()
            else:
                # Squeeze extra dimensions if needed
                mask = torch.sigmoid(output.squeeze()).cpu().numpy()

        # Resize mask back to original size
        mask_pil = Image.fromarray((mask * 255).astype(np.uint8))
        mask_pil = mask_pil.resize(original_size, Image.LANCZOS)
        mask_resized = np.array(mask_pil)

        # Create BGRA image with alpha channel
        bgra = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)
        bgra[:, :, 3] = mask_resized

        return bgra

    def remove_background_pil(self, pil_image):
        """Remove background from PIL Image.

        Args:
            pil_image: PIL Image object

        Returns:
            PIL Image with transparent background
        """
        # Convert PIL to cv2
        image_rgb = np.array(pil_image)
        image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

        # Remove background
        result_bgra = self.remove_background(image_bgr)

        # Convert back to PIL
        result_rgb = cv2.cvtColor(result_bgra, cv2.COLOR_BGRA2RGBA)
        return Image.fromarray(result_rgb)

    def batch_remove_background(self, images):
        """Remove background from multiple images (batch processing).

        Args:
            images: List of numpy arrays (BGR format)

        Returns:
            List of images with transparent backgrounds (BGRA format)
        """
        results = []
        for img in images:
            result = self.remove_background(img)
            results.append(result)
        return results

    def is_available(self):
        """Check if RMBG-2.0 dependencies are available.

        Returns:
            bool: True if all dependencies are available
        """
        try:
            import torch
            import torchvision
            from transformers import AutoModelForImageSegmentation
            return True
        except ImportError:
            return False
