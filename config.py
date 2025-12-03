"""Configuration for watermark patterns and detection."""

# Known AI tool watermark patterns (typically appear in specific locations)
WATERMARK_CONFIGS = {
    "gemini": {
        "typical_location": "bottom_right",
        "text_patterns": ["gemini", "google gemini"],
        "height_ratio": 0.15,  # Watermark typically in bottom 15% of image
    },
    "sora": {
        "typical_location": "bottom_left",
        "text_patterns": ["sora", "openai sora"],
        "height_ratio": 0.15,
    },
    "midjourney": {
        "typical_location": "bottom",
        "text_patterns": ["midjourney"],
        "height_ratio": 0.1,
    },
    "dalle": {
        "typical_location": "bottom_right",
        "text_patterns": ["dall·e", "dall-e", "dalle"],
        "height_ratio": 0.15,
    },
    "stable_diffusion": {
        "typical_location": "bottom",
        "text_patterns": ["stable diffusion", "stability.ai"],
        "height_ratio": 0.1,
    },
}

# Background removal color thresholds
BACKGROUND_COLORS = {
    "white": (255, 255, 255),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "black": (0, 0, 0),
}

# Color tolerance for background removal
COLOR_TOLERANCE = 30
