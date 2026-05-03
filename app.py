from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from decorators import login_required

app = Flask(__name__)
app.secret_key = "super_secret_key"
DATA_FILE = 'data/users.json'


def load_users():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return {}


def save_users(users):
    if not os.path.exists('data'):
        os.makedirs('data')
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Делаем full_name необязательным, если его нет в форме
        full_name = request.form.get('full_name', username)

        users = load_users()
        if username in users:
            flash("Пользователь уже существует!")
            return redirect(url_for('register'))

        users[username] = {"password": password, "full_name": full_name}
        save_users(users)
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        users = load_users()
        if username in users and users[username]['password'] == password:
            session['user'] = username
            return redirect(url_for('dashboard'))

        flash("Неверные учетные данные")
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session['user'])


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)