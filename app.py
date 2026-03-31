import os
from functools import wraps
from datetime import datetime
from flask import jsonify

from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from bson.objectid import ObjectId

# ---- Load environment ----
load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/sdiamond")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change_this_secret")

mongo = PyMongo(app)

# ================= DECORATOR =================
def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            role = session.get("role")
            if role not in allowed_roles:
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return wrapped
    return decorator


# ================= HOME =================
@app.route('/')
def home():
    return render_template("home.html")

@app.context_processor
def inject_cart_count():

    cart_count = 0

    if "user_id" in session:
        cart_count = mongo.db.cart.count_documents({
            "user_id": session["user_id"]
        })

    return dict(cart_count=cart_count)

# ================= REGISTER =================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')

        if not username or not email or not password:
            flash("Заповніть усі поля.")
            return redirect(url_for('register'))

        if mongo.db.users.find_one({"username": username}):
            flash("Користувач вже існує.")
            return redirect(url_for('register'))

        mongo.db.users.insert_one({
            "username": username,
            "email": email,
            "password_hash": generate_password_hash(password),
            "role": "user"
        })

        flash("Реєстрація успішна!")
        return redirect(url_for('login'))

    return render_template("register.html")


# ================= LOGIN =================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')

        user = mongo.db.users.find_one({"username": username})

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session['role'] = user['role']

            if user['role'] == "admin":
                return redirect(url_for('admin_home'))

            return redirect(url_for('user_home'))

        flash("Невірний логін або пароль.")
        return redirect(url_for('login'))

    return render_template("login.html")


# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# ================= USER HOME =================
@app.route('/user/home')
@role_required(['user'])
def user_home():
    return render_template("user_home.html")


# ================= PROFILE =================
@app.route('/profile')
@role_required(['user'])
def profile_page():
    user_id = session.get('user_id')

    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

    active_orders = list(
        mongo.db.orders.find({
            "user_id": user_id,
            "status": {"$ne": "скасовано"}
        }).sort("created_at", -1)
    )

    cancelled_orders = list(
        mongo.db.orders.find({
            "user_id": user_id,
            "status": "скасовано"
        }).sort("created_at", -1)
    )

    return render_template(
        "profile.html",
        user=user,
        active_orders=active_orders,
        cancelled_orders=cancelled_orders
    )


# ================= CANCEL ORDER =================
@app.route('/cancel_order/<order_id>', methods=['POST'])
@role_required(['user'])
def cancel_order(order_id):
    user_id = session.get('user_id')

    mongo.db.orders.update_one(
        {
            "_id": ObjectId(order_id),
            "user_id": user_id
        },
        {
            "$set": {
                "status": "скасовано",
                "cancelled_at": datetime.utcnow()
            }
        }
    )

    flash("Замовлення скасовано")
    return redirect(url_for('profile_page'))


# ================= UPDATE PROFILE =================
@app.route('/update_profile', methods=['POST'])
@role_required(['user'])
def update_profile():
    user_id = session.get('user_id')
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

    new_username = request.form.get('username')
    new_email = request.form.get('email')
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')

    update_data = {}

    if new_username and new_username != user['username']:
        update_data['username'] = new_username
        session['username'] = new_username

    if new_email and new_email != user['email']:
        update_data['email'] = new_email

    if new_password:
        if not current_password:
            flash("Введіть поточний пароль.")
            return redirect(url_for('profile_page'))

        if not check_password_hash(user['password_hash'], current_password):
            flash("Невірний поточний пароль.")
            return redirect(url_for('profile_page'))

        update_data['password_hash'] = generate_password_hash(new_password)

    if update_data:
        mongo.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        flash("Дані оновлено!")

    return redirect(url_for('profile_page'))


# ================= CREATE ORDER =================

    return redirect(url_for('user_home'))


# ================= ADMIN =================
@app.route('/admin/home')
@role_required(['admin'])
def admin_home():
    orders = list(mongo.db.orders.find().sort('created_at', -1))
    users = list(mongo.db.users.find().sort('username', 1))
    users_count = mongo.db.users.count_documents({})

    return render_template(
        'admin_home.html',
        orders=orders,
        users=users,
        users_count=users_count
    )


# ================= STATIC PAGES =================
@app.route("/catalog")
def catalog():

    query = {}

    type_ = request.args.get("type")
    material = request.args.get("material")
    stone = request.args.get("stone")

    min_price = request.args.get("min", type=int)
    max_price = request.args.get("max", type=int)

    if type_:
        query["type"] = type_

    if material:
        query["material"] = material

    if stone:
        query["stone"] = {"$in": [stone]}

    if min_price is not None and max_price is not None:
        query["price"] = {
            "$gte": min_price,
            "$lte": max_price
        }

    products = list(mongo.db.products.find(query))

    # 🔥 ДОДАТИ ЦЕ
    cart_count = 0
    if "user_id" in session:
        cart_count = mongo.db.cart.count_documents({
            "user_id": session["user_id"]
        })

    return render_template(
        "catalog.html",
        products=products,
        cart_count=cart_count
    )



@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():

    if "user_id" not in session:
        return jsonify({"error": "not_logged"}), 401

    data = request.json
    product_id = data.get("product_id")

    # 🔥 ВАЖЛИВО: string → ObjectId
    product_id = ObjectId(product_id)

    user_id = session["user_id"]

    # 🔥 перевіряємо чи вже є товар
    existing = mongo.db.cart.find_one({
        "user_id": user_id,
        "product_id": product_id
    })

    if existing:
        # якщо є → +1
        mongo.db.cart.update_one(
            {"_id": existing["_id"]},
            {"$inc": {"qty": 1}}
        )
    else:
        # якщо нема → додаємо
        mongo.db.cart.insert_one({
            "user_id": user_id,
            "product_id": product_id,
            "qty": 1
        })

    # 🔥 рахуємо кількість товарів
    count = mongo.db.cart.count_documents({
        "user_id": user_id
    })

    return jsonify({
        "success": True,
        "count": count
    })

@app.route('/custom-design')
def custom_design():
    return render_template("custom_design.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contacts')
def contacts():
    return render_template("contacts.html")


@app.route('/cart')
@role_required(['user'])
def cart():
    return render_template("cart.html")


# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)