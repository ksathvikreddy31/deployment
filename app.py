from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
import urllib.parse
import time

app = Flask(__name__)

# ------------------ CONFIGURATION ------------------

# Secret key for session management
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "supersecret")

# Fetch environment variables from Azure
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD') # Bunny@123
host = os.getenv('MYSQL_HOST')
database = os.getenv('MYSQL_DB')

# Professional Step: Encode the password
# This converts 'Bunny@123' to 'Bunny%40123' so the URI doesn't break
safe_password = urllib.parse.quote_plus(password) if password else ""

# Build the final connection URI
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{user}:{safe_password}@{host}/{database}"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ------------------ MODEL ------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# ------------------ ROUTES ------------------

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'])
        new_user = User(username=request.form['username'], password=hashed_pw)
        try:
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            return f"Error during registration: {str(e)}"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            return "Login Successful! Welcome to your Azure App."
        return "Invalid Credentials"
    return render_template('login.html')

# ------------------ MAIN ------------------

if __name__ == "__main__":
    # Professional Step: Database Connection Retry Loop
    # This keeps the container alive while waiting for Azure MySQL to be ready
    connected = False
    while not connected:
        try:
            with app.app_context():
                # Ensures the 'User' table exists in Azure MySQL
                db.create_all() 
            connected = True
            print("Successfully connected to Azure MySQL!")
        except Exception as e:
            # Logs the error and waits 5 seconds before retrying
            print(f"Database handshake failed... retrying in 5 seconds. Error: {e}")
            time.sleep(5)
    
    # Run the Flask server on port 5000
    app.run(host="0.0.0.0", port=5000)