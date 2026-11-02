import os
import sys
import subprocess
import runpy
import streamlit as st

# -----------------------------------------------------------------------------
# 1. Bridge Streamlit Cloud Secrets into Environment Variables
# -----------------------------------------------------------------------------
# Ensures all os.getenv() calls across backend & UI work seamlessly
for key, val in st.secrets.items():
    if isinstance(val, (str, int, float, bool)) and key not in os.environ:
        os.environ[key] = str(val)

# -----------------------------------------------------------------------------
# 2. Clone or Update Private Core Repository
# -----------------------------------------------------------------------------
CORE_DIR = os.path.abspath("private_core")

if not os.path.exists(CORE_DIR):
    token = st.secrets.get("GITHUB_READ_TOKEN")
    repo = st.secrets.get("PRIVATE_REPO_URL", "")

    if not token or not repo:
        st.error("Missing required secrets: 'GITHUB_READ_TOKEN' and 'PRIVATE_REPO_URL' must be configured in Streamlit Cloud Secrets.")
        st.stop()

    clean_repo = repo.replace("https://", "").replace("http://", "").rstrip("/")
    clone_url = f"https://{token}@{clean_repo}"

    with st.spinner("Connecting to secure private core..."):
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", clone_url, CORE_DIR],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as err:
            st.error(f"Failed to fetch private repository: {err.stderr}")
            st.stop()

# -----------------------------------------------------------------------------
# 3. Mount Private Core & Execute HimH OS
# -----------------------------------------------------------------------------
if CORE_DIR not in sys.path:
    sys.path.insert(0, CORE_DIR)

os.chdir(CORE_DIR)

# Use runpy.run_path so Streamlit reactive re-runs execute cleanly on every click
app_entrypoint = os.path.join(CORE_DIR, "ui", "app.py")
runpy.run_path(app_entrypoint, run_name="__main__")
