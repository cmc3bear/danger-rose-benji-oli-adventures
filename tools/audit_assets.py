#!/usr/bin/env python3
"""Audit all asset references in the codebase and check if files exist."""

import os
import re
from pathlib import Path
from typing import List, Tuple, Dict

def find_asset_references(project_root: Path) -> Dict[str, List[Tuple[str, int, str]]]:
    """Find all asset file references in Python source files.
    
    Returns:
        Dict mapping file types to list of (file_path, line_number, asset_path) tuples
    """
    asset_patterns = {
        'images': [
            r'\.png["\'`]',
            r'\.jpg["\'`]',
            r'\.jpeg["\'`]',
            r'images/[^"\'`]+["\'`]',
        ],
        'audio': [
            r'\.ogg["\'`]',
            r'\.mp3["\'`]',
            r'\.wav["\'`]',
            r'audio/[^"\'`]+["\'`]',
        ],
        'fonts': [
            r'\.ttf["\'`]',
            r'fonts/[^"\'`]+["\'`]',
        ]
    }
    
    references = {'images': [], 'audio': [], 'fonts': []}
    
    # Search through all Python files
    for py_file in project_root.rglob("*.py"):
        # Skip virtual environments and cache
        if any(part in py_file.parts for part in ['.venv', 'venv', '__pycache__', '.git']):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line_num, line in enumerate(lines, 1):
                # Check each asset type
                for asset_type, patterns in asset_patterns.items():
                    for pattern in patterns:
                        # Find asset references
                        matches = re.finditer(f'["\']([^"\']*{pattern[:-6]}[^"\']*)["\']', line)
                        for match in matches:
                            asset_path = match.group(1)
                            references[asset_type].append((str(py_file), line_num, asset_path))
                            
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
            
    return references

def check_asset_exists(project_root: Path, asset_path: str) -> Tuple[bool, Path]:
    """Check if an asset file exists.
    
    Returns:
        Tuple of (exists, full_path)
    """
    # Common asset base paths
    possible_paths = [
        project_root / asset_path,
        project_root / "assets" / asset_path,
        project_root / f"assets/{asset_path}",
    ]
    
    # Handle different path formats
    if asset_path.startswith("assets/"):
        possible_paths.append(project_root / asset_path)
    elif "/" in asset_path:
        # Might be a partial path
        parts = asset_path.split("/")
        if parts[0] in ["images", "audio", "fonts"]:
            possible_paths.append(project_root / "assets" / asset_path)
    
    for path in possible_paths:
        if path.exists():
            return True, path
            
    return False, Path(asset_path)

def audit_assets():
    """Run the asset audit and print results."""
    project_root = Path(__file__).parent.parent
    
    print("Auditing asset references in codebase...\n")
    
    # Find all references
    references = find_asset_references(project_root)
    
    # Check each reference
    missing_assets = {'images': [], 'audio': [], 'fonts': []}
    found_assets = {'images': [], 'audio': [], 'fonts': []}
    
    for asset_type, refs in references.items():
        print(f"\nChecking {asset_type.upper()} assets...")
        print(f"Found {len(refs)} references")
        
        # Remove duplicates while preserving first occurrence info
        unique_refs = {}
        for file_path, line_num, asset_path in refs:
            if asset_path not in unique_refs:
                unique_refs[asset_path] = (file_path, line_num)
        
        for asset_path, (file_path, line_num) in unique_refs.items():
            exists, full_path = check_asset_exists(project_root, asset_path)
            
            if exists:
                found_assets[asset_type].append((asset_path, full_path))
            else:
                missing_assets[asset_type].append((asset_path, file_path, line_num))
    
    # Print results
    print("\n" + "="*60)
    print("AUDIT RESULTS")
    print("="*60)
    
    # Missing assets
    total_missing = sum(len(items) for items in missing_assets.values())
    if total_missing > 0:
        print(f"\nMISSING ASSETS ({total_missing} total)")
        print("-"*60)
        
        for asset_type, items in missing_assets.items():
            if items:
                print(f"\n{asset_type.upper()} ({len(items)} missing):")
                for asset_path, source_file, line_num in sorted(items):
                    rel_source = Path(source_file).relative_to(project_root)
                    print(f"  - {asset_path}")
                    print(f"    Referenced in: {rel_source}:{line_num}")
    else:
        print("\nAll referenced assets found!")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for asset_type in ['images', 'audio', 'fonts']:
        total = len(found_assets[asset_type]) + len(missing_assets[asset_type])
        found = len(found_assets[asset_type])
        missing = len(missing_assets[asset_type])
        
        if total > 0:
            percentage = (found / total) * 100
            print(f"{asset_type.capitalize()}: {found}/{total} found ({percentage:.1f}%)")
    
    # Specific warnings
    if any("voice" in str(path).lower() for paths in missing_assets['audio'] for path in paths):
        print("\nWARNING: Voice description files detected in audio assets!")
        print("   These should be replaced with actual sound effects.")
    
    print("\nAudit complete!")

if __name__ == "__main__":
    audit_assets()