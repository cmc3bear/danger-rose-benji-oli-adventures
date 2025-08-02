#!/usr/bin/env python3
"""
Retro sound processing utilities for Danger Rose.
Adds 8-bit/16-bit style effects to generated sounds.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional, Dict

class RetroSoundProcessor:
    """Process sounds to give them a retro game aesthetic."""
    
    def __init__(self):
        """Initialize the retro sound processor."""
        self.ffmpeg_available = self._check_ffmpeg()
        
        # Retro processing presets
        self.presets = {
            "8bit": {
                "bitrate": "64k",
                "sample_rate": 22050,
                "filters": [
                    "aformat=sample_fmts=u8|s16:channel_layouts=mono",
                    "volume=0.8",
                    "highpass=f=200",
                    "lowpass=f=8000",
                    "acompressor=threshold=0.5:ratio=4:attack=5:release=50"
                ]
            },
            "16bit": {
                "bitrate": "96k", 
                "sample_rate": 32000,
                "filters": [
                    "aformat=sample_fmts=s16:channel_layouts=stereo",
                    "volume=0.9",
                    "highpass=f=100",
                    "lowpass=f=12000",
                    "acompressor=threshold=0.6:ratio=3:attack=10:release=100"
                ]
            },
            "arcade": {
                "bitrate": "80k",
                "sample_rate": 22050,
                "filters": [
                    "aformat=sample_fmts=s16:channel_layouts=mono",
                    "volume=0.85",
                    "highpass=f=300",
                    "lowpass=f=10000",
                    "aphaser=type=t:speed=0.5:depth=0.5",
                    "acompressor=threshold=0.4:ratio=5:attack=2:release=20"
                ]
            },
            "chiptune": {
                "bitrate": "48k",
                "sample_rate": 11025,
                "filters": [
                    "aformat=sample_fmts=u8:channel_layouts=mono",
                    "volume=0.7",
                    "aresample=resampler=soxr",
                    "highpass=f=400",
                    "lowpass=f=4000",
                    "acompressor=threshold=0.3:ratio=8:attack=1:release=10",
                    "acontrast=contrast=100"
                ]
            }
        }
        
    def _check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available."""
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
    
    def process_sound(self, input_path: Path, output_path: Path, 
                     preset: str = "16bit", custom_filters: Optional[List[str]] = None) -> bool:
        """Process a sound file with retro effects.
        
        Args:
            input_path: Input sound file
            output_path: Output file path
            preset: Processing preset to use
            custom_filters: Optional custom filter list
            
        Returns:
            True if successful
        """
        if not self.ffmpeg_available:
            print("✗ ffmpeg not available for processing")
            return False
            
        if not input_path.exists():
            print(f"✗ Input file not found: {input_path}")
            return False
            
        # Get preset settings
        settings = self.presets.get(preset, self.presets["16bit"])
        
        # Build ffmpeg command
        cmd = ["ffmpeg", "-i", str(input_path)]
        
        # Audio codec
        cmd.extend(["-c:a", "libvorbis"])
        cmd.extend(["-b:a", settings["bitrate"]])
        cmd.extend(["-ar", str(settings["sample_rate"])])
        
        # Apply filters
        filters = custom_filters or settings["filters"]
        if filters:
            filter_string = ",".join(filters)
            cmd.extend(["-af", filter_string])
        
        # Output
        cmd.extend(["-y", str(output_path)])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"✓ Processed with {preset} preset: {output_path.name}")
                return True
            else:
                print(f"✗ Processing failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"✗ Processing timeout: {input_path}")
            return False
        except Exception as e:
            print(f"✗ Processing error: {str(e)}")
            return False
    
    def batch_process_directory(self, input_dir: Path, preset: str = "16bit") -> Dict[str, bool]:
        """Process all sounds in a directory with retro effects.
        
        Args:
            input_dir: Directory containing sound files
            preset: Processing preset to use
            
        Returns:
            Dictionary mapping file paths to success status
        """
        results = {}
        
        # Create processed subdirectory
        processed_dir = input_dir / "retro_processed"
        processed_dir.mkdir(exist_ok=True)
        
        # Find all OGG files
        ogg_files = list(input_dir.glob("*.ogg"))
        
        if not ogg_files:
            print(f"No OGG files found in {input_dir}")
            return results
            
        print(f"\n🎮 Processing {len(ogg_files)} sounds with {preset} preset...")
        
        for sound_file in ogg_files:
            output_path = processed_dir / sound_file.name
            success = self.process_sound(sound_file, output_path, preset)
            results[str(sound_file)] = success
            
        return results
    
    def create_variations(self, input_path: Path, output_dir: Path) -> Dict[str, Path]:
        """Create multiple retro variations of a sound.
        
        Args:
            input_path: Input sound file
            output_dir: Directory for output variations
            
        Returns:
            Dictionary mapping preset names to output paths
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        variations = {}
        
        stem = input_path.stem
        
        for preset_name, settings in self.presets.items():
            output_path = output_dir / f"{stem}_{preset_name}.ogg"
            
            if self.process_sound(input_path, output_path, preset_name):
                variations[preset_name] = output_path
                
        return variations
    
    def add_retro_effects(self, input_path: Path, output_path: Path,
                         pitch_shift: float = 0, echo: bool = False, 
                         distortion: float = 0) -> bool:
        """Add specific retro effects to a sound.
        
        Args:
            input_path: Input sound file
            output_path: Output file path
            pitch_shift: Semitones to shift pitch (negative for lower)
            echo: Add retro echo effect
            distortion: Amount of distortion (0-1)
            
        Returns:
            True if successful
        """
        filters = []
        
        # Base retro filters
        filters.extend([
            "aformat=sample_fmts=s16:channel_layouts=mono",
            "highpass=f=200",
            "lowpass=f=10000"
        ])
        
        # Pitch shift
        if pitch_shift != 0:
            # Convert semitones to frequency ratio
            ratio = 2 ** (pitch_shift / 12)
            filters.append(f"asetrate=44100*{ratio},atempo=1/{ratio}")
        
        # Echo effect
        if echo:
            filters.append("aecho=0.8:0.9:40:0.4")
        
        # Distortion
        if distortion > 0:
            gain = 1 + (distortion * 10)
            filters.append(f"volume={gain},acompressor=threshold=0.2:ratio=20:attack=0.01")
        
        # Process with custom filters
        return self.process_sound(input_path, output_path, "16bit", filters)


def main():
    """Main function to process sounds."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Add retro effects to game sounds")
    parser.add_argument("input", help="Input file or directory")
    parser.add_argument("-p", "--preset", default="16bit", 
                       choices=["8bit", "16bit", "arcade", "chiptune"],
                       help="Processing preset (default: 16bit)")
    parser.add_argument("-o", "--output", help="Output directory")
    parser.add_argument("--variations", action="store_true",
                       help="Create all preset variations")
    parser.add_argument("--pitch", type=float, default=0,
                       help="Pitch shift in semitones")
    parser.add_argument("--echo", action="store_true",
                       help="Add retro echo effect")
    parser.add_argument("--distortion", type=float, default=0,
                       help="Distortion amount (0-1)")
    
    args = parser.parse_args()
    
    processor = RetroSoundProcessor()
    
    if not processor.ffmpeg_available:
        print("✗ ffmpeg is required for sound processing")
        return 1
    
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Process single file
        if args.variations:
            # Create variations
            output_dir = Path(args.output or input_path.parent / "variations")
            variations = processor.create_variations(input_path, output_dir)
            print(f"\n✓ Created {len(variations)} variations")
        else:
            # Process with effects
            output_path = Path(args.output or input_path.parent / f"retro_{input_path.name}")
            
            if args.pitch or args.echo or args.distortion:
                success = processor.add_retro_effects(
                    input_path, output_path,
                    args.pitch, args.echo, args.distortion
                )
            else:
                success = processor.process_sound(input_path, output_path, args.preset)
                
            if success:
                print(f"\n✓ Processed: {output_path}")
            else:
                print(f"\n✗ Processing failed")
                return 1
                
    elif input_path.is_dir():
        # Process directory
        results = processor.batch_process_directory(input_path, args.preset)
        successful = sum(1 for v in results.values() if v)
        print(f"\n✓ Processed {successful}/{len(results)} files")
    else:
        print(f"✗ Invalid input: {input_path}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())