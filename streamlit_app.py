import os
import sys
import subprocess
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
    clean_repo = repo_url.replace("https://", "").replace("http://", "").rstrip("/")
    clone_url = f"https://{token}@{clean_repo}"

    if os.path.exists(CORE_DIR):
        try:
            subprocess.run(
                ["git", "-C", "private_core", "pull", "--ff-only"],
                check=True,
                capture_output=True,
                text=True
            )
        except Exception as err:
            st.warning(f"Git pull notice: {err}")
    else:
        subprocess.run(
            ["git", "clone", "--depth", "1", clone_url, CORE_DIR],
            check=True,
            capture_output=True,
            text=True
        )
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
