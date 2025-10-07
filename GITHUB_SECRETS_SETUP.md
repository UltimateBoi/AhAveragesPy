# GitHub Secrets Setup Guide

This guide walks you through setting up GitHub Secrets for this repository to securely manage API keys and environment variables.

## Why GitHub Secrets?

GitHub Secrets allow you to:
- ✅ Store sensitive information securely (encrypted at rest)
- ✅ Inject environment variables during CI/CD workflows
- ✅ Prevent accidental exposure in logs or code
- ✅ Control access (only admins can view/edit)

## Step-by-Step Setup

### 1. Navigate to Repository Settings

1. Go to your repository on GitHub: https://github.com/UltimateBoi/AhAveragesPy
2. Click on **Settings** tab (you need admin access)
3. In the left sidebar, find **Secrets and variables** section
4. Click **Actions**

### 2. Add Required Secrets

Click **New repository secret** and add each of the following:

#### Required Secrets

| Secret Name | Value | Description |
|------------|-------|-------------|
| `HYPIXEL_API_URL` | `https://api.hypixel.net/skyblock/auctions_ended` | Hypixel API endpoint for auction data |

#### Optional Secrets

| Secret Name | Example Value | Description |
|------------|---------------|-------------|
| `HYPIXEL_API_KEY` | `your-api-key-here` | API key if Hypixel requires authentication (currently not needed) |

#### Firebase Secrets (If Adding Firebase)

If you plan to integrate Firebase in the future:

| Secret Name | Example | Description |
|------------|---------|-------------|
| `FIREBASE_API_KEY` | `AIzaSyXXXXXXXXXXXXXXXXXXXXX` | Firebase Web API Key |
| `FIREBASE_AUTH_DOMAIN` | `your-project.firebaseapp.com` | Firebase Auth Domain |
| `FIREBASE_PROJECT_ID` | `your-project-id` | Firebase Project ID |
| `FIREBASE_STORAGE_BUCKET` | `your-project.appspot.com` | Firebase Storage Bucket |
| `FIREBASE_MESSAGING_SENDER_ID` | `123456789012` | Firebase Messaging Sender ID |
| `FIREBASE_APP_ID` | `1:123456789012:web:abcdef` | Firebase App ID |

### 3. How to Add a Secret

For each secret:

1. Click **New repository secret**
2. Enter the **Name** exactly as shown in the table (case-sensitive!)
3. Enter the **Value** (this will be encrypted)
4. Click **Add secret**

### 4. Verify Secrets Are Added

After adding all secrets:
1. You should see them listed (values will be hidden)
2. You cannot view secret values after creation (only update or delete)

## Testing Your Setup

### Test Locally

1. Create a `.env` file (not committed):
   ```bash
   cp .env.example .env
   nano .env
   ```

2. Add your configuration:
   ```env
   HYPIXEL_API_URL=https://api.hypixel.net/skyblock/auctions_ended
   ```

3. Run the test scripts:
   ```bash
   python test_config.py
   python verify_security.py
   ```

4. Run the main application:
   ```bash
   python __main__.py
   ```

### Test on GitHub Actions

1. Go to **Actions** tab in your repository
2. Find the **Run Main Script** workflow
3. Click **Run workflow** → **Run workflow** (manual trigger)
4. Watch the workflow run
5. Check logs to ensure:
   - No secrets are printed (they should be masked)
   - API calls succeed
   - Data is processed correctly

## Security Best Practices

### ✅ DO:
- Use GitHub Secrets for all sensitive data
- Rotate keys regularly (update secrets periodically)
- Use `.env` for local development (it's gitignored)
- Run security checks: `python verify_security.py`
- Monitor workflow logs for suspicious activity

### ❌ DON'T:
- Never commit `.env` files to the repository
- Never hardcode API keys in source code
- Never print/log secret values
- Never share secret values in issues or PRs
- Never commit API keys even in private repositories

## Troubleshooting

### "Configuration error: HYPIXEL_API_URL must be set"

**Cause:** Environment variable not set

**Solutions:**
- For local development: Create `.env` file with the variable
- For GitHub Actions: Add `HYPIXEL_API_URL` secret in repository settings
- Check secret name matches exactly (case-sensitive)

### Workflow fails with authentication error

**Cause:** Invalid or missing API key

**Solutions:**
- Verify the API key is correct
- Check if the API endpoint has changed
- Ensure secret name matches what the workflow expects

### Secrets not being injected into workflow

**Cause:** Workflow not configured correctly or secret name mismatch

**Solutions:**
- Check `.github/workflows/run_main.yml` has `env:` section
- Verify secret names in workflow match repository secrets exactly
- Ensure workflow has permission to access secrets

### "No hardcoded API keys detected" test fails

**Cause:** API keys or URLs are hardcoded in source files

**Solutions:**
- Use `config.HYPIXEL_API_URL` instead of hardcoded URLs
- Move all sensitive data to environment variables
- Run `python verify_security.py` to identify issues

## Advanced: Using Environment Variables in Code

### Python

```python
import config

# Access environment variables through config module
api_url = config.HYPIXEL_API_URL
api_key = config.HYPIXEL_API_KEY

# Make API request
async with session.get(api_url, headers={'API-Key': api_key}) as response:
    data = await response.json()
```

### In GitHub Actions Workflow

```yaml
- name: Run script with secrets
  env:
    HYPIXEL_API_URL: ${{ secrets.HYPIXEL_API_URL }}
    HYPIXEL_API_KEY: ${{ secrets.HYPIXEL_API_KEY }}
  run: |
    python __main__.py
```

### Providing Default Values

```yaml
env:
  # Use secret if available, otherwise use default
  HYPIXEL_API_URL: ${{ secrets.HYPIXEL_API_URL || 'https://api.hypixel.net/skyblock/auctions_ended' }}
```

## Monitoring & Maintenance

### Regular Checks

1. **Monthly:** Review access logs in GitHub
2. **Quarterly:** Rotate API keys
3. **After team changes:** Audit who has access to secrets
4. **Before releases:** Run `python verify_security.py`

### Security Audit Checklist

- [ ] All secrets are stored in GitHub Secrets (not in code)
- [ ] `.env` files are in `.gitignore`
- [ ] No `.env` files in git history
- [ ] All tests pass: `python test_config.py`
- [ ] Security verification passes: `python verify_security.py`
- [ ] Workflow logs don't expose secrets
- [ ] Firebase Security Rules configured (if using Firebase)

## Getting Help

If you encounter issues:

1. Run diagnostics:
   ```bash
   python test_config.py
   python verify_security.py
   ```

2. Check documentation:
   - [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) - Detailed setup guide
   - [README.md](README.md) - Quick start guide

3. Review GitHub Actions logs for specific errors

4. Ensure you're using the latest version of the repository

---

**Last Updated:** January 2025

**Related Documentation:**
- [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md) - Full environment variable guide
- [README.md](README.md) - Repository overview
