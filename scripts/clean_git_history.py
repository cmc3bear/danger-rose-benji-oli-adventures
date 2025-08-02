#!/usr/bin/env python3
"""Script to clean sensitive data from git history."""

import subprocess
import os
import sys

def run_command(cmd):
    """Run a shell command and return output."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {cmd}")
        print(f"Error: {result.stderr}")
    return result.returncode == 0

def clean_git_history():
    """Clean sensitive data from git history."""
    print("Cleaning git history of sensitive data...")
    
    # List of patterns to remove
    sensitive_patterns = [
        # API key patterns
        '*api_key*',
        '*API_KEY*',
        '*apikey*',
        '*APIKEY*',
        # Specific files that might contain keys
        'src/scenes/drive.py',  # Had hardcoded keys
        'scripts/generate_traffic_sprites.py',  # Had hardcoded keys
        'scripts/generate_water_sprites.py',  # Had hardcoded keys
    ]
    
    # Create a backup branch
    print("Creating backup branch...")
    run_command("git branch backup-before-clean")
    
    # Use git filter-branch to remove sensitive data
    for pattern in sensitive_patterns:
        print(f"Removing pattern: {pattern}")
        # Remove files matching pattern
        cmd = f'git filter-branch -f --index-filter "git rm -rf --cached --ignore-unmatch {pattern}" HEAD'
        run_command(cmd)
    
    # Clean up refs
    print("Cleaning up refs...")
    run_command("git for-each-ref --format='delete %(refname)' refs/original | git update-ref --stdin")
    run_command("git reflog expire --expire=now --all")
    run_command("git gc --prune=now --aggressive")
    
    print("Git history cleaned!")
    print("\nNext steps:")
    print("1. Review the changes with: git log --oneline")
    print("2. Force push to remote: git push --force origin clean-v0.1.3-release")
    print("3. All collaborators must re-clone the repository")

if __name__ == "__main__":
    # Confirm with user
    response = input("This will rewrite git history. Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        sys.exit(0)
    
    clean_git_history()