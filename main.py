import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "koby_secret_123")

# --- DATABASE CONFIG ---
# Railway provides MYSQL_URL. If not found, it defaults to a local MySQL setup.
database_url = os.getenv("MYSQL_URL", "mysql+pymysql://root:@localhost/hospital")

# SQLAlchemy requires 'mysql+pymysql://' to talk to MySQL
if database_url.startswith("mysql://"):
    database_url = database_url.replace("mysql://", "mysql+pymysql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- DATABASE MODEL (Matches your original fields) ---
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    room = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# This automatically creates the 'users' table in your database if it doesn't exist
with app.app_context():
    db.create_all()

# --- ROUTES ---

@app.route('/')
def home():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    email = request.form.get('email')
    room = request.form.get('room')

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash('Email already registered!', 'error')
        return redirect(url_for('home'))

    try:
        new_user = User(
            first_name=firstname,
            last_name=lastname,
            email=email,
            room=room
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('view_users'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/users')
def view_users():
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template('users.html', users=users_list)

# --- RUN LOGIC ---
if __name__ == '__main__':
    # Railway uses the PORT env variable; Local uses 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
