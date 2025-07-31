import os
import sys
from pathlib import Path
import yt_dlp
from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
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
        
    def validate_video_file(self, video_path):
        """Validate that a video file is not corrupted and can be read"""
        print(f"Validating video file: {video_path.name}")
        print(f"File size: {video_path.stat().st_size / (1024*1024):.1f} MB")
        
        try:
            with VideoFileClip(str(video_path)) as test_clip:
                # Try to read basic properties
                duration = test_clip.duration
                fps = test_clip.fps
                size = test_clip.size
                
                print(f"Duration: {duration:.2f} seconds")
                print(f"FPS: {fps}")
                print(f"Size: {size[0]}x{size[1]}")
                
                # Check if properties are valid
                if duration <= 0:
                    print(f"❌ Invalid duration: {duration}")
                    return False
                if fps <= 0:
                    print(f"❌ Invalid FPS: {fps}")
                    return False
                if size[0] <= 0 or size[1] <= 0:
                    print(f"❌ Invalid size: {size}")
                    return False
                    
                # Try to read a frame from the middle
                try:
                    test_frame = test_clip.get_frame(duration / 2)
                    print(f"✓ Successfully read frame from middle of video")
                except Exception as frame_error:
                    print(f"❌ Failed to read frame: {frame_error}")
                    return False
                
                print(f"✓ Video validation passed")
                return True
                
        except Exception as e:
            print(f"❌ Video validation failed for {video_path.name}: {e}")
            return False
    
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
                                # Validate the downloaded video
                                if self.validate_video_file(downloaded_file):
                                    downloaded_files.append(downloaded_file)
                                    print(f"✓ Downloaded: {downloaded_file.name}")
                                else:
                                    print(f"✗ Downloaded file appears corrupted: {downloaded_file.name}")
                                    # Try to delete corrupted file
                                    try:
                                        downloaded_file.unlink()
                                    except:
                                        pass
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
        overlay_clip = None
        clip = None
        final_clip = None
        
        try:
            print(f"Processing video: {video_path.name}")
            
            # Load video with error handling for corrupted frames
            clip = VideoFileClip(str(video_path))
            
            # Validate the clip duration to avoid frame index issues
            actual_duration = clip.duration
            if actual_duration <= 0:
                print(f"Warning: Video {video_path.name} has invalid duration: {actual_duration}")
                return None
            
            # Cut to maximum duration if needed, but leave a small buffer to avoid frame issues
            if actual_duration > max_duration:
                # Use a slightly shorter duration to avoid frame index errors
                safe_duration = min(max_duration, actual_duration - 0.1)
                clip = clip.subclip(0, max(safe_duration, 1.0))  # Ensure at least 1 second
            
            # Add overlay if specified and overlay image exists
            if add_overlay:
                overlay_image_path = self.get_overlay_image()
                if overlay_image_path:
                    print(f"Adding overlay: {overlay_image_path.name}")
                    # Create image overlay
                    overlay_clip = ImageClip(str(overlay_image_path))
                    
                    # Resize overlay to fit video if needed (optional)
                    if overlay_clip.w > clip.w or overlay_clip.h > clip.h:
                        overlay_clip = overlay_clip.resize(width=clip.w//1)  # 1/1 of video width

                    # Position overlay at center of video and set duration
                    overlay_clip = overlay_clip.with_position('center').with_duration(clip.duration)
                    
                    # Composite video with overlay
                    final_clip = CompositeVideoClip([clip, overlay_clip])
                else:
                    print("No overlay image found in overlay folder")
                    final_clip = clip
            else:
                final_clip = clip
            
            # Save processed video with consistent encoding settings and error handling
            output_path = self.temp_folder / f"processed_{video_path.name}"
            
            # Use more conservative encoding settings to handle problematic videos
            final_clip.write_videofile(
                str(output_path), 
                codec='libx264', 
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                fps=30  # Force consistent FPS
            )
            
            return output_path
            
        except Exception as e:
            print(f"Error processing video {video_path.name}: {e}")
            return None
        finally:
            # Proper cleanup of all clips
            if overlay_clip:
                overlay_clip.close()
            if final_clip and final_clip != clip:
                final_clip.close()
            if clip:
                clip.close()
    
    def get_input_video(self):
        """Get the input video from the input folder"""
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']
        
        print("Scanning input folder for video files...")
        print(f"Input folder path: {self.input_folder.absolute()}")
        
        all_files = list(self.input_folder.glob("*"))
        print(f"Found {len(all_files)} files in input folder:")
        for file in all_files:
            print(f"  - {file.name} ({file.stat().st_size / (1024*1024):.1f} MB)")
        
        for ext in video_extensions:
            video_files = list(self.input_folder.glob(f"*{ext}"))
            if video_files:
                print(f"Found {len(video_files)} {ext} files:")
                for video_file in video_files:
                    print(f"  - {video_file.name}")
                    return video_file
        
        print("❌ No video files found in input folder!")
        print("Expected file types:", ", ".join(video_extensions))
        return None
    
    def create_video_pairs(self, processed_videos, input_video_path):
        """Create individual video pairs: each TikTok video + input video"""
        print("Creating individual video pairs...")
        
        if not input_video_path or not input_video_path.exists():
            print("Input video not found")
            return []
        
        created_pairs = []
        
        try:
            # Load input video once to get its properties
            input_clip_template = VideoFileClip(str(input_video_path))
            input_resolution = input_clip_template.size
            input_fps = input_clip_template.fps
            print(f"Input video resolution: {input_resolution[0]}x{input_resolution[1]} @ {input_fps} FPS")
            input_clip_template.close()
            
            for i, video_path in enumerate(processed_videos):
                if video_path and video_path.exists():
                    try:
                        print(f"Creating pair {i+1}/{len(processed_videos)}")
                        
                        # Load fresh clips for each pair to avoid corruption
                        tiktok_clip = VideoFileClip(str(video_path))
                        input_clip = VideoFileClip(str(input_video_path))  # Fresh load each time
                        
                        # Display resolution information
                        tiktok_resolution = tiktok_clip.size
                        print(f"  TikTok video resolution: {tiktok_resolution[0]}x{tiktok_resolution[1]}")
                        print(f"  Input video resolution: {input_resolution[0]}x{input_resolution[1]}")
                        
                        # Validate clip durations before concatenation
                        if tiktok_clip.duration <= 0 or input_clip.duration <= 0:
                            print(f"Warning: Invalid clip duration for pair {i+1}, skipping")
                            tiktok_clip.close()
                            input_clip.close()
                            continue
                        
                        # Handle resolution differences
                        if tiktok_resolution != input_resolution:
                            print(f"  ⚠️  Resolution mismatch detected!")
                            print(f"  📐 Scaling TikTok video to fill frame (no black borders)...")

                            target_w, target_h = input_resolution
                            tiktok_w, tiktok_h = tiktok_resolution

                            # Determine the scaling factor to fill the frame
                            scale_factor = max(target_w / tiktok_w, target_h / tiktok_h)
                            new_w = int(tiktok_w * scale_factor)
                            new_h = int(tiktok_h * scale_factor)

                            print(f"  📏 Scaling from {tiktok_w}x{tiktok_h} to {new_w}x{new_h}")

                            # In MoviePy 2.2.1, we need to use a different approach for resizing
                            # Use the resize transformation method
                            tiktok_clip = tiktok_clip.resized((new_w, new_h))

                            # Crop the resized clip from the center if its size doesn't match the target.
                            if tiktok_clip.size != (target_w, target_h):
                                print(f"  ✂️  Cropping to exact size {target_w}x{target_h}")
                                crop_x = (tiktok_clip.w - target_w) // 2
                                crop_y = (tiktok_clip.h - target_h) // 2
                                
                                tiktok_clip = tiktok_clip.crop(x1=crop_x, y1=crop_y, width=target_w, height=target_h)

                            print(f"  ✓ TikTok video scaled to {target_w}x{target_h} (no black borders)")
                        else:
                            print(f"  ✓ Resolutions match, no resizing needed")
                        
                        # Create pair: TikTok video + input video
                        # Now both videos should have the same resolution
                        pair_video = concatenate_videoclips([tiktok_clip, input_clip])
                        
                        # Save pair with consistent encoding and better error handling
                        output_path = self.output_folder / f"video_pair_{i+1:02d}.mp4"
                        pair_video.write_videofile(
                            str(output_path), 
                            codec='libx264', 
                            audio_codec='aac',
                            temp_audiofile='temp-audio.m4a',
                            remove_temp=True,
                            fps=30  # Force consistent FPS
                        )
                        
                        created_pairs.append(output_path)
                        print(f"  ✓ Created: {output_path.name}")
                        
                        # Clean up clips immediately after use
                        tiktok_clip.close()
                        input_clip.close()
                        pair_video.close()
                        
                    except Exception as e:
                        print(f"Error creating pair {i+1}: {e}")
                        continue
            
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
            print("\n❌ No input video found in 'input' folder.")
            print("\n💡 To fix this:")
            print("1. Make sure you have a video file in the 'input' folder")
            print("2. Supported formats: .mp4, .avi, .mov, .mkv, .wmv, .flv")
            print("3. Try renaming your file to have a proper extension")
            print("4. Make sure the file isn't corrupted")
            return
        
        print(f"\n✓ Found input video: {input_video.name}")
        
        # Validate input video with detailed output
        print("\n=== Validating Input Video ===")
        if not self.validate_video_file(input_video):
            print("\n❌ Input video appears to be corrupted or unreadable.")
            print("\n💡 To fix this:")
            print("1. Try re-downloading or re-copying the video file")
            print("2. Convert the video to MP4 format using a video converter")
            print("3. Check if the file is completely downloaded (not partial)")
            print("4. Try a different video file")
            print("5. Make sure the video isn't DRM-protected")
            return
        
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
            # Validate video before processing
            if self.validate_video_file(video_path):
                processed_video = self.process_video(video_path, add_overlay=True)
                if processed_video:
                    processed_videos.append(processed_video)
            else:
                print(f"Skipping corrupted video: {video_path.name}")
        
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