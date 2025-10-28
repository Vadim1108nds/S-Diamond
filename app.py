import os
from functools import wraps
from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from bson.objectid import ObjectId
from datetime import datetime


# Load .env if present
load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/sdiamond")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change_this_secret")

mongo = PyMongo(app)

# ---- Utility: decorator для перевірки ролі ----
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            role = session.get("role")
            if role not in allowed_roles:
                flash("Доступ заборонено. Увійдіть з відповідною роллю.")
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return wrapped
    return decorator

# ---- Головна (статичний сайт) ----
@app.route('/')
def index():
    return render_template("index.html")

# ---- Реєстрація (звичайні користувачі) ----
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not username or not email or not password:
            flash("Заповніть усі поля.")
            return redirect(url_for('register'))

        if mongo.db.users.find_one({"username": username}):
            flash("Користувач з таким username вже існує.")
            return redirect(url_for('register'))

        mongo.db.users.insert_one({
            "username": username,
            "email": email,
            "password_hash": generate_password_hash(password),
            "role": "user"
        })
        flash("Реєстрація успішна! Увійдіть, будь ласка.")
        return redirect(url_for('login'))

    return render_template("register.html")

# ---- Логін ----
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = mongo.db.users.find_one({"username": username})
        if user and check_password_hash(user.get("password_hash",""), password):
            session['user_id'] = str(user.get("_id"))
            session['username'] = user.get("username")
            session['role'] = user.get("role")
            flash("Успішний вхід.")
            # Редірект за роллю
            if user.get("role") == "admin":
                return redirect(url_for('admin_home'))
            return redirect(url_for('user_home'))
        flash("Невірний логін або пароль.")
        return redirect(url_for('login'))

    return render_template("login.html")

# ---- Вихід ----
@app.route('/logout')
def logout():
    session.clear()
    flash("Вихід виконано.")
    return redirect(url_for('index'))



@app.route('/user/home')
@role_required(['user'])
def user_home():
    return render_template("user_home.html")

# ---- Простий API для перевірки (необов'язково) ----
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash("Увійдіть, щоб бачити профіль.")
        return redirect(url_for('login'))
    return {
        "user_id": session.get("user_id"),
        "username": session.get("username"),
        "role": session.get("role")
    }
@app.route('/create_order', methods=['POST'])
@role_required(['user'])
def create_order():
    user_id = session.get('user_id')
    username = session.get('username')

    order_type = request.form.get('order_type')  # "стандартне" або "кастомне"
    item = request.form.get('item')
    material = request.form.get('material')
    stone = request.form.get('stone', '')
    custom_name = request.form.get('custom_name', '')
    customer_name = request.form.get('customer_name')
    customer_phone = request.form.get('customer_phone')

    # Перевірка обов'язкових полів
    if not all([order_type, item, material, customer_name, customer_phone, custom_name]):
        flash("Заповніть усі обов'язкові поля.")
        return redirect(url_for('user_home'))

    # Створюємо документ для MongoDB
    order_doc = {
        "user_id": user_id,
        "username": username,
        "order_type": order_type,
        "item": item,
        "material": material,
        "stone": stone,
        "custom_name": custom_name,
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "status": "нове замовлення", 
        "created_at": datetime.utcnow()
    }

    mongo.db.orders.insert_one(order_doc)
    flash(f"Замовлення '{custom_name}' успішно створено!", "success")
    return redirect(url_for('user_home'))

# --- Адмінка ---
# --- Адмінська панель ---
@app.route('/admin/home')
@role_required(['admin'])
def admin_home():
    orders = list(mongo.db.orders.find().sort('created_at', -1))
    users = list(mongo.db.users.find().sort('username', 1))
    users_count = mongo.db.users.count_documents({})
    return render_template('admin_home.html', orders=orders, users=users, users_count=users_count)

@app.route('/update_order_status/<order_id>', methods=['POST'])
@role_required(['admin'])
def update_order_status(order_id):
    new_status = request.form.get('status')
    if new_status not in ["нове замовлення", "в роботі", "неможливе", "готове до видачі"]:
        flash("Некоректний статус!", "error")
    else:
        mongo.db.orders.update_one({'_id': ObjectId(order_id)}, {'$set': {'status': new_status}})
        flash(f"Статус замовлення оновлено на '{new_status}'", "success")
    return redirect(url_for('admin_home'))

@app.route('/delete_order/<order_id>', methods=['POST'])
@role_required(['admin'])
def delete_order(order_id):
    mongo.db.orders.delete_one({'_id': ObjectId(order_id)})
    flash("Замовлення успішно видалено.", "success")
    return redirect(url_for('admin_home'))

@app.route('/delete_user/<user_id>', methods=['POST'])
@role_required(['admin'])
def delete_user(user_id):
    mongo.db.users.delete_one({'_id': ObjectId(user_id)})
    flash("Користувача успішно видалено.", "success")
    return redirect(url_for('admin_home'))




if __name__ == '__main__':
    app.run(debug=True)