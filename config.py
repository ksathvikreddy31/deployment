import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")

    # Database credentials from environment variables
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_USER = os.getenv("MYSQL_USER")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
    MYSQL_DB = os.getenv("MYSQL_DB")

    # Updated URI with SSL bypass parameters
    # This allows the connection to work without needing the Baltimore certificate file
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DB}"
        "?ssl_verify_cert=false&ssl_verify_identity=false"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False