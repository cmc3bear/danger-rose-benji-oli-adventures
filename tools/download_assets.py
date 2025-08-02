#!/usr/bin/env python3
"""
Asset Download Tool for Danger Rose
Downloads high-quality character sprites from various free sources.
"""

import shutil
import zipfile
from pathlib import Path

import requests


class AssetDownloader:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.downloads_dir = self.project_root / "assets" / "downloads"
        self.downloads_dir.mkdir(parents=True, exist_ok=True)

        # Asset sources
        self.sources = {
            "lpc_characters_v3": {
                "url": "https://opengameart.org/sites/default/files/lpc-character-bases-v3_1.zip",
                "filename": "lpc-character-bases-v3_1.zip",
                "description": "LPC Character Bases with child/adult variations",
            }
        }

    def download_file(self, url, filename):
        """Download a file with progress indication"""
        print(f"Downloading {filename}...")

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            filepath = self.downloads_dir / filename
            total_size = int(response.headers.get("content-length", 0))

            with open(filepath, "wb") as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(
                                f"\\r  Progress: {percent:.1f}% ({downloaded:,} / {total_size:,} bytes)",
                                end="",
                            )

            print(f"\\n  Downloaded: {filepath}")
            return filepath

        except Exception as e:
            print(f"  Error downloading {filename}: {e}")
            return None

    def extract_zip(self, zip_path, extract_to):
        """Extract zip file to specified directory"""
        print(f"Extracting {zip_path.name}...")

        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_to)

            print(f"  Extracted to: {extract_to}")
            return True

        except Exception as e:
            print(f"  Error extracting {zip_path.name}: {e}")
            return False

    def download_lpc_characters(self):
        """Download LPC character bases"""
        source = self.sources["lpc_characters_v3"]

        # Download the zip file
        zip_path = self.download_file(source["url"], source["filename"])

        if zip_path and zip_path.exists():
            # Extract to organized directory
            extract_dir = self.downloads_dir / "lpc_characters"
            extract_dir.mkdir(exist_ok=True)

            if self.extract_zip(zip_path, extract_dir):
                print(f"  LPC Characters available at: {extract_dir}")
                return extract_dir

        return None

    def organize_lpc_assets(self, lpc_dir):
        """Organize LPC assets by character type"""
        if not lpc_dir or not lpc_dir.exists():
            return

        print("Organizing LPC assets...")

        # Create organized structure
        organized_dir = self.downloads_dir / "lpc_organized"
        organized_dir.mkdir(exist_ok=True)

        # Look for useful character files
        character_types = ["child", "teen", "adult", "male", "female"]

        for png_file in lpc_dir.rglob("*.png"):
            filename = png_file.name.lower()

            # Categorize by character type
            for char_type in character_types:
                if char_type in filename:
                    target_dir = organized_dir / char_type
                    target_dir.mkdir(exist_ok=True)

                    target_path = target_dir / png_file.name
                    shutil.copy2(png_file, target_path)
                    print(f"  Organized: {png_file.name} → {char_type}/")
                    break

    def create_asset_summary(self):
        """Create a summary of available assets"""
        summary_content = """# Downloaded Assets Summary

## Available Character Assets

### 1. LPC Character Bases (OpenGameArt.org)
- **Source**: Liberated Pixel Cup community
- **License**: CC-BY-SA 3.0 / GPL 3.0
- **Location**: `assets/downloads/lpc_characters/`
- **Features**:
  - Multiple body types (child, teen, adult, muscular)
  - Complete animation sets (walk, cast, thrust, shoot, hurt, jump)
  - Modular heads (human, fantasy races)
  - Easy to recolor and modify

### Usage Recommendations

#### For Danger Rose Project:
1. **Use Kenney sprites as primary** (already extracted)
   - Consistent cartoon style
   - Family-friendly appearance
   - Rich animations

2. **Use LPC assets for reference**:
   - Child body proportions
   - Animation timing
   - Additional poses/actions

3. **Custom outfit creation**:
   - Modify existing Kenney sprites
   - Add scene-specific clothing
   - Maintain art style consistency

### Next Steps:
1. Review LPC assets for useful reference materials
2. Create custom outfit variations for each scene
3. Test new sprites in game engine
4. Optimize file sizes for web distribution

## Attribution Notes:
- LPC assets require attribution if used
- Kenney assets are CC0 (no attribution required)
- Document any assets used in final game
"""

        summary_path = self.downloads_dir / "ASSETS_SUMMARY.md"
        with open(summary_path, "w") as f:
            f.write(summary_content)

        print(f"Created asset summary: {summary_path}")


def main():
    """Main execution function"""
    print("Danger Rose Asset Downloader")
    print("=" * 40)

    downloader = AssetDownloader()

    # Download LPC character bases
    print("\\n1. Downloading LPC Character Bases...")
    lpc_dir = downloader.download_lpc_characters()

    # Organize the assets
    print("\\n2. Organizing assets...")
    downloader.organize_lpc_assets(lpc_dir)

    # Create summary
    print("\\n3. Creating asset summary...")
    downloader.create_asset_summary()

    print("\\n" + "=" * 40)
    print("Download complete!")
    print(f"Assets available in: {downloader.downloads_dir}")
    print("\\nRecommendation: Use your existing Kenney sprites as primary assets.")
    print("Use downloaded assets for reference and inspiration.")


if __name__ == "__main__":
    main()
