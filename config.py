import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")

    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB = os.getenv("MYSQL_DB")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
        f"@{MYSQL_HOST}/{MYSQL_DB}"
    )

    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            "ssl": {"ssl_disabled": False}
        }
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False