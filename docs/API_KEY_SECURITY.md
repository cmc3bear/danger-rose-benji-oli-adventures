# API Key Security Guide

## Overview

This document explains how API keys are securely managed in the Danger Rose project. We use a vault system to ensure API keys are NEVER exposed in the codebase or git history.

## Vault System Location

All API keys are stored in:
```
C:\dev\api-key-forge\vault\
```

This directory is **OUTSIDE** the game repository to prevent accidental commits.

## Supported API Keys

### OpenAI (DALL-E)
- **Location**: `C:\dev\api-key-forge\vault\OPENAI\`
- **Filenames**: `api_key.txt` or `key_*.txt`
- **Usage**: Character sprite generation

### 11labs
- **Location**: `C:\dev\api-key-forge\vault\11LABS\`
- **Filename**: `API-KEY.txt`
- **Usage**: Sound effect generation

### GitHub
- **Location**: `C:\dev\api-key-forge\vault\GITHUB\`
- **Filename**: `api_key.txt`
- **Usage**: Repository operations

### Suno
- **Location**: `C:\dev\api-key-forge\vault\SUNO\`
- **Filename**: `api_key.txt`
- **Usage**: Music generation

## Using API Keys in Code

### Python Scripts

Always use the `vault_utils.py` module:

```python
from scripts.vault_utils import get_api_key

# Get OpenAI key
api_key = get_api_key("OPENAI")

# Initialize client
client = OpenAI(api_key=api_key)
```

### Never Do This:

```python
# WRONG - Never hardcode keys
api_key = "sk-abc123..."

# WRONG - Never read directly
with open("my_api_key.txt") as f:
    api_key = f.read()
```

## Security Checklist

### Before Committing:
1. ✅ Never store API keys in the repository
2. ✅ Always use `vault_utils.py` for key access
3. ✅ Check git status for accidental key files
4. ✅ Ensure `.gitignore` excludes key patterns

### Git Safety:
- `.gitignore` includes patterns for common key files
- Vault directory is outside repository
- All scripts use relative paths to vault

## Vault Structure

```
C:\dev\api-key-forge\vault\
├── OPENAI\
│   └── key_*.txt  (or api_key.txt)
├── 11LABS\
│   └── API-KEY.txt
├── GITHUB\
│   └── api_key.txt
└── SUNO\
    └── api_key.txt
```

## Testing Key Access

Run this command to verify vault setup:
```bash
python scripts/vault_utils.py
```

This will check:
- Vault directory exists
- Available keys are found
- Security configuration is correct

## Adding New API Keys

1. Create directory in vault: `C:\dev\api-key-forge\vault\SERVICE_NAME\`
2. Add key file: `api_key.txt`
3. Update `vault_utils.py` if needed
4. Test access before use

## Emergency Response

If an API key is accidentally exposed:

1. **Immediately revoke** the exposed key
2. **Generate new key** from the service
3. **Update vault** with new key
4. **Check git history** for other exposures
5. **Run security audit** on recent commits

## Best Practices

1. **Environment Variables**: Can use as fallback
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

2. **Key Rotation**: Regularly update API keys
3. **Access Logs**: Monitor API usage for anomalies
4. **Minimal Permissions**: Use keys with limited scope

## Common Issues

### "API key not found"
- Check vault directory exists
- Verify filename matches expected pattern
- Ensure file contains valid key

### "Permission denied"
- Check file permissions on vault
- Run as appropriate user

### "Invalid API key"
- Verify key is active on service
- Check for extra whitespace in file
- Ensure key hasn't expired

---

Remember: **NEVER commit API keys to git!** Always use the vault system.