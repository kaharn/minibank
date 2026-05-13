from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os
import random
from werkzeug.security import generate_password_hash, check_password_hash
from decorators import login_required

app = Flask(__name__)
app.secret_key = "super_secret_key"

DATA_FILE = 'data/users.json'
TRANSACTIONS_FILE = 'data/transactions.json'


# =========================
# USERS
# =========================

def load_users():
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return {}

def generate_card_number():

    return f"{random.randint(4000,4999)} {random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}"

def save_users(users):
    if not os.path.exists('data'):
        os.makedirs('data')

    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


# =========================
# TRANSACTIONS
# =========================

def load_transactions():
    if not os.path.exists(TRANSACTIONS_FILE):
        return []

    with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return []


def save_transactions(transactions):
    with open(TRANSACTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(transactions, f, indent=4, ensure_ascii=False)


# =========================
# HOME
# =========================

@app.route('/')
def home():
    return render_template('home.html')

def generate_card_number():

    return f"""
        {random.randint(4000,4999)}
        {random.randint(1000,9999)}
        {random.randint(1000,9999)}
        {random.randint(1000,9999)}
    """.replace("\n", "").strip()


# =========================
# REGISTER
# =========================

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

        hashed_password = generate_password_hash(password)

        users[username] = {
            "password": hashed_password,
            "full_name": full_name,
            "balance": 1000,
            "card_number": generate_card_number()
        }

        save_users(users)

        flash("Регистрация успешна!")
        return redirect(url_for('login'))

    return render_template('register.html')


# =========================
# LOGIN
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        users = load_users()

        user_data = users.get(username)

        if user_data and check_password_hash(user_data['password'], password):

            session['user'] = username

            return redirect(url_for('dashboard'))

        flash("Неверный логин или пароль")

        return redirect(url_for('login'))

    return render_template('login.html')


# =========================
# DASHBOARD
# =========================

@app.route('/dashboard')
@login_required
def dashboard():

    users = load_users()

    transactions = load_transactions()

    current_user = users.get(session['user'])

    user_transactions = []

    for tx in reversed(transactions):

        if tx['sender'] == session['user'] or tx['receiver'] == session['user']:
            user_transactions.append(tx)

    user_transactions = user_transactions[:5]

    return render_template(
        'dashboard.html',
        username=session['user'],
        balance=current_user.get('balance', 0),
        transactions=user_transactions,
        card_number=current_user.get("card_number", "0000 0000 0000 0000")
    )


# =========================
# TRANSFER
# =========================

@app.route('/transfer', methods=['POST'])
@login_required
def transfer():

    receiver = request.form.get('receiver')
    amount = request.form.get('amount')

    users = load_users()

    sender = session['user']

    if receiver not in users:
        flash('Пользователь не найден')
        return redirect(url_for('dashboard'))

    if receiver == sender:
        flash('Нельзя перевести самому себе')
        return redirect(url_for('dashboard'))

    try:
        amount = float(amount)

    except:
        flash('Неверная сумма')
        return redirect(url_for('dashboard'))

    if amount <= 0:
        flash('Сумма должна быть больше 0')
        return redirect(url_for('dashboard'))

    if amount > 5000:
        flash('Превышен дневной лимит перевода ($5000)')
        return redirect(url_for('dashboard'))

    if users[sender]['balance'] < amount:
        flash('Недостаточно средств')
        return redirect(url_for('dashboard'))

    users[sender]['balance'] -= amount
    users[receiver]['balance'] += amount

    save_users(users)

    transactions = load_transactions()

    transactions.append({
        'sender': sender,
        'receiver': receiver,
        'amount': amount
    })

    save_transactions(transactions)

    flash('Перевод выполнен успешно')

    return redirect(url_for('dashboard'))


# =========================
# DEPOSIT
# =========================

@app.route('/deposit', methods=['POST'])
@login_required
def deposit():

    amount = request.form.get('amount')

    users = load_users()

    current_user = session['user']

    try:
        amount = float(amount)

    except:
        flash('Неверная сумма')
        return redirect(url_for('dashboard'))

    if amount <= 0:
        flash('Сумма должна быть больше 0')
        return redirect(url_for('dashboard'))

    if amount > 10000:
        flash('Максимальное пополнение: $10000')
        return redirect(url_for('dashboard'))

    users[current_user]['balance'] += amount

    save_users(users)

    transactions = load_transactions()

    transactions.append({
        'sender': 'BANK',
        'receiver': current_user,
        'amount': amount
    })

    save_transactions(transactions)

    flash('Баланс успешно пополнен')

    return redirect(url_for('dashboard'))


# =========================
# TRANSACTIONS
# =========================

@app.route('/transactions')
@login_required
def transactions_page():

    transactions = load_transactions()

    user_transactions = []

    for tx in reversed(transactions):

        if tx['sender'] == session['user'] or tx['receiver'] == session['user']:
            user_transactions.append(tx)

    return render_template(
        'transactions.html',
        transactions=user_transactions,
        username=session['user']
    )


# =========================
# PAYMENTS PAGES
# =========================

@app.route("/payments")
@login_required
def payments_page():
    return render_template("payments.html")


@app.route("/payments/mobile")
@login_required
def mobile_payment_page():
    return render_template("mobile_payment.html")


@app.route("/payments/internet")
@login_required
def internet_payment_page():
    return render_template("internet_payment.html")


@app.route("/payments/olimpbet")
@login_required
def olimpbet_page():
    return render_template("olimpbet_payment.html")


# =========================
# PAYMENTS
# =========================

@app.route('/payment/<service>', methods=['POST'])
@login_required
def payment(service):

    amount = request.form.get('amount')

    users = load_users()

    current_user = session['user']

    services = {
        'hareket': 'Харекет Қоры',
        'mobile': 'Мобильная связь',
        'internet': 'Интернет',
        'utilities': 'Коммунальные услуги'
    }

    if service not in services:
        flash('Сервис не найден')
        return redirect(url_for('dashboard'))

    try:
        amount = float(amount)

    except:
        flash('Неверная сумма')
        return redirect(url_for('dashboard'))

    if amount <= 0:
        flash('Сумма должна быть больше 0')
        return redirect(url_for('dashboard'))

    if users[current_user]['balance'] < amount:
        flash('Недостаточно средств')
        return redirect(url_for('dashboard'))

    users[current_user]['balance'] -= amount

    save_users(users)

    transactions = load_transactions()

    transactions.append({
        'sender': current_user,
        'receiver': services[service],
        'amount': amount
    })

    save_transactions(transactions)

    flash(f'Оплата выполнена: {services[service]}')

    return redirect(url_for('dashboard'))


# =========================
# OLIMPBET
# =========================

@app.route("/payment/olimpbet", methods=["POST"])
@login_required
def payment_olimpbet():

    account = request.form.get("account")
    amount = request.form.get("amount")

    users = load_users()

    username = session["user"]

    try:
        amount = float(amount)

    except:
        flash("Неверная сумма")
        return redirect("/payments/olimpbet")

    if amount <= 0:
        flash("Сумма должна быть больше 0")
        return redirect("/payments/olimpbet")

    if users[username]["balance"] < amount:
        flash("Недостаточно средств")
        return redirect("/payments/olimpbet")

    users[username]["balance"] -= amount

    save_users(users)

    transactions = load_transactions()

    transactions.append({
        "type": "Olimpbet",
        "sender": username,
        "receiver": account,
        "amount": amount
    })

    save_transactions(transactions)

    flash("Счет Olimpbet успешно пополнен")

    return redirect("/payments")


# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():

    session.clear()

    return redirect(url_for('home'))


# =========================
# START
# =========================

if __name__ == '__main__':
    app.run(debug=True)