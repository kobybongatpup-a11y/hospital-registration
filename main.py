from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'koby'

app.config['MYSQL_HOST'] = 'mysql.railway.internal'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'XlQUmnlVDWVNuUpmzhQRYfEyizpDLJJC'
app.config['MYSQL_DB'] = 'hospital'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register():
    
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    room = request.form['room']

    cur = mysql.connection.cursor()
    # Check if user exists
    cur.execute('SELECT * FROM users WHERE email = %s', (email,))
    existing_user = cur.fetchone()

    if existing_user:
        cur.close()
        flash('Email already registered!', 'error')
        return redirect(url_for('home'))

    try:
        # Insert new user
        cur.execute('''INSERT INTO users (first_name, last_name, email, room, created_at) 
                           VALUES (%s, %s, %s, %s, %s)''',
                    (firstname, lastname, email, room, datetime.now()))
        mysql.connection.commit()
        cur.close()
        flash('Registration successful!', 'success')
        # Ensure you have a 'success' route defined, or change this to 'home'
        return redirect(url_for('home'))
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('home'))



# Route: View All Users
@app.route('/users')
def view_users():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM users ORDER BY created_at DESC')
    users = cur.fetchall()
    cur.close()
    return render_template('users.html', users=users)


if __name__ == '__main__':

    app.run(debug=True)
