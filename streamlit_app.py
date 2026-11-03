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
    if isinstance(val, (str, int, float, bool)) and key not in os.environ:
        os.environ[key] = str(val)

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

    # Use x-access-token to supply both username and password non-interactively
    clone_url = f"https://x-access-token:{token_clean}@{clean_repo}"

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
        # If directory exists but has no valid .git (e.g. aborted clone), remove it
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
            safe_err = err.stderr.replace(token_clean, "[TOKEN_REDACTED]") if token_clean else err.stderr
            st.error(f"Git Clone Failed: {safe_err}")
            st.info("Check that GITHUB_READ_TOKEN has repo read permissions and PRIVATE_REPO_URL is 'github.com/Snehil1618/himh-os-private.git'")
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
