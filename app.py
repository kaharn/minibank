from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
from werkzeug.security import generate_password_hash, check_password_hash  # Для защиты паролей
from decorators import login_required

app = Flask(__name__)
app.secret_key = "super_secret_key"
DATA_FILE = 'data/users.json'


#  Вспомогательные функции
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


#Маршруты
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name', username)

        users = load_users()
        if username in users:
            flash("Пользователь уже существует!")
            return redirect(url_for('register'))

        # УСИЛЕНИЕ: Хешируем пароль и добавляем баланс
        hashed_password = generate_password_hash(password)
        users[username] = {
            "password": hashed_password,
            "full_name": full_name,
            "balance": 0.0  # Начальный баланс для Week 3
        }

        save_users(users)
        flash("Регистрация успешна!")
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        users = load_users()
        user_data = users.get(username)

        # УСИЛЕНИЕ: Проверяем хешированный пароль
        if user_data and check_password_hash(user_data['password'], password):
            session['user'] = username
            return redirect(url_for('dashboard'))

        flash("Неверный логин или пароль")
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/dashboard')
@login_required
def dashboard():
    users = load_users()
    current_user = users.get(session['user'])
    # УСИЛЕНИЕ: Передаем реальный баланс в шаблон
    return render_template('dashboard.html',
                           username=session['user'],
                           balance=current_user.get('balance', 0))


@app.route('/logout')
def logout():
    session.clear()  # Полная очистка сессии
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True, port=5000)