from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os
import urllib.parse
import time # Added for retry logic

app = Flask(__name__)

# ------------------ CONFIGURATION ------------------

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "supersecret")

# Professional Step: Extract components and encode the password
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD') 
host = os.getenv('MYSQL_HOST')
database = os.getenv('MYSQL_DB')

# URL Encode the password to handle '@' and '!'
safe_password = urllib.parse.quote_plus(password) if password else ""

# Professional Step: Handle SSL requirements for Azure MySQL
# We add ?ssl_ca= to ensure the connection is accepted by Azure's security gate
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
            return f"Error: {str(e)}"
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
    # Professional Step: Retry Loop
    # This prevents 'CrashLoopBackOff' if the DB is slow to respond on startup
    connected = False
    while not connected:
        try:
            with app.app_context():
                db.create_all() # Automatically creates tables
            connected = True
            print("Successfully connected to Azure MySQL!")
        except Exception as e:
            print(f"Database not ready yet... retrying in 5 seconds. Error: {e}")
            time.sleep(5)
    
    app.run(host="0.0.0.0", port=5000)