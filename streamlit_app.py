import os
import sys
import subprocess
import shutil
import runpy
import streamlit as st

# -----------------------------------------------------------------------------
# 1. Bridge Streamlit Cloud Secrets into Environment Variables
# -----------------------------------------------------------------------------
for key, val in st.secrets.items():
    if isinstance(val, (str, int, float, bool)):
        str_val = str(val).strip()
        os.environ[key] = str_val
        os.environ[key.upper()] = str_val

LAUNCHER_ROOT = os.path.dirname(os.path.abspath(__file__))
CORE_DIR = os.path.join(LAUNCHER_ROOT, "private_core")

# -----------------------------------------------------------------------------
# 2. Cached Git Sync Function (Clones or Pulls Latest Build)
# -----------------------------------------------------------------------------
@st.cache_resource
def sync_private_core(repo_url: str, token: str) -> bool:
    token_clean = str(token).strip().strip("'\"")
    clean_repo = str(repo_url).strip().strip("'\"")

    for p in ("https://", "http://"):
        if clean_repo.startswith(p):
            clean_repo = clean_repo[len(p):]
    clean_repo = clean_repo.rstrip("/")
    if not clean_repo.endswith(".git"):
        clean_repo += ".git"

    # Extract GitHub username from repo URL (e.g. github.com/Snehil1618/himh-os-private.git -> Snehil1618)
    parts = clean_repo.split("/")
    if len(parts) >= 3 and "github.com" in parts[0]:
        user = parts[1]
    elif len(parts) == 2:
        user = parts[0]
        clean_repo = f"github.com/{clean_repo}"
    else:
        user = "oauth2"

    # Use https://USERNAME:TOKEN@github.com/... (Standard GitHub HTTPS auth)
    clone_url = f"https://{user}:{token_clean}@{clean_repo}"

    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"

    is_valid_git_repo = os.path.isdir(CORE_DIR) and os.path.isdir(os.path.join(CORE_DIR, ".git"))

    if is_valid_git_repo:
        try:
            subprocess.run(
                ["git", "-C", CORE_DIR, "pull", "--ff-only"],
                check=True,
                capture_output=True,
                text=True,
                env=env
            )
        except subprocess.CalledProcessError as err:
            st.warning(f"Git pull notice: {err.stderr}")
    else:
        # If directory exists but has no valid .git, clean it before cloning
        if os.path.exists(CORE_DIR):
            shutil.rmtree(CORE_DIR, ignore_errors=True)

        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", clone_url, CORE_DIR],
                check=True,
                capture_output=True,
                text=True,
                env=env
            )
        except subprocess.CalledProcessError as err:
            # Fallback attempt: try cloning with token directly if username:token failed
            fallback_url = f"https://{token_clean}@{clean_repo}"
            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", fallback_url, CORE_DIR],
                    check=True,
                    capture_output=True,
                    text=True,
                    env=env
                )
            except subprocess.CalledProcessError as fallback_err:
                safe_err = fallback_err.stderr.replace(token_clean, "[TOKEN_REDACTED]") if token_clean else fallback_err.stderr
                st.error(f"Git Clone Failed: {safe_err}")
                st.markdown(f"""
                **Troubleshooting Authentication:**
                - Target Repository: `{clean_repo}`
                - Authenticated User: `{user}`
                - Token format detected: `{token_clean[:4]}...` (Length: {len(token_clean)} chars)
                
                Please ensure your token was generated at [github.com/settings/tokens](https://github.com/settings/tokens) with the **`repo`** scope checked, and that your Streamlit Cloud secret is saved as:
                ```toml
                GITHUB_READ_TOKEN = "ghp_..."
                PRIVATE_REPO_URL = "github.com/{user}/himh-os-private.git"
                ```
                """)
                st.stop()

    return True

token = st.secrets.get("GITHUB_READ_TOKEN")
repo = st.secrets.get("PRIVATE_REPO_URL", "")

if not token or not repo:
    st.error("Missing required secrets: 'GITHUB_READ_TOKEN' and 'PRIVATE_REPO_URL' must be configured in Streamlit Cloud Secrets.")
    st.stop()

with st.spinner("Connecting to secure private core..."):
    sync_private_core(repo, token)

# -----------------------------------------------------------------------------
# 3. Mount Private Core & Execute HimH OS
# -----------------------------------------------------------------------------
if CORE_DIR not in sys.path:
    sys.path.insert(0, CORE_DIR)

os.chdir(CORE_DIR)

# Execute ui/app.py using runpy.run_path to avoid sys.modules import caching on widget clicks
runpy.run_path(os.path.join(CORE_DIR, "ui", "app.py"), run_name="__main__")
