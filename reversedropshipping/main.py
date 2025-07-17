import os
import sys
from pathlib import Path
import yt_dlp
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
import shutil
import json
import re
from urllib.parse import urlparse

class TikTokVideoProcessor:
    def __init__(self):
        self.input_folder = Path("input")
        self.output_folder = Path("output")
        self.temp_folder = Path("temp")
        self.overlay_folder = Path("overlay")
        
        # Create folders if they don't exist
        self.input_folder.mkdir(exist_ok=True)
        self.output_folder.mkdir(exist_ok=True)
        self.temp_folder.mkdir(exist_ok=True)
        self.overlay_folder.mkdir(exist_ok=True)
        
    def get_overlay_image(self):
        """Get the overlay image from the overlay folder"""
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        
        for ext in image_extensions:
            for image_file in self.overlay_folder.glob(f"*{ext}"):
                return image_file
        
        return None
    
    def extract_username_from_url(self, url):
        """Extract username from TikTok profile URL"""
        # Handle various TikTok URL formats
        patterns = [
            r'tiktok\.com/@([^/?]+)',
            r'tiktok\.com/user/([^/?]+)',
            r'vm\.tiktok\.com/([^/?]+)',
            r'tiktok\.com/([^/@?]+)/?$'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        raise ValueError("Invalid TikTok URL format")
    
    def clear_temp_folder(self):
        """Clear temporary folder before starting"""
        print("Clearing temporary folder...")
        try:
            if self.temp_folder.exists():
                shutil.rmtree(self.temp_folder)
            self.temp_folder.mkdir(exist_ok=True)
        except Exception as e:
            print(f"Error clearing temp folder: {e}")
    
    def download_tiktok_videos(self, profile_url, max_videos=50):
        """Download TikTok videos from a profile"""
        print(f"Downloading up to {max_videos} videos from {profile_url}")
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'best[ext=mp4]',
            'outtmpl': str(self.temp_folder / '%(uploader)s_%(upload_date)s_%(title)s.%(ext)s'),
            'playlistend': max_videos,
            'playlistreverse': False,  # Get latest videos first
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'ignoreerrors': True,  # Continue if some videos fail
        }
        
        downloaded_files = []
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("Extracting video information...")
                # Extract info first to get video URLs
                info = ydl.extract_info(profile_url, download=False)
                
                if 'entries' in info:
                    # Filter out None entries and limit to max_videos
                    entries = [entry for entry in info['entries'] if entry is not None][:max_videos]
                    
                    print(f"Found {len(entries)} videos to download")
                    
                    for i, entry in enumerate(entries):
                        try:
                            print(f"Downloading video {i+1}/{len(entries)}: {entry.get('title', 'Unknown')}")
                            
                            # Download individual video
                            video_url = entry['webpage_url']
                            
                            # Create a new ydl instance for individual downloads
                            individual_ydl_opts = {
                                'format': 'best[ext=mp4]',
                                'outtmpl': str(self.temp_folder / f'video_{i+1:03d}_%(title)s.%(ext)s'),
                                'quiet': True,
                                'no_warnings': True,
                            }
                            
                            with yt_dlp.YoutubeDL(individual_ydl_opts) as individual_ydl:
                                individual_ydl.download([video_url])
                            
                            # Find the downloaded file
                            downloaded_file = None
                            for file in self.temp_folder.glob(f"video_{i+1:03d}_*.mp4"):
                                downloaded_file = file
                                break
                            
                            if downloaded_file and downloaded_file.exists():
                                downloaded_files.append(downloaded_file)
                                print(f"✓ Downloaded: {downloaded_file.name}")
                            else:
                                print(f"✗ Failed to find downloaded file for video {i+1}")
                                        
                        except Exception as e:
                            print(f"Error downloading video {i+1}: {e}")
                            continue
                            
                else:
                    print("No videos found in the profile")
                    
        except Exception as e:
            print(f"Error downloading videos: {e}")
            
        print(f"Successfully downloaded {len(downloaded_files)} out of {max_videos} requested videos")
        return downloaded_files
    
    def process_video(self, video_path, max_duration=20, add_overlay=True):
        """Process individual video: cut to max duration and add image overlay if specified"""
        try:
            print(f"Processing video: {video_path.name}")
            
            # Load video
            clip = VideoFileClip(str(video_path))
            
            # Cut to maximum duration if needed
            if clip.duration > max_duration:
                clip = clip.subclip(0, max_duration)
            
            # Add overlay if specified and overlay image exists
            if add_overlay:
                overlay_image_path = self.get_overlay_image()
                if overlay_image_path:
                    print(f"Adding overlay: {overlay_image_path.name}")
                    # Create image overlay
                    overlay_clip = ImageClip(str(overlay_image_path))
                    
                    # Resize overlay to fit video if needed (optional)
                    if overlay_clip.w > clip.w or overlay_clip.h > clip.h:
                        overlay_clip = overlay_clip.resize(height=clip.h//4)  # Make it 1/4 of video height
                    
                    # Position overlay at center of video
                    overlay_clip = overlay_clip.set_position('center').set_duration(clip.duration)
                    
                    # Composite video with overlay
                    final_clip = CompositeVideoClip([clip, overlay_clip])
                else:
                    print("No overlay image found in overlay folder")
                    final_clip = clip
            else:
                final_clip = clip
            
            # Save processed video
            output_path = self.temp_folder / f"processed_{video_path.name}"
            final_clip.write_videofile(str(output_path), codec='libx264', audio_codec='aac')
            
            # Clean up
            clip.close()
            if final_clip != clip:
                final_clip.close()
            
            return output_path
            
        except Exception as e:
            print(f"Error processing video {video_path.name}: {e}")
            return None
    
    def get_input_video(self):
        """Get the input video from the input folder"""
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
        
        for ext in video_extensions:
            for video_file in self.input_folder.glob(f"*{ext}"):
                return video_file
        
        return None
    
    def create_video_pairs(self, processed_videos, input_video_path):
        """Create individual video pairs: each TikTok video + input video"""
        print("Creating individual video pairs...")
        
        if not input_video_path or not input_video_path.exists():
            print("Input video not found")
            return []
        
        created_pairs = []
        
        try:
            # Load input video once
            input_clip = VideoFileClip(str(input_video_path))
            
            for i, video_path in enumerate(processed_videos):
                if video_path and video_path.exists():
                    try:
                        print(f"Creating pair {i+1}/{len(processed_videos)}")
                        
                        # Load TikTok video
                        tiktok_clip = VideoFileClip(str(video_path))
                        
                        # Create pair: TikTok video + input video
                        pair_video = concatenate_videoclips([tiktok_clip, input_clip])
                        
                        # Save pair
                        output_path = self.output_folder / f"video_pair_{i+1:02d}.mp4"
                        pair_video.write_videofile(str(output_path), codec='libx264', audio_codec='aac')
                        
                        created_pairs.append(output_path)
                        
                        # Clean up
                        tiktok_clip.close()
                        pair_video.close()
                        
                    except Exception as e:
                        print(f"Error creating pair {i+1}: {e}")
                        continue
            
            # Clean up input clip
            input_clip.close()
            
            return created_pairs
            
        except Exception as e:
            print(f"Error creating video pairs: {e}")
            return []
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        print("Cleaning up temporary files...")
        try:
            shutil.rmtree(self.temp_folder)
            self.temp_folder.mkdir(exist_ok=True)
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")
    
    def run(self):
        """Main execution function"""
        print("=== TikTok Video Processor ===")
        
        # Clear temp folder to ensure clean start
        self.clear_temp_folder()
        
        # Get input video
        input_video = self.get_input_video()
        if not input_video:
            print("No input video found in 'input' folder. Please add a video file.")
            return
        
        print(f"Found input video: {input_video.name}")
        
        # Check for overlay image
        overlay_image = self.get_overlay_image()
        if overlay_image:
            print(f"Found overlay image: {overlay_image.name}")
        else:
            print("No overlay image found in 'overlay' folder. TikTok videos will have no overlay.")
        
        # Get TikTok profile URL
        profile_url = input("Enter TikTok profile URL: ").strip()
        if not profile_url:
            print("No profile URL provided")
            return
        
        # Validate and normalize URL
        if not any(domain in profile_url for domain in ['tiktok.com', 'vm.tiktok.com']):
            print("Invalid TikTok URL. Please use a valid TikTok profile URL.")
            return
        
        print(f"Using profile URL: {profile_url}")
        
        # Get number of videos to download
        try:
            max_videos = int(input("Enter maximum number of videos to download (1-50): "))
            if max_videos < 1 or max_videos > 50:
                print("Number must be between 1 and 50")
                return
        except ValueError:
            print("Invalid number format")
            return
        
        # Download TikTok videos
        downloaded_videos = self.download_tiktok_videos(profile_url, max_videos)
        
        if not downloaded_videos:
            print("No videos were downloaded")
            return
        
        print(f"Downloaded {len(downloaded_videos)} videos")
        
        # Process each video (with overlay for TikTok videos)
        processed_videos = []
        for video_path in downloaded_videos:
            processed_video = self.process_video(video_path, add_overlay=True)
            if processed_video:
                processed_videos.append(processed_video)
        
        print(f"Processed {len(processed_videos)} videos")
        
        # Create individual video pairs
        video_pairs = self.create_video_pairs(processed_videos, input_video)
        
        if video_pairs:
            print(f"Created {len(video_pairs)} video pairs:")
            for pair in video_pairs:
                print(f"  - {pair.name}")
            print("Process completed successfully!")
        else:
            print("Failed to create video pairs")
        
        # Clean up temporary files
        self.cleanup_temp_files()

def main():
    processor = TikTokVideoProcessor()
    processor.run()

if __name__ == "__main__":
    main()