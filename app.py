from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "supersecret")

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER')}:"
    f"{os.getenv('MYSQL_PASSWORD')}@"
    f"{os.getenv('MYSQL_HOST')}/"
    f"{os.getenv('MYSQL_DB')}"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ------------------ MODEL ------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

# ------------------ ROUTES ------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'])

        user = User(
            username=request.form['username'],
            password=hashed_pw
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        user = User.query.filter_by(
            username=request.form['username']
        ).first()

        if user and check_password_hash(user.password, request.form['password']):
            return "Login Successful"

        return "Invalid Credentials"

    return render_template('login.html')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)