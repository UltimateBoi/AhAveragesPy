# Environment Variables & API Key Protection Guide

## Overview
This repository now uses environment variables to securely manage API keys and configuration. This prevents sensitive information from being committed to the repository and exposed in the codebase.

## Important Security Information

### Current API Usage
This project uses the **Hypixel API** to fetch Skyblock auction data. The Hypixel API endpoint used (`/skyblock/auctions_ended`) is a public endpoint that typically doesn't require authentication. However, this setup allows you to:
- Add API keys if Hypixel requires them in the future
- Easily switch between different API endpoints
- Add other APIs (like Firebase) without exposing credentials

### Firebase (Optional)
If you plan to add Firebase to this project in the future, the configuration structure is already in place. See the "Adding Firebase" section below.

## Setup Instructions

### For Local Development

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit the .env file with your configuration:**
   ```bash
   # The .env file is already in .gitignore and will NOT be committed
   nano .env
   ```

3. **Set your API configuration:**
   ```env
   HYPIXEL_API_URL=https://api.hypixel.net/skyblock/auctions_ended
   HYPIXEL_API_KEY=your-api-key-if-needed
   ```

4. **Run the application:**
   ```bash
   python __main__.py
   ```

The application will automatically load the `.env` file and use your configuration.

### For GitHub Actions (Production)

Environment variables are injected via GitHub Secrets during CI/CD workflows. Here's how to set them up:

#### Step 1: Add Secrets to GitHub Repository

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

   | Secret Name | Value | Required |
   |------------|-------|----------|
   | `HYPIXEL_API_URL` | `https://api.hypixel.net/skyblock/auctions_ended` | No (has default) |
   | `HYPIXEL_API_KEY` | Your API key (if needed) | No (currently not required) |

#### Step 2: Secrets Are Already Configured in Workflows

The GitHub Actions workflow (`.github/workflows/run_main.yml`) is already configured to use these secrets:

```yaml
- name: Run main script
  env:
    HYPIXEL_API_URL: ${{ secrets.HYPIXEL_API_URL || 'https://api.hypixel.net/skyblock/auctions_ended' }}
    HYPIXEL_API_KEY: ${{ secrets.HYPIXEL_API_KEY }}
  run: |
    python __main__.py
```

The configuration uses fallback values, so if secrets aren't set, the defaults will be used.

## How It Works

### Architecture

1. **config.py** - Central configuration module that:
   - Loads environment variables from `.env` file (local development)
   - Reads environment variables from the system (GitHub Actions)
   - Provides sensible defaults
   - Validates configuration

2. **__main__.py** - Main application imports and uses the config:
   ```python
   import config
   
   # Uses config.HYPIXEL_API_URL instead of hardcoded URL
   async with session.get(config.HYPIXEL_API_URL, headers=headers) as response:
       ...
   ```

3. **.env** (local only, not committed):
   - Contains your actual secrets
   - Automatically loaded by config.py
   - Protected by .gitignore

4. **.env.example** (committed):
   - Template showing what variables are needed
   - No actual secrets
   - Serves as documentation

### Security Features

✅ **Environment variables never appear in code**
- All sensitive data loaded from environment
- No hardcoded API keys or URLs in source files

✅ **.env files are gitignored**
- Multiple patterns in .gitignore: `.env`, `.env.local`, `.env*.local`, `*.env`
- Impossible to accidentally commit secrets

✅ **GitHub Secrets are encrypted**
- Secrets stored in GitHub are encrypted at rest
- Only visible to repository administrators
- Injected at runtime during workflows

✅ **Defaults for non-sensitive values**
- Public API URLs can have defaults
- Application works even without secrets set

## Adding Firebase (Optional)

If you want to add Firebase to your project:

### Step 1: Update your .env file

```env
FIREBASE_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=123456789012
FIREBASE_APP_ID=1:123456789012:web:abcdef123456
```

### Step 2: Add Firebase secrets to GitHub

Add these secrets in GitHub: **Settings** → **Secrets and variables** → **Actions**:
- `FIREBASE_API_KEY`
- `FIREBASE_AUTH_DOMAIN`
- `FIREBASE_PROJECT_ID`
- `FIREBASE_STORAGE_BUCKET`
- `FIREBASE_MESSAGING_SENDER_ID`
- `FIREBASE_APP_ID`

### Step 3: Update workflows to pass Firebase secrets

Edit `.github/workflows/run_main.yml` to include Firebase environment variables:

```yaml
- name: Run main script
  env:
    HYPIXEL_API_URL: ${{ secrets.HYPIXEL_API_URL || 'https://api.hypixel.net/skyblock/auctions_ended' }}
    HYPIXEL_API_KEY: ${{ secrets.HYPIXEL_API_KEY }}
    FIREBASE_API_KEY: ${{ secrets.FIREBASE_API_KEY }}
    FIREBASE_AUTH_DOMAIN: ${{ secrets.FIREBASE_AUTH_DOMAIN }}
    FIREBASE_PROJECT_ID: ${{ secrets.FIREBASE_PROJECT_ID }}
    FIREBASE_STORAGE_BUCKET: ${{ secrets.FIREBASE_STORAGE_BUCKET }}
    FIREBASE_MESSAGING_SENDER_ID: ${{ secrets.FIREBASE_MESSAGING_SENDER_ID }}
    FIREBASE_APP_ID: ${{ secrets.FIREBASE_APP_ID }}
  run: |
    python __main__.py
```

### Step 4: Use Firebase in your code

```python
import config

# Get Firebase configuration
firebase_config = config.get_firebase_config()

# Initialize Firebase (you'll need to install firebase-admin)
import firebase_admin
from firebase_admin import credentials, firestore

# Use the configuration...
```

## Verification

### Verify Secrets Are Protected

1. **Check .gitignore:**
   ```bash
   cat .gitignore | grep -i env
   ```
   Should show: `.env`, `.env.local`, `.env*.local`, `*.env`

2. **Verify .env is not tracked:**
   ```bash
   git status
   ```
   Your `.env` file should NOT appear in untracked files if you created it

3. **Check workflow configuration:**
   ```bash
   cat .github/workflows/run_main.yml
   ```
   Should show environment variables being injected from secrets

### Test Locally

1. Create `.env` with test values:
   ```env
   HYPIXEL_API_URL=https://api.hypixel.net/skyblock/auctions_ended
   ```

2. Run the application:
   ```bash
   python __main__.py
   ```

3. Check output - should show:
   ```
   Starting...
   Using API URL: https://api.hypixel.net/skyblock/auctions_ended
   Getting auctions...
   ```

## Troubleshooting

### "Configuration error: HYPIXEL_API_URL must be set"
- **Cause:** Environment variable not set
- **Solution:** Create `.env` file with `HYPIXEL_API_URL` or set it in your environment

### Secrets not working in GitHub Actions
- **Check:** Ensure secrets are added in repository Settings → Secrets
- **Check:** Secret names match exactly (case-sensitive)
- **Check:** Workflow has permission to access secrets

### .env file being tracked by git
- **Solution:** Run `git rm --cached .env` to remove it from tracking
- **Verify:** `.env` is in `.gitignore`

## Best Practices

1. **Never commit secrets:** Always use environment variables or secrets
2. **Use .env.example:** Document required environment variables
3. **Rotate keys regularly:** Update GitHub Secrets if keys are compromised
4. **Minimal permissions:** Only grant necessary API permissions
5. **Monitor usage:** Check API usage to detect unauthorized access

## Additional Security for Production

For Firebase specifically (when you add it):

1. **Enable Firebase App Check** - Prevents unauthorized clients
2. **Configure Firebase Security Rules** - Control data access
3. **Restrict Authorized Domains** - Only allow your GitHub Pages domain
4. **Enable authentication** - Require user login for sensitive operations
5. **Monitor Firebase Console** - Watch for unusual activity

## Need Help?

- Check that `.env.example` is properly configured
- Verify all required secrets are set in GitHub
- Review workflow logs for environment variable issues
- Ensure `config.py` is being imported correctly

---

**Remember:** The goal is not just to hide API keys, but to implement proper security practices including access controls, monitoring, and regular key rotation.
