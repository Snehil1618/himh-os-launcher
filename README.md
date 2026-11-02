# HimH OS Public Launcher (Streamlit Community Cloud Wrapper)

This is a lightweight public bootstrap repo for hosting **HimH OS** on **Streamlit Community Cloud (share.streamlit.io)** without exposing your private intellectual property or consuming your private repository quota.

---

## 🛠️ Setup Instructions (2 Minutes)

### Step 1: Create the Empty Public Repo on GitHub
1. Create a new repository on your GitHub account: `himh-os-launcher`
2. Set visibility to **Public**
3. Push only the 2 files from this directory:
   - `streamlit_app.py`
   - `requirements.txt`

### Step 2: Generate a GitHub Read-Only Personal Access Token (PAT)
1. In your GitHub account, go to **Settings → Developer Settings → Personal Access Tokens → Fine-grained tokens** (or Tokens Classic).
2. Click **Generate new token**:
   - **Token Name:** `streamlit-cloud-himh-launcher`
   - **Repository Access:** Selected repositories → Choose your private repo (e.g. `himh-os-private`)
   - **Permissions:** Repository permissions → **Contents: Read-only**
3. Copy the generated token (`github_pat_...`).

### Step 3: Deploy on Streamlit Community Cloud
1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Click **New App**:
   - **Repository:** `<your-username>/himh-os-launcher`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app.py`
3. Click **Advanced Settings → Secrets** and paste:

```toml
# Private Core Git Access
GITHUB_READ_TOKEN = "github_pat_..."
PRIVATE_REPO_URL = "github.com/<your-username>/himh-os-private.git"

# HimH OS Configuration
DEFAULT_PROPERTY_ID = "a0000000-0000-0000-0000-000000000001"
OWNER_PIN = "1234"
PROPERTY_GSTIN = "02AAACH1234F1Z5"
TAX_RATE_ACCOMMODATION = "0.0"
TAX_RATE_CAFE = "5.0"
TAX_RATE_ACTIVITY = "0.0"

# Supabase Credentials (Optional for sandbox, required for cloud persistence)
SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-supabase-key"

# AI & Telegram
GEMINI_API_KEY = "your-gemini-api-key"
TELEGRAM_BOT_TOKEN = "your-telegram-bot-token"
```

4. Click **Save** and **Deploy**!
