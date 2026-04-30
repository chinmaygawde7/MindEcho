import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY                   = os.environ["FLASK_SECRET_KEY"]
    SESSION_TYPE                 = "filesystem"
    SESSION_FILE_DIR             = "flask_session"
    SESSION_PERMANENT            = True
    PERMANENT_SESSION_LIFETIME   = timedelta(days=1)
    SESSION_REFRESH_EACH_REQUEST = True

    SUPABASE_URL              = os.environ["SUPABASE_URL"]
    SUPABASE_ANON_KEY         = os.environ["SUPABASE_ANON_KEY"]
    SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

    ELEVENLABS_API_KEY        = os.environ["ELEVENLABS_API_KEY"]
    ANTHROPIC_API_KEY         = os.environ["ANTHROPIC_API_KEY"]
    RESEND_API_KEY            = os.environ["RESEND_API_KEY"]
    APP_URL                   = os.environ.get("APP_URL", "http://localhost:5000")


class ProductionConfig(Config):
    SESSION_TYPE = "signed_cookie"   # no filesystem needed — stored in browser cookie