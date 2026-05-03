from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
from decorators import login_required

app = Flask(__name__)
app.secret_key = "super_secret_key"  # Необходимо для работы сессий
DATA_FILE = 'data/users.json'


def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def save_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f, indent=4)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']

        users = load_users()
        if username in users:
            return "User already exists!"

        users[username] = {"password": password, "full_name": full_name}
        save_users(users)
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        users = load_users()
        if username in users and users[username]['password'] == password:
            session['user'] = username
            return redirect(url_for('dashboard'))
        return "Invalid credentials"
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=session['user'])


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)