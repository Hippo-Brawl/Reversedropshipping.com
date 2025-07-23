# TikTok Video Processor

This script downloads TikTok videos from a profile, processes them, and creates individual video pairs with your input video.

## Features

- Downloads up to 50 videos from any TikTok profile
- Automatically cuts videos to 20 seconds maximum
- Adds custom image overlay to each TikTok video (from overlay folder)
- Creates individual video pairs: each TikTok video + your input video
- Saves each pair as a separate file in the output folder

## Setup

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Create the folder structure:
   - `input/` - Place your video file here
   - `overlay/` - Place your overlay image here (PNG, JPG, etc.)
   - `output/` - Individual video pairs will be saved here
   - `temp/` - Temporary files (created automatically)

## Usage

1. Place your video file in the `input/` folder
2. Place your overlay image in the `overlay/` folder (optional)
3. Run the script:
```bash
python main.py
```
4. Enter the TikTok profile URL when prompted
5. Enter the number of videos to download (1-50)
6. Wait for processing to complete
7. Find your individual video pairs in the `output/` folder

## Output

If you download 5 TikTok videos, you'll get 5 separate files:
- `video_pair_01.mp4` - TikTok video 1 + your input video
- `video_pair_02.mp4` - TikTok video 2 + your input video  
- `video_pair_03.mp4` - TikTok video 3 + your input video
- `video_pair_04.mp4` - TikTok video 4 + your input video
- `video_pair_05.mp4` - TikTok video 5 + your input video

## Supported Formats

- **Video formats**: MP4, AVI, MOV, MKV, WMV, FLV
- **Image formats**: PNG, JPG, JPEG, GIF, BMP

## Notes

- The script requires an active internet connection to download TikTok videos
- Processing time depends on the number of videos and their length
- Overlay images are resized automatically to fit the video
- Only TikTok videos get the overlay - your input video remains unchanged
- Make sure you have sufficient disk space for all the output files

## Troubleshooting

- If downloads fail, check if the TikTok profile URL is correct and public
- If video processing fails, ensure your input video is in a supported format
- If video processing fails when you're using a supported format, make sure that you are using the correct ratio(9:16)
- For overlay issues, make sure your overlay image is in the overlay folder
- For permission errors, make sure the script has write access to the folders
