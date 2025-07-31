#!/usr/bin/env python3
"""
Test script to verify all dependencies are installed correctly and check versions
"""

import subprocess
import sys
import pkg_resources
import requests
from packaging import version
import platform

def check_latest_version(package_name):
    """Check the latest version of a package on PyPI"""
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data["info"]["version"]
    except Exception as e:
        print(f"Could not check latest version for {package_name}: {e}")
    return None

def get_installed_version(package_name):
    """Get the installed version of a package"""
    try:
        return pkg_resources.get_distribution(package_name).version
    except pkg_resources.DistributionNotFound:
        return None

def auto_install_or_update_package(package_name, display_name):
    """Automatically install or update a Python package"""
    print(f"🔄 Installing/updating {display_name}...")
    try:
        # For MoviePy, use version 2.2.1 for latest compatibility
        if package_name == 'moviepy':
            result = subprocess.run([sys.executable, '-m', 'pip', 'uninstall', package_name, '-y'], 
                                  capture_output=True, text=True, timeout=60)
            print(f"  Uninstalled old {display_name}")
            # Install specific version 2.2.1 for latest features
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'moviepy==2.2.1', '--no-cache-dir'], 
                                  capture_output=True, text=True, timeout=120)
        else:
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', package_name], 
                                  capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"✅ {display_name} installed/updated successfully!")
            return True
        else:
            print(f"❌ Failed to install/update {display_name}: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ Install/update timeout for {display_name}")
        return False
    except Exception as e:
        print(f"❌ Error installing/updating {display_name}: {e}")
        return False

def auto_install_ffmpeg():
    """Automatically install FFmpeg using Windows package managers or direct download"""
    print("🔄 Attempting to install FFmpeg...")
    
    # Check if running on Windows
    if platform.system() != "Windows":
        print("❌ Auto-install for FFmpeg only supported on Windows")
        return False
    
    # Try winget first (Windows 10/11)
    try:
        print("  Trying winget...")
        result = subprocess.run(['winget', 'install', 'Gyan.FFmpeg'], 
                              capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print("✅ FFmpeg installed successfully via winget!")
            return True
        else:
            print("  winget install failed")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("  winget not available")
    
    # If winget fails, provide direct download command
    print("\n❌ Could not auto-install FFmpeg via winget")
    print("💡 Run this command in PowerShell as Administrator to install FFmpeg:")
    print("=" * 80)
    
    cmd = '''# Download and install FFmpeg
$ffmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$downloadPath = "$env:TEMP\\ffmpeg.zip"
$extractPath = "C:\\ffmpeg"

Write-Host "Downloading FFmpeg..." -ForegroundColor Yellow
Invoke-WebRequest -Uri $ffmpegUrl -OutFile $downloadPath

Write-Host "Extracting FFmpeg..." -ForegroundColor Yellow
Expand-Archive -Path $downloadPath -DestinationPath $extractPath -Force

# Find the actual ffmpeg folder (it has a version number)
$ffmpegFolder = Get-ChildItem -Path $extractPath -Directory | Where-Object { $_.Name -like "ffmpeg-*" } | Select-Object -First 1
$ffmpegBinPath = Join-Path $ffmpegFolder.FullName "bin"

Write-Host "Adding FFmpeg to PATH..." -ForegroundColor Yellow
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
if ($currentPath -notlike "*$ffmpegBinPath*") {
    [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$ffmpegBinPath", "Machine")
    Write-Host "FFmpeg added to system PATH" -ForegroundColor Green
} else {
    Write-Host "FFmpeg already in PATH" -ForegroundColor Green
}

# Clean up
Remove-Item $downloadPath -Force
Write-Host "Installation complete! Restart this script to verify." -ForegroundColor Green'''
    
    print(cmd)
    print("=" * 80)
    print("\nAfter running the command above, restart this script to verify the installation.")
    return False

def fix_moviepy_installation():
    """Fix common MoviePy installation issues"""
    print("🔧 Attempting to fix MoviePy installation...")
    
    try:
        # First, try to uninstall and reinstall MoviePy completely
        print("  Uninstalling MoviePy...")
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', 'moviepy', '-y'], 
                      capture_output=True, text=True, timeout=60)
        
        # Also uninstall imageio-ffmpeg which can cause issues
        subprocess.run([sys.executable, '-m', 'pip', 'uninstall', 'imageio-ffmpeg', '-y'], 
                      capture_output=True, text=True, timeout=60)
        
        print("  Reinstalling MoviePy with dependencies...")
        # Use version 2.2.1 for latest features
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'moviepy==2.2.1', 'imageio-ffmpeg', '--no-cache-dir'], 
                              capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0:
            print("✅ MoviePy reinstalled successfully!")
            
            # Test the import immediately with new API
            try:
                from moviepy import VideoFileClip
                print("✅ MoviePy import test passed!")
                return True
            except ImportError as e:
                print(f"❌ MoviePy import still failing: {e}")
                return False
        else:
            print(f"❌ Failed to reinstall MoviePy: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing MoviePy: {e}")
        return False

def test_ffmpeg():
    """Test if ffmpeg is installed and accessible, auto-install if missing"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # Extract version from output
            version_line = result.stdout.split('\n')[0]
            ffmpeg_version = version_line.split()[2] if len(version_line.split()) > 2 else "unknown"
            print(f"✓ FFmpeg is installed (version: {ffmpeg_version})")
            return True
        else:
            print("❌ FFmpeg is installed but not working properly")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
        print("❌ FFmpeg is not installed or not in PATH")
        
        # Attempt auto-installation
        if auto_install_ffmpeg():
            # Re-test after installation
            try:
                result = subprocess.run(['ffmpeg', '-version'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    version_line = result.stdout.split('\n')[0]
                    ffmpeg_version = version_line.split()[2] if len(version_line.split()) > 2 else "unknown"
                    print(f"✓ FFmpeg now working (version: {ffmpeg_version})")
                    return True
            except Exception:
                pass
        
        print("  Manual install: https://ffmpeg.org/download.html")
        return False

def test_versions():
    """Check versions of critical packages and auto-install/update"""
    print("\n=== Version Information & Auto-Updates ===")
    
    packages_to_check = {
        'moviepy': 'moviepy',
        'yt-dlp': 'yt-dlp',
        'Pillow': 'Pillow',
        'requests': 'requests',
        'packaging': 'packaging'
    }
    
    packages_updated = []
    
    for display_name, package_name in packages_to_check.items():
        installed_ver = get_installed_version(package_name)
        needs_update = False
        
        if installed_ver:
            print(f"✓ {display_name}: {installed_ver} (installed)")
            
            # Check latest version
            latest_ver = check_latest_version(package_name)
            if latest_ver:
                if version.parse(installed_ver) < version.parse(latest_ver):
                    print(f"  ⚠️  Newer version available: {latest_ver}")
                    # Special handling for MoviePy - ask user before updating
                    if package_name == 'moviepy':
                        try:
                            # Test if current MoviePy works with new API
                            from moviepy import VideoFileClip
                            print(f"  ✅ Current MoviePy {installed_ver} is working correctly")
                            response = input(f"  ❓ Update MoviePy to {latest_ver}? (y/N): ").strip().lower()
                            if response in ['y', 'yes']:
                                needs_update = True
                            else:
                                print(f"  ℹ️  Keeping current working version {installed_ver}")
                                needs_update = False
                        except ImportError:
                            print(f"  ❌ Current MoviePy {installed_ver} is not working, will update")
                            needs_update = True
                    else:
                        needs_update = True
                else:
                    print(f"  ✅ Up to date (latest: {latest_ver})")
            else:
                print(f"  ❓ Could not check latest version")
        else:
            print(f"❌ {display_name}: Not installed")
            needs_update = True
        
        # Install or update if needed
        if needs_update:
            if auto_install_or_update_package(package_name, display_name):
                packages_updated.append(display_name)
                # Get new version after update
                new_ver = get_installed_version(package_name)
                if new_ver:
                    print(f"  ✅ Now at version: {new_ver}")
    
    if packages_updated:
        print(f"\n✅ Updated packages: {', '.join(packages_updated)}")
    else:
        print(f"\n✅ All packages are up to date!")

def test_imports():
    """Test if all required packages can be imported"""
    print("\n=== Testing Imports ===")
    
    # Test yt-dlp first
    try:
        import yt_dlp
        print("✓ yt-dlp imported successfully")
    except ImportError as e:
        print(f"❌ yt-dlp import error: {e}")
        return False
    
    # Test MoviePy with new 2.2.1 API
    moviepy_imported = False
    try:
        from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
        print("✓ moviepy imported successfully")
        moviepy_imported = True
    except ImportError as e:
        print(f"❌ moviepy import error: {e}")
        print("🔧 Attempting to fix MoviePy installation...")
        
        if fix_moviepy_installation():
            # Try importing again after fix
            try:
                from moviepy import VideoFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
                print("✓ moviepy imported successfully after fix!")
                moviepy_imported = True
            except ImportError as e2:
                print(f"❌ moviepy still failing after fix: {e2}")
                moviepy_imported = False
    
    if not moviepy_imported:
        return False
    
    # Test other packages
    try:
        import requests
        print("✓ requests imported successfully")
        
        from PIL import Image
        print("✓ Pillow imported successfully")
        
        import os
        from pathlib import Path
        print("✓ Standard libraries imported successfully")
        
        # Test packaging import (needed for version comparison)
        from packaging import version
        print("✓ packaging imported successfully")
        
        print("\n✅ All dependencies are installed correctly!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_moviepy_functionality():
    """Test if moviepy can actually process videos"""
    print("\n=== Testing MoviePy Functionality ===")
    try:
        from moviepy import VideoFileClip, ColorClip
        
        # Create a test clip
        test_clip = ColorClip(size=(640, 480), color=(255, 0, 0), duration=1)
        
        # Test basic operations
        test_clip_resized = test_clip.resize(0.5)
        test_clip_subclip = test_clip.subclip(0, 0.5)
        
        # Clean up
        test_clip.close()
        test_clip_resized.close()
        test_clip_subclip.close()
        
        print("✓ MoviePy functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ MoviePy functionality test failed: {e}")
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
    print("Testing TikTok Video Processor setup with auto-install/update...\n")
    
    # Test and auto-update versions first
    test_versions()
    
    # Test imports (should work now if packages were installed)
    imports_ok = test_imports()
    
    if imports_ok:
        # Test FFmpeg (with auto-install)
        ffmpeg_ok = test_ffmpeg()
        
        # Test MoviePy functionality
        moviepy_ok = test_moviepy_functionality()
        
        # Test folders
        test_folders()
        
        # Final summary
        print("\n" + "="*50)
        if ffmpeg_ok and moviepy_ok:
            print("🎉 Setup complete! You can now run main.py")
        else:
            print("⚠️  Setup has issues. Please address the problems above.")
            if not ffmpeg_ok:
                print("   - FFmpeg installation failed - try manual installation")
            if not moviepy_ok:
                print("   - MoviePy functionality test failed")
    else:
        print("\n❌ Some dependencies could not be imported after installation.")
        print("💡 This often happens with MoviePy. Try these solutions:")
        print("1. Restart your Python environment/IDE")
        print("2. Run this script again")
        print("3. Manual reinstall: pip uninstall moviepy && pip install moviepy==2.2.1 --no-cache-dir")
        print("4. If still failing: pip install moviepy==2.2.1  # Use latest stable version")
