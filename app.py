import os
from functools import wraps
from datetime import datetime
from flask import jsonify
from werkzeug.utils import secure_filename

from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from bson.objectid import ObjectId

import hashlib
import base64
import json
import requests
from datetime import datetime

# Налаштування LiqPay
LIQPAY_PUBLIC_KEY = os.getenv("LIQPAY_PUBLIC_KEY", "sandbox_i19446328529")
LIQPAY_PRIVATE_KEY = os.getenv("LIQPAY_PRIVATE_KEY", "sandbox_MuZtaKkFHg2fuITmHsXpB5RYs4QoH0RBrnXmbfrE")
LIQPAY_URL = "https://www.liqpay.ua/api/3/checkout"

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


# ================= PRODUCT MANAGEMENT (ADMIN) =================

# ================= ADMIN ROUTES =================

@app.route('/admin/home')
@role_required(['admin'])
def admin_home():
    orders = list(mongo.db.orders.find().sort('created_at', -1))
    users = list(mongo.db.users.find().sort('username', 1))
    users_count = mongo.db.users.count_documents({})
    products = list(mongo.db.products.find().sort('name', 1))
    return render_template('admin_home.html', orders=orders, users=users, users_count=users_count, products=products)

@app.route('/update_order_status/<order_id>', methods=['POST'])
@role_required(['admin'])
def update_order_status(order_id):
    status = request.form.get("status")
    mongo.db.orders.update_one({"_id": ObjectId(order_id)}, {"$set": {"status": status, "updated_at": datetime.utcnow()}})
    return redirect(url_for('admin_home'))

@app.route('/delete_order/<order_id>', methods=['POST'])
@role_required(['admin'])
def delete_order(order_id):
    mongo.db.orders.delete_one({"_id": ObjectId(order_id)})
    return redirect(url_for('admin_home'))

@app.route('/delete_user/<user_id>', methods=['POST'])
@role_required(['admin'])
def delete_user(user_id):
    mongo.db.users.delete_one({"_id": ObjectId(user_id)})
    mongo.db.cart.delete_many({"user_id": user_id})
    mongo.db.orders.delete_many({"user_id": user_id})
    flash("Користувача видалено")
    return redirect(url_for('admin_home'))

@app.route('/delete_product/<product_id>', methods=['POST'])
@role_required(['admin'])
def delete_product(product_id):
    mongo.db.cart.delete_many({"product_id": ObjectId(product_id)})
    mongo.db.products.delete_one({"_id": ObjectId(product_id)})
    flash("Товар видалено")
    return redirect(url_for('admin_home'))

@app.route('/edit_product/<product_id>', methods=['GET', 'POST'])
@role_required(['admin'])
def edit_product(product_id):
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        flash("Товар не знайдено")
        return redirect(url_for('admin_home'))
    if request.method == 'POST':
        name = request.form.get('name')
        type_ = request.form.get('type')
        material = request.form.get('material')
        stone = request.form.get('stone')
        price = int(request.form.get('price'))
        weight = float(request.form.get('weight') or 0)
        description = request.form.get('description')
        update_data = {
            "name": name,
            "type": type_,
            "material": material,
            "stone": [stone],
            "price": price,
            "weight": weight,
            "description": description
        }
        if 'image' in request.files and request.files['image'].filename:
            file = request.files['image']
            filename = secure_filename(file.filename)
            filepath = os.path.join('static/images/products', filename)
            file.save(filepath)
            update_data["image"] = filename
        mongo.db.products.update_one({"_id": ObjectId(product_id)}, {"$set": update_data})
        flash("Товар оновлено")
        return redirect(url_for('admin_home'))
    return render_template('edit_product.html', product=product)
UPLOAD_FOLDER = "static/images/products"

@app.route('/add_product', methods=['POST'])
@role_required(['admin'])
def add_product():
    name = request.form.get("name")
    type_ = request.form.get("type")
    material = request.form.get("material")
    stone = request.form.get("stone")
    price = int(request.form.get("price"))
    weight = float(request.form.get("weight") or 0)
    description = request.form.get("description")

    file = request.files["image"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    mongo.db.products.insert_one({
        "name": name,
        "type": type_,
        "material": material,
        "stone": [stone],
        "price": price,
        "weight": weight,
        "description": description,
        "image": filename
    })

    flash("Товар додано!")
    return redirect(url_for('admin_home'))

# ================= STATIC PAGES =================
@app.route("/catalog")
def catalog():

    query = {}

    type_ = request.args.get("type")
    material = request.args.get("material")
    stone = request.args.get("stone")

    min_price = request.args.get("min", type=int)
    max_price = request.args.get("max", type=int)

    type_mapping = {
        "Кільця": "ring",
        "Сережки": "earrings",
        "Браслети": "bracelet",
        "Підвіски": "pendant"
    }

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

    product_id = ObjectId(product_id)
    user_id = session["user_id"]

    existing = mongo.db.cart.find_one({
        "user_id": user_id,
        "product_id": product_id
    })

    if existing:
        mongo.db.cart.update_one(
            {"_id": existing["_id"]},
            {"$inc": {"qty": 1}}
        )
    else:
        mongo.db.cart.insert_one({
            "user_id": user_id,
            "product_id": product_id,
            "qty": 1
        })

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
@app.route('/add_custom_to_cart', methods=['POST'])
@role_required(['user'])
def add_custom_to_cart():
    data = request.json
    user_id = session['user_id']

    custom_item = {
        "user_id": user_id,
        "is_custom": True,
        "qty": 1,
        "unit_price": data['price'],
        "total_price": data['price'],
        "custom_data": {
            "type": data['type'],
            "metal": data['metal'],
            "stone": data['stone'],
            "size": data.get('size'),
            "lead_days": data.get('lead_days', 14),
            "description": data.get('description', 'Індивідуальна прикраса'),
            "image": data.get('image', '/static/images/custom_placeholder.png')
        }
    }

    # Можна дозволити тільки один кастомний товар або будь-яку кількість
    mongo.db.cart.insert_one(custom_item)

    # Оновлюємо лічильник кошика
    cart_count = mongo.db.cart.count_documents({"user_id": user_id})
    return jsonify({"success": True, "count": cart_count})


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/contacts')
def contacts():
    return render_template("contacts.html")


@app.route('/cart')
@role_required(['user'])
def cart():
    user_id = session.get('user_id')
    cart_items = list(mongo.db.cart.find({"user_id": user_id}))
    
    # Словники для перекладу
    metal_ua = {
        'gold': 'золото',
        'silver': 'срібло',
        'platinum': 'платина'
    }
    stone_ua = {
        'diamond': 'діамант',
        'sapphire': 'сапфір',
        'amethyst': 'аметист',
        'ruby': 'рубін',
        'none': 'без каменю'
    }
    type_ua = {
        'ring': 'Кільце',
        'earrings': 'Сережки',
        'pendant': 'Підвіска'
    }
    
    items = []
    total_price = 0
    
    for item in cart_items:
        if item.get('is_custom'):
            custom = item['custom_data']
            # Переклад
            metal = metal_ua.get(custom.get('metal', ''), custom.get('metal', ''))
            stone = stone_ua.get(custom.get('stone', ''), custom.get('stone', ''))
            size_info = f", розмір {custom.get('size')}" if custom.get('size') else ""
            items.append({
                "cart_id": str(item["_id"]),
                "is_custom": True,
                "name": f"{type_ua.get(custom.get('type'), 'Прикраса')} (індивідуальне)",
                "price": item['unit_price'],
                "qty": item['qty'],
                "total": item['total_price'],
                "image": custom.get('image', '/static/images/custom_placeholder.png'),
                "custom_details": f"{metal}, {stone}{size_info}"
            })
            total_price += item['total_price']
        else:
            product = mongo.db.products.find_one({"_id": item["product_id"]})
            if product:
                item_total = product["price"] * item["qty"]
                items.append({
                    "cart_id": str(item["_id"]),
                    "product_id": str(product["_id"]),
                    "name": product["name"],
                    "price": product["price"],
                    "qty": item["qty"],
                    "total": item_total,
                    "image": product.get("image", ""),
                    "material": product.get("material", ""),
                    "stone": product.get("stone", [""])[0] if product.get("stone") else ""
                })
                total_price += item_total
    
    cart_count = sum(item["qty"] for item in items)
    return render_template("cart.html", items=items, total_price=total_price, cart_count=cart_count)

@app.route('/update_cart', methods=['POST'])
@role_required(['user'])
def update_cart():
    data = request.json
    cart_id = data.get("cart_id")
    action = data.get("action")
    
    cart_item = mongo.db.cart.find_one({"_id": ObjectId(cart_id), "user_id": session["user_id"]})
    if not cart_item:
        return jsonify({"error": "Товар не знайдено"}), 404
    
    if action == "increase":
        new_qty = cart_item["qty"] + 1
        mongo.db.cart.update_one({"_id": ObjectId(cart_id)}, {"$set": {"qty": new_qty}})
        # оновлюємо total_price для кастомного товару
        if cart_item.get('is_custom'):
            new_total = cart_item['unit_price'] * new_qty
            mongo.db.cart.update_one({"_id": ObjectId(cart_id)}, {"$set": {"total_price": new_total}})
    elif action == "decrease":
        if cart_item["qty"] > 1:
            new_qty = cart_item["qty"] - 1
            mongo.db.cart.update_one({"_id": ObjectId(cart_id)}, {"$set": {"qty": new_qty}})
            if cart_item.get('is_custom'):
                new_total = cart_item['unit_price'] * new_qty
                mongo.db.cart.update_one({"_id": ObjectId(cart_id)}, {"$set": {"total_price": new_total}})
        else:
            mongo.db.cart.delete_one({"_id": ObjectId(cart_id)})
    elif action == "remove":
        mongo.db.cart.delete_one({"_id": ObjectId(cart_id)})
    else:
        return jsonify({"error": "Невідома дія"}), 400
    
    all_cart_items = list(mongo.db.cart.find({"user_id": session["user_id"]}))
    total_count = sum(item.get("qty", 1) for item in all_cart_items)
    
    return jsonify({"success": True, "cart_count": total_count})

@app.route('/checkout')
@role_required(['user'])
def checkout():
    user_id = session.get('user_id')
    cart_items = list(mongo.db.cart.find({"user_id": user_id}))
    
    items = []
    total_price = 0
    
    for item in cart_items:
        if item.get('is_custom'):
            total_price += item['total_price']
            items.append({
                "name": f"Індивідуальне замовлення ({item['custom_data']['type']})",
                "qty": item['qty'],
                "total": item['total_price']
            })
        else:
            product = mongo.db.products.find_one({"_id": item["product_id"]})
            if product:
                item_total = product["price"] * item["qty"]
                items.append({
                    "name": product["name"],
                    "qty": item["qty"],
                    "total": item_total,
                })
                total_price += item_total
    
    cart_count = sum(item["qty"] for item in items)
    return render_template("checkout.html", items=items, total_price=total_price, cart_count=cart_count)

@app.route('/create_order', methods=['POST'])
@role_required(['user'])
def create_order():
    user_id = session.get('user_id')
    
    fullname = request.form.get('fullname')
    phone = request.form.get('phone')
    email = request.form.get('email')
    delivery_type = request.form.get('delivery_type')
    nova_poshta_branch = request.form.get('nova_poshta_branch')
    comment = request.form.get('comment')
    payment_method = request.form.get('payment_method')
    
    cart_items = list(mongo.db.cart.find({"user_id": user_id}))
    
    items = []
    total_price = 0
    
    for cart_item in cart_items:
        if cart_item.get('is_custom'):
            items.append({
                "is_custom": True,
                "custom_data": cart_item['custom_data'],
                "price": cart_item['unit_price'],
                "qty": cart_item['qty']
            })
            total_price += cart_item['total_price']
        else:
            product = mongo.db.products.find_one({"_id": cart_item["product_id"]})
            if product:
                items.append({
                    "product_id": str(product["_id"]),
                    "name": product["name"],
                    "price": product["price"],
                    "qty": cart_item["qty"]
                })
                total_price += product["price"] * cart_item["qty"]
    
    order_number = f"SD-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
    
    order_data = {
        "user_id": user_id,
        "order_number": order_number,
        "fullname": fullname,
        "phone": phone,
        "email": email,
        "delivery_type": delivery_type,
        "nova_poshta_branch": nova_poshta_branch if delivery_type == 'delivery' else None,
        "comment": comment,
        "payment_method": payment_method,
        "items": items,
        "total_amount": total_price,
        "status": "нове замовлення",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    order_id = mongo.db.orders.insert_one(order_data).inserted_id
    
    # Очищаємо кошик
    mongo.db.cart.delete_many({"user_id": user_id})
    
    if payment_method == "card":
        return redirect(url_for('liqpay_payment', order_id=str(order_id)))
    
    flash(f"Замовлення #{order_number} успішно створено!")
    return redirect(url_for('profile_page'))

@app.route('/liqpay_payment/<order_id>')
@role_required(['user'])
def liqpay_payment(order_id):
    order = mongo.db.orders.find_one({"_id": ObjectId(order_id), "user_id": session["user_id"]})
    
    if not order:
        flash("Замовлення не знайдено")
        return redirect(url_for('cart'))
    
    # Параметри для LiqPay
    params = {
        "version": "3",
        "public_key": LIQPAY_PUBLIC_KEY,
        "action": "pay",
        "amount": str(order["total_amount"]),
        "currency": "UAH",
        "description": f"Оплата замовлення #{order['order_number']}",
        "order_id": order["order_number"],
        "result_url": url_for('payment_result', _external=True),   # ← після оплати → профіль
        "server_url": url_for('payment_callback', _external=True),
    }
    
    # Створюємо підпис
    data = base64.b64encode(json.dumps(params).encode()).decode()
    signature = base64.b64encode(hashlib.sha1(f"{LIQPAY_PRIVATE_KEY}{data}{LIQPAY_PRIVATE_KEY}".encode()).digest()).decode()
    
    return render_template("liqpay_form.html", data=data, signature=signature, liqpay_url=LIQPAY_URL)

@app.route('/payment_result')
def payment_result():
    # Отримуємо параметри з URL (LiqPay передасть їх у GET)
    order_id = request.args.get('order_id')
    status = request.args.get('status')  # success або failure
    # Можна також перевірити підпис, але для спрощення поки так
    if status == 'success':
        flash('Оплата пройшла успішно! Дякуємо за покупку.')
    else:
        flash('Помилка оплати. Спробуйте ще раз.')
    return redirect(url_for('profile_page'))  # або на сторінку замовлення

@app.route('/payment_callback', methods=['POST'])
def payment_callback():
    data = request.form.get('data')
    signature = request.form.get('signature')
    
    # Перевіряємо підпис
    expected_signature = base64.b64encode(hashlib.sha1(f"{LIQPAY_PRIVATE_KEY}{data}{LIQPAY_PRIVATE_KEY}".encode()).digest()).decode()
    
    if signature != expected_signature:
        return "Invalid signature", 400
    
    # Декодуємо дані
    decoded_data = json.loads(base64.b64decode(data).decode())
    
    order_number = decoded_data.get('order_id')
    status = decoded_data.get('status')
    
    # Оновлюємо статус замовлення
    order = mongo.db.orders.find_one({"order_number": order_number})
    if order:
        mongo.db.orders.update_one(
            {"_id": order["_id"]},
            {
                "$set": {
                    "status": "paid" if status == "success" else "failed",
                    "payment_id": decoded_data.get('payment_id'),
                    "updated_at": datetime.utcnow()
                }
            }
        )
    
    return "OK", 200




# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)