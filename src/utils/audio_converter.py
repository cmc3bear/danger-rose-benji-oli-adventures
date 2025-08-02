"""Audio conversion utilities for optimizing music files."""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import shutil


class AudioConverter:
    """Utility for converting and optimizing audio files."""
    
    def __init__(self):
        """Initialize the audio converter."""
        self.ffmpeg_available = self._check_ffmpeg()
        self.conversion_stats = {
            "files_converted": 0,
            "total_size_before": 0,
            "total_size_after": 0,
            "conversion_errors": []
        }
        
        # Default conversion settings
        self.settings = {
            "output_format": "ogg",
            "quality": "192k",
            "sample_rate": 44100,
            "channels": 2,
            "normalize": True,
            "fade_in": 0.0,
            "fade_out": 0.0,
            "compression_level": 6  # OGG compression level (0-10)
        }
    
    def _check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available on the system.
        
        Returns:
            True if ffmpeg is available
        """
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def convert_file(self, input_path: str, output_path: str, 
                    settings: Optional[Dict] = None) -> bool:
        """Convert a single audio file.
        
        Args:
            input_path: Path to input audio file
            output_path: Path for output file
            settings: Optional conversion settings override
            
        Returns:
            True if conversion was successful
        """
        if not os.path.exists(input_path):
            print(f"Error: Input file not found: {input_path}")
            return False
        
        if not self.ffmpeg_available:
            print("Error: ffmpeg not available for audio conversion")
            return False
        
        # Use provided settings or defaults
        conv_settings = settings or self.settings
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Build ffmpeg command
        cmd = self._build_ffmpeg_command(input_path, output_path, conv_settings)
        
        try:
            # Get file size before conversion
            size_before = os.path.getsize(input_path)
            
            # Run conversion
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                # Get file size after conversion
                size_after = os.path.getsize(output_path)
                
                # Update stats
                self.conversion_stats["files_converted"] += 1
                self.conversion_stats["total_size_before"] += size_before
                self.conversion_stats["total_size_after"] += size_after
                
                print(f"✓ Converted: {input_path} -> {output_path}")
                print(f"  Size: {size_before:,} bytes -> {size_after:,} bytes "
                      f"({(size_after/size_before)*100:.1f}%)")
                
                return True
            else:
                error_msg = f"Conversion failed: {result.stderr}"
                print(f"✗ {error_msg}")
                self.conversion_stats["conversion_errors"].append(error_msg)
                return False
                
        except subprocess.TimeoutExpired:
            error_msg = f"Conversion timeout: {input_path}"
            print(f"✗ {error_msg}")
            self.conversion_stats["conversion_errors"].append(error_msg)
            return False
        except Exception as e:
            error_msg = f"Conversion error: {input_path} - {str(e)}"
            print(f"✗ {error_msg}")
            self.conversion_stats["conversion_errors"].append(error_msg)
            return False
    
    def _build_ffmpeg_command(self, input_path: str, output_path: str, 
                             settings: Dict) -> List[str]:
        """Build ffmpeg command with specified settings.
        
        Args:
            input_path: Input file path
            output_path: Output file path
            settings: Conversion settings
            
        Returns:
            List of command arguments for ffmpeg
        """
        cmd = ["ffmpeg", "-i", input_path]
        
        # Audio codec and quality settings
        if settings["output_format"] == "ogg":
            cmd.extend(["-c:a", "libvorbis"])
            cmd.extend(["-q:a", str(self._quality_to_vorbis_q(settings["quality"]))])
        elif settings["output_format"] == "mp3":
            cmd.extend(["-c:a", "libmp3lame"])
            cmd.extend(["-b:a", settings["quality"]])
        
        # Sample rate and channels
        cmd.extend(["-ar", str(settings["sample_rate"])])
        cmd.extend(["-ac", str(settings["channels"])])
        
        # Audio filters
        filters = []
        
        # Normalization
        if settings.get("normalize", False):
            filters.append("loudnorm")
        
        # Fade effects
        if settings.get("fade_in", 0) > 0:
            filters.append(f"afade=t=in:st=0:d={settings['fade_in']}")
        
        if settings.get("fade_out", 0) > 0:
            filters.append(f"afade=t=out:st=-{settings['fade_out']}:d={settings['fade_out']}")
        
        # Apply filters if any
        if filters:
            cmd.extend(["-af", ",".join(filters)])
        
        # Overwrite output file
        cmd.append("-y")
        
        # Output file
        cmd.append(output_path)
        
        return cmd
    
    def _quality_to_vorbis_q(self, quality: str) -> int:
        """Convert bitrate string to Vorbis quality level.
        
        Args:
            quality: Quality string like "192k"
            
        Returns:
            Vorbis quality level (0-10)
        """
        # Extract numeric value
        numeric_quality = int(quality.replace("k", ""))
        
        # Map bitrates to Vorbis quality levels
        quality_map = {
            64: 0,
            80: 1,
            96: 2,
            112: 3,
            128: 4,
            160: 5,
            192: 6,
            224: 7,
            256: 8,
            320: 9,
            500: 10
        }
        
        # Find closest match
        closest_bitrate = min(quality_map.keys(), 
                             key=lambda x: abs(x - numeric_quality))
        return quality_map[closest_bitrate]
    
    def convert_directory(self, input_dir: str, output_dir: str,
                         recursive: bool = True) -> Dict[str, bool]:
        """Convert all audio files in a directory.
        
        Args:
            input_dir: Input directory path
            output_dir: Output directory path
            recursive: Whether to process subdirectories
            
        Returns:
            Dictionary mapping file paths to conversion success
        """
        if not os.path.exists(input_dir):
            print(f"Error: Input directory not found: {input_dir}")
            return {}
        
        # Find audio files
        audio_extensions = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".wma"}
        audio_files = []
        
        if recursive:
            for root, dirs, files in os.walk(input_dir):
                for file in files:
                    if Path(file).suffix.lower() in audio_extensions:
                        audio_files.append(os.path.join(root, file))
        else:
            for file in os.listdir(input_dir):
                if Path(file).suffix.lower() in audio_extensions:
                    audio_files.append(os.path.join(input_dir, file))
        
        if not audio_files:
            print(f"No audio files found in {input_dir}")
            return {}
        
        print(f"Found {len(audio_files)} audio files to convert")
        
        # Convert each file
        results = {}
        for input_file in audio_files:
            # Calculate relative path for output
            rel_path = os.path.relpath(input_file, input_dir)
            output_file = os.path.join(output_dir, rel_path)
            
            # Change extension to target format
            output_file = str(Path(output_file).with_suffix(f".{self.settings['output_format']}"))
            
            # Convert file
            success = self.convert_file(input_file, output_file)
            results[input_file] = success
        
        return results
    
    def batch_convert_music_library(self, music_dir: str) -> bool:
        """Convert entire music library with optimized settings for each category.
        
        Args:
            music_dir: Root music directory path
            
        Returns:
            True if all conversions were successful
        """
        # Category-specific settings
        category_settings = {
            "title": {**self.settings, "quality": "256k"},  # Higher quality for title
            "hub": {**self.settings, "quality": "192k", "normalize": True},
            "minigame": {**self.settings, "quality": "192k", "compression_level": 7},
            "victory": {**self.settings, "quality": "160k"},  # Short clips
            "unlockables": {**self.settings, "quality": "256k"},  # Special tracks
        }
        
        all_success = True
        
        for category, settings in category_settings.items():
            input_cat_dir = os.path.join(music_dir, "original", category)
            output_cat_dir = os.path.join(music_dir, "converted", category)
            
            if os.path.exists(input_cat_dir):
                print(f"\n🎵 Converting {category} music...")
                results = self.convert_directory(input_cat_dir, output_cat_dir)
                
                # Check if all conversions in category succeeded
                category_success = all(results.values()) if results else True
                all_success = all_success and category_success
                
                if category_success:
                    print(f"✓ {category} conversion completed successfully")
                else:
                    print(f"✗ {category} conversion had errors")
        
        return all_success
    
    def get_conversion_report(self) -> Dict:
        """Get detailed conversion statistics.
        
        Returns:
            Dictionary with conversion statistics
        """
        stats = self.conversion_stats.copy()
        
        if stats["total_size_before"] > 0:
            compression_ratio = stats["total_size_after"] / stats["total_size_before"]
            size_reduction = (1 - compression_ratio) * 100
            
            stats["compression_ratio"] = compression_ratio
            stats["size_reduction_percent"] = size_reduction
            stats["space_saved_mb"] = (stats["total_size_before"] - stats["total_size_after"]) / (1024 * 1024)
        
        return stats
    
    def validate_converted_files(self, converted_dir: str) -> Dict[str, bool]:
        """Validate that converted files are playable.
        
        Args:
            converted_dir: Directory containing converted files
            
        Returns:
            Dictionary mapping file paths to validation results
        """
        results = {}
        
        for root, dirs, files in os.walk(converted_dir):
            for file in files:
                if file.endswith(f".{self.settings['output_format']}"):
                    file_path = os.path.join(root, file)
                    
                    # Basic validation - check if file exists and has content
                    try:
                        file_size = os.path.getsize(file_path)
                        is_valid = file_size > 1024  # At least 1KB
                        
                        # Could add more sophisticated validation here
                        # like trying to load with pygame.mixer.Sound
                        
                        results[file_path] = is_valid
                        
                        if not is_valid:
                            print(f"⚠️  Invalid converted file: {file_path}")
                            
                    except OSError:
                        results[file_path] = False
                        print(f"✗ Error validating: {file_path}")
        
        return results
    
    def create_conversion_script(self, output_path: str = "convert_music.py") -> str:
        """Create a standalone script for music conversion.
        
        Args:
            output_path: Path for the conversion script
            
        Returns:
            Path to the created script
        """
        script_content = '''#!/usr/bin/env python3
"""
Standalone music conversion script for Danger Rose.
Converts MP3 files to optimized OGG format.
"""

import os
import sys
from pathlib import Path

# Add src to path so we can import the converter
sys.path.insert(0, str(Path(__file__).parent / "src"))

from utils.audio_converter import AudioConverter

def main():
    """Main conversion function."""
    converter = AudioConverter()
    
    if not converter.ffmpeg_available:
        print("Error: ffmpeg is required for audio conversion")
        print("Please install ffmpeg and make sure it's in your PATH")
        return 1
    
    # Default paths
    music_dir = Path("assets/audio/music")
    
    if not music_dir.exists():
        print(f"Error: Music directory not found: {music_dir}")
        return 1
    
    print("🎵 Starting music conversion for Danger Rose...")
    print(f"Converting files in: {music_dir}")
    
    # Convert all music
    success = converter.batch_convert_music_library(str(music_dir))
    
    # Print report
    report = converter.get_conversion_report()
    print("\\n📊 Conversion Report:")
    print(f"Files converted: {report['files_converted']}")
    print(f"Space saved: {report.get('space_saved_mb', 0):.1f} MB")
    print(f"Size reduction: {report.get('size_reduction_percent', 0):.1f}%")
    
    if report['conversion_errors']:
        print(f"Errors: {len(report['conversion_errors'])}")
        for error in report['conversion_errors']:
            print(f"  - {error}")
    
    if success:
        print("\\n✅ All conversions completed successfully!")
        return 0
    else:
        print("\\n❌ Some conversions failed. Check errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
        
        with open(output_path, 'w') as f:
            f.write(script_content)
        
        # Make script executable on Unix systems
        try:
            os.chmod(output_path, 0o755)
        except:
            pass
        
        print(f"Created conversion script: {output_path}")
        return output_path