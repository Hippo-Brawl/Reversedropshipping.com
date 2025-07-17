#!/usr/bin/env python3
"""
Test script to verify all dependencies are installed correctly
"""

def test_imports():
    try:
        import yt_dlp
        print("✓ yt-dlp imported successfully")
        
        from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
        print("✓ moviepy imported successfully")
        
        import requests
        print("✓ requests imported successfully")
        
        from PIL import Image
        print("✓ Pillow imported successfully")
        
        import os
        from pathlib import Path
        print("✓ Standard libraries imported successfully")
        
        print("\n✅ All dependencies are installed correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_folders():
    from pathlib import Path
    
    folders = ['input', 'overlay', 'output', 'temp']
    for folder in folders:
        path = Path(folder)
        path.mkdir(exist_ok=True)
        if path.exists():
            print(f"✓ {folder}/ folder exists")
        else:
            print(f"❌ {folder}/ folder could not be created")
    
    # Check if example overlay exists
    overlay_path = Path("overlay/example_overlay.png")
    if overlay_path.exists():
        print("✓ Example overlay image found")
    else:
        print("ℹ No overlay image found - run create_example_overlay.py to create one")
    
    print("\n✅ All folders are ready!")

if __name__ == "__main__":
    print("Testing TikTok Video Processor setup...\n")
    
    if test_imports():
        test_folders()
        print("\n🎉 Setup complete! You can now run main.py")
    else:
        print("\n❌ Setup incomplete. Please install missing dependencies.")
