from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
import urllib.parse
import time
import sys

app = Flask(__name__)

# STARTUP LOG - This MUST show up in 'az container logs'
print("--- APPLICATION INITIALIZING ---", flush=True)

# ------------------ CONFIGURATION ------------------
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "supersecret")

user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD') 
host = os.getenv('MYSQL_HOST')
database = os.getenv('MYSQL_DB')

print(f"DEBUG: Attempting to connect as user: {user} to host: {host}", flush=True)

# THE CRITICAL FIX for 'Bunny@123'
if password:
    safe_password = urllib.parse.quote_plus(password)
    print("DEBUG: Password successfully encoded.", flush=True)
else:
    safe_password = ""
    print("DEBUG: WARNING - No password found in environment variables!", flush=True)

app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{user}:{safe_password}@{host}/{database}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ------------------ MODEL ------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# ------------------ ROUTES ------------------
@app.route('/')
def home():
    return "App is Running!"

# ------------------ MAIN ------------------
if __name__ == "__main__":
    print("--- AZURE STARTUP ---", flush=True)
    connected = False
    retry_count = 0
    
    while not connected and retry_count < 10:
        try:
            print(f"Connection Attempt {retry_count + 1}...", flush=True)
            with app.app_context():
                db.create_all() 
            connected = True
            print("SUCCESS: Connected to Azure MySQL!", flush=True)
        except Exception as e:
            retry_count += 1
            print(f"ERROR: Database not ready. Reason: {e}", flush=True)
            time.sleep(5)
    
    if connected:
        print("Starting Flask server on port 5000...", flush=True)
        app.run(host="0.0.0.0", port=5000)
    else:
        print("FATAL: Could not connect to DB after 10 attempts. Shutting down.", flush=True)
        sys.exit(1)