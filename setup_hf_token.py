#!/usr/bin/env python3
"""Interactive setup for Hugging Face token to use RMBG-2.0."""

import os
import sys


def main():
    print("=" * 60)
    print("RMBG-2.0 Hugging Face Token Setup")
    print("=" * 60)
    print()
    print("RMBG-2.0 requires a Hugging Face token to access the model.")
    print()
    print("Quick steps:")
    print("1. Visit: https://huggingface.co/briaai/RMBG-2.0")
    print("   - Click 'Agree and access repository'")
    print()
    print("2. Get your token: https://huggingface.co/settings/tokens")
    print("   - Click 'New token'")
    print("   - Copy the token (starts with 'hf_...')")
    print()
    print("=" * 60)
    print()

    # Check if token is already set
    existing_token = os.environ.get('HF_TOKEN') or os.environ.get('HUGGING_FACE_HUB_TOKEN')

    if existing_token:
        print(f"[INFO] Token already set: {existing_token[:10]}...")
        response = input("\nDo you want to update it? (y/n): ").strip().lower()
        if response != 'y':
            print("Keeping existing token.")
            return

    # Get token from user
    print("Paste your Hugging Face token below:")
    token = input("Token: ").strip()

    if not token:
        print("\n[ERROR] No token provided. Exiting.")
        sys.exit(1)

    if not token.startswith('hf_'):
        print("\n[WARNING] Token doesn't look right. HF tokens usually start with 'hf_'")
        response = input("Continue anyway? (y/n): ").strip().lower()
        if response != 'y':
            sys.exit(1)

    # Set environment variable for current session
    os.environ['HF_TOKEN'] = token

    print("\n" + "=" * 60)
    print("[SUCCESS] Token set for this session!")
    print("=" * 60)
    print()

    # Provide instructions for permanent setup
    print("To make this permanent, add to your environment:")
    print()
    print("Windows (Command Prompt):")
    print(f'  setx HF_TOKEN "{token}"')
    print()
    print("Windows (PowerShell):")
    print(f'  [System.Environment]::SetEnvironmentVariable("HF_TOKEN", "{token}", "User")')
    print()
    print("Linux/Mac (.bashrc or .zshrc):")
    print(f'  export HF_TOKEN="{token}"')
    print()
    print("=" * 60)
    print()

    # Test the token
    response = input("Do you want to test the token now? (y/n): ").strip().lower()

    if response == 'y':
        print("\nTesting token by loading model...")
        try:
            from rmbg_remover import RMBGRemover
            print("Creating RMBG remover instance...")
            remover = RMBGRemover()
            print("[SUCCESS] Token works! RMBG-2.0 is ready to use.")
            print()
            print("Try it:")
            print("  python main.py images -w --use-ai --ai-model rmbg")
        except Exception as e:
            print(f"\n[ERROR] Token test failed: {e}")
            print("\nPlease check:")
            print("1. You clicked 'Agree and access' at https://huggingface.co/briaai/RMBG-2.0")
            print("2. Your token is valid at https://huggingface.co/settings/tokens")
            print("3. Dependencies are installed: pip install torch torchvision transformers")
    else:
        print("\nToken is set. You can now use:")
        print("  python main.py images -w --use-ai --ai-model rmbg")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Setup cancelled by user.")
        sys.exit(1)
