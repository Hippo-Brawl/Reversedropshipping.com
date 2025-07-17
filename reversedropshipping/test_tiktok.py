#!/usr/bin/env python3
"""
Test script to verify TikTok video downloading functionality
"""

import yt_dlp
import json
from pathlib import Path

def test_tiktok_extraction(profile_url, max_videos=5):
    """Test TikTok video extraction without downloading"""
    print(f"Testing TikTok extraction for: {profile_url}")
    print(f"Looking for {max_videos} videos...")
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'playlistend': max_videos,
        'playlistreverse': False,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(profile_url, download=False)
            
            if 'entries' in info:
                entries = [entry for entry in info['entries'] if entry is not None][:max_videos]
                
                print(f"Found {len(entries)} videos:")
                for i, entry in enumerate(entries):
                    title = entry.get('title', 'Unknown')
                    upload_date = entry.get('upload_date', 'Unknown')
                    duration = entry.get('duration', 'Unknown')
                    url = entry.get('webpage_url', 'Unknown')
                    
                    print(f"  {i+1}. {title}")
                    print(f"     Upload date: {upload_date}")
                    print(f"     Duration: {duration}s")
                    print(f"     URL: {url}")
                    print()
                
                return len(entries) > 0
            else:
                print("No videos found in the profile")
                return False
                
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("=== TikTok Video Extraction Test ===")
    
    # Test URL - you can change this to test different profiles
    test_url = input("Enter TikTok profile URL to test: ").strip()
    
    if not test_url:
        print("No URL provided")
        return
    
    max_videos = 5  # Test with just 5 videos
    
    success = test_tiktok_extraction(test_url, max_videos)
    
    if success:
        print("✅ TikTok extraction test passed!")
        print("The script should be able to download videos from this profile.")
    else:
        print("❌ TikTok extraction test failed!")
        print("There might be an issue with the profile URL or TikTok access.")

if __name__ == "__main__":
    main()
