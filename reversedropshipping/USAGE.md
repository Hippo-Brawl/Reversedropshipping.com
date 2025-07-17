# Example Usage

## Quick Start Guide

1. **Place your video in the input folder**
   - Copy your video file to the `input/` folder
   - Supported formats: MP4, AVI, MOV, MKV, WMV, FLV

2. **Add your overlay image (optional)**
   - Copy your overlay image to the `overlay/` folder
   - Supported formats: PNG, JPG, JPEG, GIF, BMP
   - An example overlay is created automatically when you run the script

3. **Run the script**
   ```bash
   python main.py
   ```

4. **Follow the prompts**
   - Enter TikTok profile URL (e.g., https://www.tiktok.com/@username)
   - Enter number of videos to download (1-50)

5. **Wait for processing**
   - The script will download, process, and create video pairs
   - Progress will be shown in the terminal

6. **Get your results**
   - Individual video pairs will be saved in the `output/` folder
   - Each file contains: TikTok video (with overlay) + your input video

## Example Output

If you download 3 TikTok videos, you'll get:
```
output/
├── video_pair_01.mp4
├── video_pair_02.mp4
└── video_pair_03.mp4
```

Each file structure:
- **TikTok video 1** (with overlay) → **Your input video**
- **TikTok video 2** (with overlay) → **Your input video**
- **TikTok video 3** (with overlay) → **Your input video**

## Example TikTok URLs

- User profile: `https://www.tiktok.com/@username`
- Alternative format: `https://www.tiktok.com/user/username`
- Mobile link: `https://vm.tiktok.com/xxx`

## What the script does:

1. **Downloads** TikTok videos from the specified profile
2. **Processes** each TikTok video:
   - Cuts to maximum 20 seconds
   - Adds your custom overlay image (if provided)
3. **Creates pairs**: Each TikTok video + your input video
4. **Saves** each pair as a separate file

## Tips:

- Use PNG overlay images for transparency
- Make overlay images reasonably sized (they'll be auto-resized)
- Use public TikTok profiles for best results
- Ensure stable internet connection for downloads
- Each video pair will be roughly: TikTok duration + your input video duration
