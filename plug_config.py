import os
from pathlib import Path

import environ

from plugs.manager import PlugManager
from plugs.plug import Plug

# Load .env file before reading environment variables
# This ensures plugin configs can access .env values
env_file = Path(__file__).resolve().parent / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)

# Care Scribe Plugin - Local Development
scribe_plug = Plug(
    name="care_scribe",
    package_name="/Users/jagankumar/Office/Work/repo/Care Platform/Carecare_scribe",
    version="",  # Empty for local path
    configs={
        "SCRIBE_API_PROVIDER": os.environ.get("SCRIBE_API_PROVIDER", "openai"),
        "SCRIBE_CHAT_MODEL_NAME": os.environ.get("SCRIBE_CHAT_MODEL_NAME", "gpt-4o"),
        "SCRIBE_AUDIO_MODEL_NAME": os.environ.get("SCRIBE_AUDIO_MODEL_NAME", "whisper-1"),
        "SCRIBE_OPENAI_API_KEY": os.environ.get("SCRIBE_OPENAI_API_KEY", ""),
        "SCRIBE_TNC": os.environ.get(
            "SCRIBE_TNC",
            "<p>By using Care Scribe, you agree to have your audio transcribed by AI services.</p>",
        ),
        # Azure configs (if using azure provider)
        "SCRIBE_AZURE_API_VERSION": os.environ.get("SCRIBE_AZURE_API_VERSION", ""),
        "SCRIBE_AZURE_ENDPOINT": os.environ.get("SCRIBE_AZURE_ENDPOINT", ""),
        "SCRIBE_AZURE_API_KEY": os.environ.get("SCRIBE_AZURE_API_KEY", ""),
        # Google configs (if using google provider)
        "SCRIBE_GOOGLE_PROJECT_ID": os.environ.get("SCRIBE_GOOGLE_PROJECT_ID", ""),
        "SCRIBE_GOOGLE_LOCATION": os.environ.get("SCRIBE_GOOGLE_LOCATION", "us-central1"),
    },
)





# Care Scribe Plugin - Local Development
scribe_auto = Plug(
    # /Users/jagankumar/Office/Work/repo/care_task_plugin/care_auto_assign
    name="care_auto_assign",
    package_name="/Users/jagankumar/Office/Work/repo/Care Platform/care_auto_assign/care_auto_assign",
    version="",  # Empty for local path
    configs={
        "SERVICE_API_KEY": "my_api_key",

    },
)

plugs = [scribe_plug,scribe_auto]

manager = PlugManager(plugs)
