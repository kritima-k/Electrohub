import os 
from flask import Flask, render_template, request, redirect, session, jsonify, url_for
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
 
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "electrohub_secret_key")
 
 
#  DATABASE CONNECTION 
 
def get_db_connection():
    connection = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "electrohub"),
        port=int(os.getenv("DB_PORT", "3306"))
    )
    return connection
 
# ================= HOME =================
 
@app.route('/')
def home():
    return render_template('index.html')
 
 
# ================= MAIN PAGES =================
 
@app.route('/about')
def about():
    return render_template('about.html')
 
 
@app.route('/product')
def product():
    return render_template('product.html')
 
 
@app.route('/categories')
def categories():
    return render_template('categories.html')
 
 
@app.route('/deals')
def deals():
    return render_template('deals.html')
 
 
@app.route('/contact')
def contact():
    return render_template('contact.html')
 
 
@app.route('/cart')
def cart():
    if 'user_id' not in session:
        return redirect('/login')
 
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM cart WHERE user_id=%s",
        (session['user_id'],)
    )
    cart_items = cursor.fetchall()
    cursor.close()
    conn.close()
 
    total = sum(item['price'] * item['quantity'] for item in cart_items)
 
    return render_template('cart.html', cart_items=cart_items, total=total)
 
 
@app.route('/wishlist')
def wishlist():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('wishlist.html')
 
 
@app.route('/place_order', methods=['POST'])
def place_order():
 
    if 'user_id' not in session:
        return jsonify({
            "success": False,
            "message": "Please login first."
        })
 
    data = request.get_json()
 
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
 
    # Get cart items
    cursor.execute(
        "SELECT * FROM cart WHERE user_id=%s",
        (session['user_id'],)
    )
 
    cart_items = cursor.fetchall()
 
    if not cart_items:
        cursor.close()
        conn.close()
 
        return jsonify({
            "success": False,
            "message": "Your cart is empty."
        })
 
    # Calculate total
    total = sum(item["price"] * item["quantity"] for item in cart_items)
 
    # Save order
    cursor.execute("""
        INSERT INTO orders
        (
            user_id,
            full_name,
            phone,
            address,
            city,
            state,
            pincode,
            payment_method,
            total_amount
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """,(
        session["user_id"],
        data["full_name"],
        data["phone"],
        data["address"],
        data["city"],
        data["state"],
        data["pincode"],
        data["payment_method"],
        total
    ))
 
    order_id = cursor.lastrowid
 
    # Save products
    for item in cart_items:
 
        cursor.execute("""
            INSERT INTO order_items
            (
                order_id,
                product_id,
                product_name,
                price,
                quantity,
                image
            )
            VALUES
            (%s,%s,%s,%s,%s,%s)
        """,(
            order_id,
            item["product_id"],
            item["product_name"],
            item["price"],
            item["quantity"],
            item["image"]
        ))
 
    # Clear cart
    cursor.execute(
        "DELETE FROM cart WHERE user_id=%s",
        (session["user_id"],)
    )
 
    conn.commit()
 
    cursor.close()
    conn.close()
 
    return jsonify({
        "success": True,
        "order_id": order_id
    })
 
 
@app.route('/update_cart', methods=['POST'])
def update_cart():
 
    if 'user_id' not in session:
        return jsonify({"status": "login"})
 
    data = request.get_json()
 
    conn = get_db_connection()
    cursor = conn.cursor()
 
    cursor.execute("""
        UPDATE cart
        SET quantity=%s
        WHERE user_id=%s AND product_id=%s
    """, (
        data["quantity"],
        session["user_id"],
        data["id"]
    ))
 
    conn.commit()
 
    cursor.close()
    conn.close()
 
    return jsonify({"status": "success"})
 
 
# ================= CATEGORY PAGES =================
 
@app.route('/smartphones')
def smartphones():
    return render_template('smartphones.html')
 
 
@app.route('/laptops')
def laptops():
    return render_template('laptops.html')
 
 
@app.route('/earbuds')
def earbuds():
    return render_template('earbuds.html')
 
 
@app.route('/watches')
def watches():
    return render_template('watches.html')
 
 
@app.route('/gaming')
def gaming():
    return render_template('gaming.html')
 
 
@app.route('/speakers')
def speakers():
    return render_template('speakers.html')
 
 
@app.route('/tablets')
def tablets():
    return render_template('tablets.html')
 
 
@app.route('/accessories')
def accessories():
    return render_template('accessories.html')
 
 
@app.route('/cameras')
def cameras():
    return render_template('cameras.html')
 
 
@app.route('/powerbanks')
def powerbanks():
    return render_template('powerbanks.html')
 
 
# ================= RETURNS =================
 
@app.route('/returns')
def returns():
    return render_template('returns.html')
 
 
# ================= ADD TO CART =================
 
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
 
    if 'user_id' not in session:
        return jsonify({
            "status": "login",
            "redirect": url_for("login")
        })
 
    data = request.get_json()
 
    product_id = data['id']
    product_name = data['name']
    product_price = data['price']
    product_image = data['image']
 
    conn = get_db_connection()
    cursor = conn.cursor()
 
    cursor.execute(
        "SELECT * FROM cart WHERE user_id=%s AND product_id=%s",
        (session['user_id'], product_id)
    )
 
    item = cursor.fetchone()
 
    if item:
 
        cursor.execute(
            """
            UPDATE cart
            SET quantity = quantity + 1
            WHERE user_id=%s AND product_id=%s
            """,
            (session['user_id'], product_id)
        )
 
    else:
 
        cursor.execute(
            """
            INSERT INTO cart
            (user_id, product_id, product_name, price, image, quantity)
            VALUES(%s,%s,%s,%s,%s,%s)
            """,
            (
                session['user_id'],
                product_id,
                product_name,
                product_price,
                product_image,
                1
            )
        )
 
    conn.commit()
 
    cursor.close()
    conn.close()
 
    return jsonify({
        "status": "success"
    })
 
 
# ================= CART COUNT =================
 
@app.route('/cart_count')
def cart_count():
    if 'user_id' not in session:
        return jsonify({"count": 0})
 
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT SUM(quantity) FROM cart WHERE user_id=%s",
        (session['user_id'],)
    )
    result = cursor.fetchone()
    cursor.close()
    conn.close()
 
    count = result[0] if result[0] else 0
    return jsonify({"count": count})
 
 
@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
 
    if 'user_id' not in session:
        return jsonify({"status": "login"})
 
    data = request.get_json()
 
    conn = get_db_connection()
    cursor = conn.cursor()
 
    cursor.execute(
        """
        DELETE FROM cart
        WHERE user_id=%s AND product_id=%s
        """,
        (
            session['user_id'],
            data['id']
        )
    )
 
    conn.commit()
 
    cursor.close()
    conn.close()
 
    return jsonify({"status": "success"})
 
 
# ================= CHECKOUT =================
 
@app.route('/checkout')
def checkout():
    if 'user_id' not in session:
        return redirect('/login')
 
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM cart WHERE user_id=%s",
        (session['user_id'],)
    )
    cart_items = cursor.fetchall()
    cursor.close()
    conn.close()
 
    total = sum(item['price'] * item['quantity'] for item in cart_items)
 
    return render_template('checkout.html', cart_items=cart_items, total=total)
 
 
# ================= ADD TO WISHLIST =================
 
@app.route('/add_to_wishlist', methods=['POST'])
def add_to_wishlist():
 
    if 'user_id' not in session:
        return jsonify({
            "status": "login",
            "redirect": url_for("login")
        })
 
    data = request.get_json()
 
    conn = get_db_connection()
    cursor = conn.cursor()
 
    # Check if product already exists in wishlist
    cursor.execute(
        "SELECT * FROM wishlist WHERE user_id=%s AND product_id=%s",
        (session['user_id'], data['id'])
    )
 
    item = cursor.fetchone()
 
    if item:
        cursor.close()
        conn.close()
        return jsonify({"status": "exists"})
 
    cursor.execute(
        """
        INSERT INTO wishlist
        (user_id, product_id, product_name, price, image)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            session['user_id'],
            data['id'],
            data['name'],
            data['price'],
            data['image']
        )
    )
 
    conn.commit()
    cursor.close()
    conn.close()
 
    return jsonify({
        "status": "success",
        "message": "Product added to wishlist."
    })
 
 
# ================= GET WISHLIST =================
 
@app.route('/get_wishlist')
def get_wishlist():
    if 'user_id' not in session:
        return jsonify([])
 
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM wishlist WHERE user_id=%s",
        (session['user_id'],)
    )
    items = cursor.fetchall()
    cursor.close()
    conn.close()
 
    return jsonify(items)
 
 
# ================= REMOVE FROM WISHLIST =================
@app.route('/remove_wishlist/<int:item_id>', methods=['DELETE'])
def remove_wishlist(item_id):
    if 'user_id' not in session:
        return jsonify({"status": "login"})
 
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM wishlist WHERE id=%s AND user_id=%s",
        (item_id, session['user_id'])
    )
    conn.commit()
    cursor.close()
    conn.close()
 
    return jsonify({"status": "success"})
 
 
# ================= MOVE TO CART =================
 
@app.route('/move_to_cart/<int:item_id>', methods=['POST'])
def move_to_cart(item_id):
    if 'user_id' not in session:
        return jsonify({"status": "login"})
 
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
 
    # Get wishlist item
    cursor.execute(
        "SELECT * FROM wishlist WHERE id=%s AND user_id=%s",
        (item_id, session['user_id'])
    )
    item = cursor.fetchone()
 
    if not item:
        cursor.close()
        conn.close()
        return jsonify({"status": "not_found"})
 
    # Check if already in cart
    cursor.execute(
        "SELECT * FROM cart WHERE user_id=%s AND product_id=%s",
        (session['user_id'], item['product_id'])
    )
    existing = cursor.fetchone()
 
    if existing:
        cursor.execute(
            "UPDATE cart SET quantity = quantity + 1 WHERE user_id=%s AND product_id=%s",
            (session['user_id'], item['product_id'])
        )
    else:
        cursor.execute(
            """
            INSERT INTO cart (user_id, product_id, product_name, price, image, quantity)
            VALUES (%s,%s,%s,%s,%s,%s)
            """,
            (session['user_id'], item['product_id'], item['product_name'],
             item['price'], item['image'], 1)
        )
 
    # Remove from wishlist
    cursor.execute(
        "DELETE FROM wishlist WHERE id=%s AND user_id=%s",
        (item_id, session['user_id'])
    )
 
    conn.commit()
    cursor.close()
    conn.close()
 
    return jsonify({"status": "success"})
 
 
# SIGNUP
 
@app.route('/signup', methods=['GET', 'POST'])
def signup():
 
    if request.method == 'POST':
 
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirmPassword']
 
        if password != confirm_password:
            return "Passwords do not match!"
 
        hashed_password = generate_password_hash(password)
 
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (Name, Email, Password)
                VALUES (%s,%s,%s)
                """,
                (name, email, hashed_password)
            )
            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/login')
        except pymysql.err.IntegrityError:
            return "Email already exists! Please login."
 
    return render_template('signup.html')
 
 
# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
 
        email = request.form['email']
        password = request.form['password']
 
        conn = get_db_connection()
        cursor = conn.cursor()
 
        cursor.execute(
            "SELECT * FROM users WHERE Email=%s",
            (email,)
        )
 
        user = cursor.fetchone()
        cursor.close()
        conn.close()
 
        if user:
 
            if check_password_hash(user[3], password):
 
                session['user_id'] = user[0]
                session['user_name'] = user[1]
 
                return redirect('/')
 
            else:
                return "Incorrect Password!"
 
        else:
            return "Email not found!"
 
    return render_template('login.html')
 
 
# ================= LOGOUT =================
 
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
 
 
# ================= RUN =================
 
if __name__ == "__main__":
    app.run(debug=True)