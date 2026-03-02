from flask import Flask,render_template,request, redirect, session, flash, send_file, url_for
from flask_mail import Mail, Message
import sqlite3
import bcrypt
import random
import config
import os
import io
from fpdf import FPDF
from werkzeug.utils import secure_filename
import razorpay


app = Flask(__name__)



app.secret_key = config.SECRET_KEY


razorpay_client = razorpay.Client(
    auth=(config.RAZORPAY_KEY_ID, config.RAZORPAY_KEY_SECRET)
)




# ---------------- EMAIL CONFIGURATION ----------------
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = config.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = "".join(config.MAIL_PASSWORD.split()) # Remove ALL whitespace (tabs, spaces, etc.)
app.config['MAIL_DEFAULT_SENDER'] = config.MAIL_USERNAME
app.config['MAIL_DEBUG'] = True  

mail = Mail(app)

# ---------------- RAZORPAY CONFIGURATION ----------------
razorpay_client = razorpay.Client(auth=(config.RAZORPAY_KEY_ID, config.RAZORPAY_KEY_SECRET))



# ---------------- DB CONNECTION FUNCTION --------------
def get_db_connection():
    conn = sqlite3.connect(os.path.abspath(config.DATABASE))
    conn.row_factory = sqlite3.Row
    return conn



@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Fetch super admin name for copyright info
    cursor.execute("SELECT name FROM admin WHERE is_superadmin = 1 LIMIT 1")
    super_admin = cursor.fetchone()
    cursor.close()
    conn.close()
    
    super_admin_name = super_admin['name'] if super_admin else "Super Admin"
    return render_template("admin/index.html", super_admin_name=super_admin_name)




# ---------------------------------------------------------
# ROUTE 1: ADMIN SIGNUP (SEND OTP)
# ---------------------------------------------------------
# ROUTE 1: ADMIN SIGNUP (DIRECT REGISTRATION)
# ---------------------------------------------------------
@app.route('/admin-signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == "GET":
        return render_template("admin/admin_signup.html")

    name = request.form['name']
    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT admin_id FROM admin WHERE email=?", (email,))
    existing_admin = cursor.fetchone()

    if existing_admin:
        cursor.close()
        conn.close()
        flash("This email is already registered. Please login instead.", "danger")
        return redirect('/admin-signup')

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    is_super = 1 if email == config.MAIL_USERNAME else 0
    is_approved = 1 if is_super else 0

    cursor.execute(
        "INSERT INTO admin (name, email, password, is_approved, is_superadmin) VALUES (?, ?, ?, ?, ?)",
        (name, email, hashed_password, is_approved, is_super)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return render_template('admin/admin_register_success.html')





# =================================================================
# ROUTE 4: ADMIN LOGIN PAGE (GET + POST)
# =================================================================
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():

    # Show login page
    if request.method == 'GET':
        return render_template("admin/admin_login.html")

    # POST → Validate login
    email = request.form['email']
    password = request.form['password']

    # Step 1: Check if admin email exists
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM admin WHERE email=?", (email,))
    admin_row = cursor.fetchone()
    cursor.close()
    conn.close()

    if admin_row is None:
        flash("Email not found! Please register first.", "danger")
        return redirect('/admin-login')

    admin = dict(admin_row)

    # auto-approve if it is the primary admin from config
    if admin['email'] == config.MAIL_USERNAME:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE admin SET is_approved=1 WHERE admin_id=?", (admin['admin_id'],))
        conn.commit()
        cursor.close()
        conn.close()
        admin['is_approved'] = 1

    # Step 2: Compare entered password with hashed password
    stored_hashed_password = admin['password']
    if isinstance(stored_hashed_password, str):
        stored_hashed_password = stored_hashed_password.encode('utf-8')

    if not bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
        flash("Incorrect password! Try again.", "danger")
        return redirect('/admin-login')

    # Check if admin is approved
    if not admin['is_approved']:
        flash("Your account is pending approval from the Super Admin.", "warning")
        return redirect('/admin-login')

    # Step 5: If login success → Create admin session
    session['admin_id'] = admin['admin_id']
    session['admin_name'] = admin['name']
    session['admin_email'] = admin['email']
    session['is_superadmin'] = admin['is_superadmin']

    flash("Login Successful!", "success")
    return redirect('/admin-dashboard')




# =================================================================
# ROUTE 5: ADMIN DASHBOARD (PROTECTED ROUTE)
# =================================================================
@app.route('/admin-dashboard')
def admin_dashboard():

    # INCOME TRACKING FOR SUPER ADMIN
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Total Global Income & Products Sold
    cursor.execute("SELECT SUM(amount) as total FROM orders_table")
    total_income = cursor.fetchone()['total'] or 0
    
    cursor.execute("SELECT SUM(quantity) as total_sold FROM order_items_table")
    total_products_sold = cursor.fetchone()['total_sold'] or 0

    # 2. Income & Products Sold by individual admins
    cursor.execute("""
        SELECT a.name, a.is_superadmin, 
               SUM(p.price * oi.quantity) as admin_income,
               SUM(oi.quantity) as admin_products_sold
        FROM admin a
        LEFT JOIN products p ON a.admin_id = p.added_by
        LEFT JOIN order_items_table oi ON p.product_id = oi.product_id
        GROUP BY a.admin_id
    """)
    admin_stats = cursor.fetchall()
    
    # Check if currently logged in admin is superadmin
    is_super = session.get('is_superadmin')
    
    # 3. Personal Stats (for normal admin)
    personal_income = 0
    personal_products_sold = 0
    if not is_super:
        for stat in admin_stats:
            if stat['name'] == session['admin_name']:
                personal_income = stat['admin_income'] or 0
                personal_products_sold = stat['admin_products_sold'] or 0

    cursor.close()
    conn.close()

    return render_template("admin/dashboard.html", 
                         admin_name=session['admin_name'], 
                         total_income=total_income,
                         total_products_sold=total_products_sold,
                         admin_stats=admin_stats,
                         is_superadmin=is_super,
                         personal_income=personal_income,
                         personal_products_sold=personal_products_sold)



# =================================================================
# ROUTE 6: ADMIN LOGOUT
# =================================================================
@app.route('/admin-logout')
def admin_logout():

    # Clear admin session
    session.pop('admin_id', None)
    session.pop('admin_name', None)
    session.pop('admin_email', None)

    flash("Logged out successfully.", "success")
    return redirect('/admin-login')








# ------------------- IMAGE UPLOAD PATH -------------------
UPLOAD_FOLDER = 'static/uploads/product_images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




# =================================================================
# ROUTE 1: SHOW ADD PRODUCT PAGE (Protected Route)
# =================================================================
@app.route('/admin/add-item', methods=['GET'])
def add_item_page():

    # Only logged-in admin can access
    if 'admin_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/admin-login')

    return render_template("admin/add_item.html")






# =================================================================
# ROUTE 2: ADD PRODUCT INTO DATABASE
# =================================================================
@app.route('/admin/add-item', methods=['POST'])
def add_item():

    # Check admin session
    if 'admin_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/admin-login')

    # 1️⃣ Get form data
    name = request.form['name']
    description = request.form['description']
    category = request.form['category']
    price = request.form['price']
    image_file = request.files['image']

    # 2️⃣ Validate image upload
    if image_file.filename == "":
        flash("Please upload a product image!", "danger")
        return redirect('/admin/add-item')

    # 3️⃣ Secure the file name
    filename = secure_filename(image_file.filename)
    image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    # Handle optional images
    image2 = request.files.get('image2')
    image3 = request.files.get('image3')

    filename2 = ""
    if image2 and image2.filename:
        filename2 = secure_filename(image2.filename)
        image2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
        
    filename3 = ""
    if image3 and image3.filename:
        filename3 = secure_filename(image3.filename)
        image3.save(os.path.join(app.config['UPLOAD_FOLDER'], filename3))

    is_bestseller = 1 if request.form.get('is_bestseller') else 0
    added_by = session['admin_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, description, category, price, image, image2, image3, is_bestseller, added_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (name, description, category, price, filename, filename2, filename3, is_bestseller, added_by)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Product added successfully!", "success")
    return redirect('/admin/item-list')






# Removed duplicated admin_item_list route





#=================================================================
# ROUTE 10: VIEW SINGLE PRODUCT DETAILS
# =================================================================
@app.route('/admin/view-item/<int:item_id>')
def view_item(item_id):

    # Check admin session
    if 'admin_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/admin-login')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE product_id = ?", (item_id,))
    product = cursor.fetchone()

    cursor.close()
    conn.close()

    if not product:
        flash("Product not found!", "danger")
        return redirect('/admin/item-list')

    return render_template("admin/view_item.html", product=product)










# Route: /admin/update-item/<id> (GET)
# =================================================================
# ROUTE 11: SHOW UPDATE FORM WITH EXISTING DATA
# =================================================================
@app.route('/admin/update-item/<int:item_id>', methods=['GET'])
def update_item_page(item_id):

    # Check login
    if 'admin_id' not in session:
        flash("Please login!", "danger")
        return redirect('/admin-login')

    # Fetch product data
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE product_id = ?", (item_id,))
    product = cursor.fetchone()

    cursor.close()
    conn.close()

    if not product:
        flash("Product not found!", "danger")
        return redirect('/admin/item-list')

    return render_template("admin/update_item.html", product=product)







# 🟩 Step 2: Update Product Logic
# Route: /admin/update-item/<id> (POST)
# =================================================================
# ROUTE: UPDATE PRODUCT + OPTIONAL IMAGE REPLACE
# =================================================================
@app.route('/admin/update-item/<int:item_id>', methods=['POST'])
def update_item(item_id):

    if 'admin_id' not in session:
        flash("Please login!", "danger")
        return redirect('/admin-login')

    # 1️⃣ Get updated form data
    name = request.form['name']
    description = request.form['description']
    category = request.form['category']
    price = request.form['price']

    # Image processing
    image = request.files.get('image')
    image2 = request.files.get('image2')
    image3 = request.files.get('image3')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch current product data to get old image names
    cursor.execute("SELECT image, image2, image3 FROM products WHERE product_id = ?", (item_id,))
    current_images = cursor.fetchone()
    old_image_name = current_images[0] if current_images else None
    old_image2_name = current_images[1] if current_images else None
    old_image3_name = current_images[2] if current_images else None

    if image and image.filename:
        # Delete old image file if it exists
        if old_image_name:
            old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], old_image_name)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
        
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        cursor.execute("UPDATE products SET image=? WHERE product_id=?", (filename, item_id))

    if image2 and image2.filename:
        # Delete old image2 file if it exists
        if old_image2_name:
            old_image2_path = os.path.join(app.config['UPLOAD_FOLDER'], old_image2_name)
            if os.path.exists(old_image2_path):
                os.remove(old_image2_path)

        filename2 = secure_filename(image2.filename)
        image2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
        cursor.execute("UPDATE products SET image2=? WHERE product_id=?", (filename2, item_id))
        
    if image3 and image3.filename:
        # Delete old image3 file if it exists
        if old_image3_name:
            old_image3_path = os.path.join(app.config['UPLOAD_FOLDER'], old_image3_name)
            if os.path.exists(old_image3_path):
                os.remove(old_image3_path)

        filename3 = secure_filename(image3.filename)
        image3.save(os.path.join(app.config['UPLOAD_FOLDER'], filename3))
        cursor.execute("UPDATE products SET image3=? WHERE product_id=?", (filename3, item_id))

    is_bestseller = 1 if request.form.get('is_bestseller') else 0

    cursor.execute(
        "UPDATE products SET name=?, description=?, category=?, price=?, is_bestseller=? WHERE product_id=?",
        (name, description, category, price, is_bestseller, item_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Product updated!", "success")
    return redirect('/admin/item-list')





# =================================================================
# UPDATED PRODUCT LIST WITH SEARCH + CATEGORY FILTER
# =================================================================
@app.route('/admin/item-list')
def item_list():

    if 'admin_id' not in session:
        flash("Please login!", "danger")
        return redirect('/admin-login')

    search = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1️⃣ Fetch category list for dropdown
    cursor.execute("SELECT DISTINCT category FROM products")
    categories = [dict(row) for row in cursor.fetchall()]

    # 2️⃣ Build dynamic query based on filters
    is_super = session.get('is_superadmin')
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if not is_super:
        query += " AND added_by = ?"
        params.append(session['admin_id'])

    if search:
        s_clean = search.replace(" ", "")
        query += " AND (REPLACE(name, ' ', '') LIKE ? OR name LIKE ?)"
        params.append("%" + s_clean + "%")
        params.append("%" + search + "%")

    if category_filter:
        query += " AND category = ?"
        params.append(category_filter)

    cursor.execute(query, params)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "admin/item_list.html",
        products=products,
        categories=categories
    )






#  ROUTE 2: Delete Product + Delete Image from Server
# =================================================================
# DELETE PRODUCT (DELETE DB ROW + DELETE IMAGE FILE)
# =================================================================
@app.route('/admin/delete-item/<int:item_id>')
def delete_item(item_id):

    if 'admin_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/admin-login')

    conn = get_db_connection()
    cursor = conn.cursor()

    # 1️⃣ Fetch product to get image name
    cursor.execute("SELECT image FROM products WHERE product_id=?", (item_id,))
    product = cursor.fetchone()

    if not product:
        flash("Product not found!", "danger")
        return redirect('/admin/item-list')

    image_name = product['image']

    # Delete image from folder
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_name)
    if os.path.exists(image_path):
        os.remove(image_path)

    # 2️⃣ Delete product from DB
    cursor.execute("DELETE FROM products WHERE product_id=?", (item_id,))
    conn.commit()

    cursor.close()
    conn.close()

    flash("Product deleted successfully!", "success")
    return redirect('/admin/item-list')



ADMIN_UPLOAD_FOLDER = 'static/uploads/admin_profiles'
app.config['ADMIN_UPLOAD_FOLDER'] = ADMIN_UPLOAD_FOLDER

USER_UPLOAD_FOLDER = 'static/uploads/user_profiles'
app.config['USER_UPLOAD_FOLDER'] = USER_UPLOAD_FOLDER






# Route 1: Show Admin Profile Page (GET)
# =================================================================
# ROUTE 1: SHOW ADMIN PROFILE DATA
# =================================================================
@app.route('/admin/profile', methods=['GET'])
def admin_profile():

    if 'admin_id' not in session:
        flash("Please login!", "danger")
        return redirect('/admin-login')

    admin_id = session['admin_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM admin WHERE admin_id = ?", (admin_id,))
    admin = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("admin/admin_profile.html", admin=admin)





# Route 2: Update Admin Profile (POST)
# This route updates name + email + password (optional) + image (optional).
# =================================================================
# ROUTE 2: UPDATE ADMIN PROFILE (NAME, EMAIL, PASSWORD, IMAGE)
# =================================================================
@app.route('/admin/profile', methods=['POST'])
def admin_profile_update():

    if 'admin_id' not in session:
        flash("Please login!", "danger")
        return redirect('/admin-login')

    admin_id = session['admin_id']

    # 1️⃣ Get form data
    name = request.form['name']
    email = request.form['email']
    new_password = request.form['password']
    new_image = request.files['profile_image']

    conn = get_db_connection()
    cursor = conn.cursor()

    # 2️⃣ Fetch old admin data
    cursor.execute("SELECT * FROM admin WHERE admin_id = ?", (admin_id,))
    admin = cursor.fetchone()

    old_image_name = admin['profile_image']

    # 3️⃣ Update password only if entered
    if new_password:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    else:
        hashed_password = admin['password']  # keep old password

    # 4️⃣ Process new profile image if uploaded
    if new_image and new_image.filename != "":
        
        from werkzeug.utils import secure_filename
        new_filename = secure_filename(new_image.filename)

        # Save new image
        image_path = os.path.join(app.config['ADMIN_UPLOAD_FOLDER'], new_filename)
        new_image.save(image_path)

        # Delete old image
        if old_image_name:
            old_image_path = os.path.join(app.config['ADMIN_UPLOAD_FOLDER'], old_image_name)
            if os.path.exists(old_image_path):
                os.remove(old_image_path)

        final_image_name = new_filename
    else:
        final_image_name = old_image_name

    # 5️⃣ Update database
    cursor.execute("""
        UPDATE admin
        SET name=?, email=?, password=?, profile_image=?
        WHERE admin_id=?
    """, (name, email, hashed_password, final_image_name, admin_id))

    conn.commit()
    cursor.close()
    conn.close()

    # Update session name for UI consistency
    session['admin_name'] = name  
    session['admin_email'] = email

    flash("Profile updated successfully!", "success")
    return redirect('/admin/profile')







#--------------------------------- USER CREDIENTIALS--------------------------------------------





#  ROUTE 1: User Registration (GET + POST)
# =================================================================
# ROUTE: USER REGISTRATION
# =================================================================
@app.route('/user-register', methods=['GET', 'POST'])
def user_register():

    # GET logic
    if request.method == 'GET':
        return render_template("user/user_register.html")

    # POST logic
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    phone = request.form.get('phone', '')
    address = request.form.get('address', '')
    city = request.form.get('city', '')
    pincode = request.form.get('pincode', '')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        flash("Email already registered! Try Logging in.", "danger")
        cursor.close()
        conn.close()
        return redirect('/user-login')

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insert user into database
    cursor.execute(
        "INSERT INTO users (name, email, password, phone, address, city, pincode) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, email, hashed_password, phone, address, city, pincode)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("Registration Successful! Please login.", "success")
    return redirect('/user-login')




#  ROUTE 2: User Login (GET + POST)
# =================================================================
# ROUTE: USER LOGIN
# =================================================================
@app.route('/user-login', methods=['GET', 'POST'])
def user_login():

    if request.method == 'GET':
        return render_template("user/user_login.html")

    email = request.form['email']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    bin_user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not bin_user:
        flash("Email not found! Please register.", "danger")
        return redirect('/user-login')

    user = dict(bin_user)

    # Verify password
    stored_hash = user['password']
    if isinstance(stored_hash, str):
        stored_hash = stored_hash.encode('utf-8')

    if not bcrypt.checkpw(password.encode('utf-8'), stored_hash):
        flash("Incorrect password!", "danger")
        return redirect('/user-login')

    # Create user session
    session['user_id'] = user['user_id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']

    flash("Login successful!", "success")
    return redirect('/user-dashboard')




# ROUTE 3: User Dashboard (Protected)
# =================================================================
# ROUTE: USER DASHBOARD
# =================================================================
@app.route('/user-dashboard')
def user_dashboard():

    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/user-login')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch products grouped by categories dynamically
    cursor.execute("SELECT DISTINCT category FROM products LIMIT 15")
    cats = cursor.fetchall()
    
    sections = []
    for cat_row in cats:
        cat_name = cat_row['category']
        cursor.execute("SELECT * FROM products WHERE category = ? ORDER BY is_bestseller DESC, product_id DESC LIMIT 4", (cat_name,))
        prods = cursor.fetchall()
        if prods:
            sections.append({'name': cat_name, 'products': prods})

    cursor.close()
    conn.close()

    return render_template(
        "user/user_home.html", 
        user_name=session['user_name'],
        sections=sections
    )




# ROUTE 4: User Logout
# =================================================================
# ROUTE: USER LOGOUT
# =================================================================
@app.route('/user-logout')
def user_logout():
    
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)

    flash("Logged out successfully!", "success")
    return redirect('/user-login')










# ROUTE 1: Display All Products for Users
# =================================================================
# ROUTE: USER PRODUCT LISTING (SEARCH + FILTER)
# =================================================================
@app.route('/user/products')
def user_products():

    # Optional: restrict only logged-in users
    if 'user_id' not in session:
        flash("Please login to view products!", "danger")
        return redirect('/user-login')

    search = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch categories for filter dropdown
    cursor.execute("SELECT DISTINCT category FROM products")
    categories = [dict(row) for row in cursor.fetchall()]

    # Build dynamic SQL
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if search:
        s_clean = search.replace(" ", "")
        query += " AND (REPLACE(name, ' ', '') LIKE ? OR name LIKE ?)"
        params.append("%" + s_clean + "%")
        params.append("%" + search + "%")

    if category_filter:
        query += " AND category = ?"
        params.append(category_filter)

    query += " ORDER BY is_bestseller DESC, product_id DESC"
    cursor.execute(query, params)
    products = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "user/user_products.html",
        products=products,
        categories=categories
    )

# ROUTE 2: Single Product Details Page
# =================================================================
# ROUTE: USER PRODUCT DETAILS PAGE
# =================================================================
@app.route('/user/product/<int:product_id>')
def user_product_details(product_id):

    if 'user_id' not in session:
        flash("Please login!", "danger")
        return redirect('/user-login')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
    product = cursor.fetchone()

    cursor.close()
    conn.close()

    if not product:
        flash("Product not found!", "danger")
        return redirect('/user/products')

    return render_template("user/product_details.html", product=product)



# ROUTE 1: Add to Cart
# =================================================================
# ADD ITEM TO CART
# =================================================================
@app.route('/user/add-to-cart/<int:product_id>')
def add_to_cart(product_id):

    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/user-login')

    # Create cart if doesn't exist
    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']

    # Get product
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id=?", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()

    if not product:
        flash("Product not found.", "danger")
        return redirect(request.referrer)

    pid = str(product_id)

    # If exists → increase quantity
    if pid in cart:
        cart[pid]['quantity'] += 1
    else:
        cart[pid] = {
            'name': product['name'],
            'price': float(product['price']),
            'image': product['image'],
            'quantity': 1
        }

    session['cart'] = cart

    flash("Item added to cart!", "success")
    return redirect(request.referrer)   # Return to same page




# ROUTE: BUY NOW (Add to Cart + Redirect to Cart)
# =================================================================
@app.route('/user/buy-now/<int:product_id>')
def buy_now(product_id):

    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/user-login')

    if 'cart' not in session:
        session['cart'] = {}

    cart = session['cart']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE product_id=?", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()

    if not product:
        flash("Product not found.", "danger")
        return redirect('/user/products')

    pid = str(product_id)
    if pid in cart:
        cart[pid]['quantity'] += 1
    else:
        cart[pid] = {
            'name': product['name'],
            'price': float(product['price']),
            'image': product['image'],
            'quantity': 1
        }

    session['cart'] = cart
    return redirect('/user/cart')




# ROUTE 2: View Cart Page
# =================================================================
# VIEW CART PAGE
# =================================================================
@app.route('/user/cart')
def view_cart():

    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/user-login')

    cart = session.get('cart', {})

    # Calculate total
    grand_total = sum(item['price'] * item['quantity'] for item in cart.values())

    return render_template("user/cart.html", cart=cart, grand_total=grand_total)




# ROUTE 3: Increase Quantity
# =================================================================
# INCREASE QUANTITY
# =================================================================
@app.route('/user/cart/increase/<pid>')
def increase_quantity(pid):

    cart = session.get('cart', {})

    if pid in cart:
        cart[pid]['quantity'] += 1

    session['cart'] = cart
    return redirect('/user/cart')



# ROUTE 4: Decrease Quantity
# =================================================================
# DECREASE QUANTITY
# =================================================================
@app.route('/user/cart/decrease/<pid>')
def decrease_quantity(pid):

    cart = session.get('cart', {})

    if pid in cart:
        cart[pid]['quantity'] -= 1

        # If quantity becomes 0 → remove item
        if cart[pid]['quantity'] <= 0:
            cart.pop(pid)

    session['cart'] = cart
    return redirect('/user/cart')



# ROUTE 5: Remove Item Completely
# =================================================================
# REMOVE ITEM
# =================================================================
@app.route('/user/cart/remove/<pid>')
def remove_from_cart(pid):

    cart = session.get('cart', {})

    if pid in cart:
        cart.pop(pid)

    session['cart'] = cart

    flash("Item removed!", "success")
    return redirect('/user/cart')


# =================================================================
# ROUTE: CHECKOUT & CREATE RAZORPAY ORDER
# =================================================================
@app.route('/user/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect('/user-login')

    user_id = session['user_id']
    cart = session.get('cart', {})
    if not cart:
        flash("Your cart is empty!", "warning")
        return redirect('/user/products')

    conn = get_db_connection()
    cursor = conn.cursor()

    # GET: Show address selection
    if request.method == 'GET':
        cursor.execute("SELECT * FROM user_addresses WHERE user_id = ? ORDER BY is_default DESC, address_id DESC", (user_id,))
        addresses = cursor.fetchall()
        cursor.close()
        conn.close()
        
        grand_total = sum(item['price'] * item['quantity'] for item in cart.values())
        return render_template("user/select_address.html", addresses=addresses, grand_total=grand_total)

    # POST: Process checkout with selected address
    address_id = request.form.get('address_id')
    if not address_id:
        flash("Please select a delivery address!", "warning")
        return redirect('/user/checkout')

    # Store selected address ID in session for payment_success
    session['selected_address_id'] = address_id

    grand_total = sum(item['price'] * item['quantity'] for item in cart.values())
    amount = int(grand_total * 100)
    
    data = {
        "amount": amount,
        "currency": "INR",
        "receipt": f"receipt_{random.randint(1000, 9999)}",
        "payment_capture": "1"
    }

    try:
        order = razorpay_client.order.create(data=data)
        cursor.close()
        conn.close()
        return render_template(
            "user/payment.html", 
            order=order, 
            key_id=config.RAZORPAY_KEY_ID,
            amount=amount,
            user_name=session['user_name'],
            user_email=session['user_email']
        )
    except Exception as e:
        cursor.close()
        conn.close()
        flash(f"Payment Gateways Error: {str(e)}", "danger")
        return redirect('/user/cart')


# =================================================================
# ROUTE: PAYMENT SUCCESS CALLBACK
# =================================================================
@app.route('/payment-success', methods=['POST'])
def payment_success():
    if 'user_id' not in session:
        return redirect('/user-login')

    # In a real app, verify signature using razorpay_client.utility.verify_payment_signature(params_dict)
    payment_id = request.form.get('razorpay_payment_id')
    order_id = request.form.get('razorpay_order_id')
    
    cart = session.get('cart', {})
    grand_total = sum(item['price'] * item['quantity'] for item in cart.values())
    user_id = session['user_id']

    # 1. Fetch address details for the order snapshot
    address_id = session.get('selected_address_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if address_id:
        cursor.execute("SELECT * FROM user_addresses WHERE address_id = ?", (address_id,))
        address_row = cursor.fetchone()
    else:
        # Fallback to user table if somehow address_id is missing
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        address_row = cursor.fetchone()

    # Convert row to dict for .get() support
    address_data = dict(address_row) if address_row else {}

    # 2. Save order to database with address snapshot
    cursor.execute(
        "INSERT INTO orders_table (user_id, amount, payment_id, address, city, pincode, phone) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, grand_total, payment_id, address_data.get('address_line', address_data.get('address')), address_data.get('city'), address_data.get('pincode'), address_data.get('phone'))
    )
    db_order_id = cursor.lastrowid

    # 3. Save items to database
    for pid, item in cart.items():
        cursor.execute(
            "INSERT INTO order_items_table (order_id, product_id, quantity) VALUES (?, ?, ?)",
            (db_order_id, pid, item['quantity'])
        )
    
    conn.commit()
    cursor.close()
    conn.close()

    # Send Payment Confirmation Email
    try:
        items_detail = ""
        for pid, item in cart.items():
            items_detail += f"- {item['name']} x {item['quantity']} : ₹{item['price'] * item['quantity']:,.2f}\n"

        # --- Send Confirmation Email with Invoice PDF ---
        try:
            pdf_buffer, filename = generate_invoice_pdf_data(db_order_id, session['user_id'])
            if pdf_buffer:
                msg = Message(
                    f"Payment Successful - Order #{db_order_id}",
                    sender=app.config['MAIL_USERNAME'],
                    recipients=[session['user_email']]
                )
                msg.body = f"""Dear {session['user_name']},

Your payment of ₹{grand_total:,.2f} for Order #{db_order_id} was successful.
Attached is your invoice for reference.

Payment ID: {payment_id}

Thank you for shopping with Elite Cart!"""
                msg.attach(filename, "application/pdf", pdf_buffer.read())
                mail.send(msg)
        except Exception as e:
            print(f"Error sending email: {e}")

        # Clear the cart
        session.pop('cart', None)
        flash("Payment Successful! Your order has been placed and a confirmation email with your invoice has been sent.", "success")
        return redirect(url_for('payment_confirmation', payment_id=payment_id, order_id=db_order_id))
    except Exception as e:
        print(f"Payment success error: {e}")
        return redirect('/user-dashboard')


@app.route('/order-confirmation')
def payment_confirmation():
    if 'user_id' not in session:
        return redirect('/user-login')
    
    payment_id = request.args.get('payment_id')
    order_id = request.args.get('order_id')
    
    if not payment_id or not order_id:
        return redirect('/user-dashboard')

    return render_template("user/payment_success.html", payment_id=payment_id, order_id=order_id)


# =================================================================
# ROUTE: USER PROFILE (GET + POST)
# =================================================================
@app.route('/user/profile', methods=['GET', 'POST'])
def user_profile():
    if 'user_id' not in session:
        return redirect('/user-login')

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        city = request.form['city']
        pincode = request.form['pincode']
        password = request.form['password']
        profile_image = request.files.get('profile_image')

        # Fetch existing user data
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_data = cursor.fetchone()
        old_image_name = user_data['profile_image']

        # Handle image upload
        final_image_name = old_image_name
        if profile_image and profile_image.filename:
            filename = secure_filename(profile_image.filename)
            profile_image.save(os.path.join(app.config['USER_UPLOAD_FOLDER'], filename))
            
            # Delete old image
            if old_image_name:
                old_image_path = os.path.join(app.config['USER_UPLOAD_FOLDER'], old_image_name)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            final_image_name = filename

        if password:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute("UPDATE users SET name=?, email=?, phone=?, address=?, city=?, pincode=?, password=?, profile_image=? WHERE user_id=?", 
                         (name, email, phone, address, city, pincode, hashed_password, final_image_name, user_id))
        else:
            cursor.execute("UPDATE users SET name=?, email=?, phone=?, address=?, city=?, pincode=?, profile_image=? WHERE user_id=?", 
                         (name, email, phone, address, city, pincode, final_image_name, user_id))
        
        conn.commit()
        session['user_name'] = name
        flash("Profile updated successfully!", "success")
        return redirect('/user/profile')

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()

    # Fetch addresses
    cursor.execute("SELECT * FROM user_addresses WHERE user_id = ? ORDER BY is_default DESC, address_id DESC", (user_id,))
    addresses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("user/user_profile.html", user=user, addresses=addresses)


# ---------------------------------------------------------
# ROUTE: USER ADD ADDRESS
# ---------------------------------------------------------
@app.route('/user/add-address', methods=['POST'])
def add_address():
    if 'user_id' not in session:
        return redirect('/user-login')

    user_id = session['user_id']
    address_line = request.form['address_line']
    city = request.form['city']
    pincode = request.form['pincode']
    phone = request.form['phone']

    conn = get_db_connection()
    cursor = conn.cursor()

    # If first address, make it default
    cursor.execute("SELECT COUNT(*) FROM user_addresses WHERE user_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    is_default = 1 if count == 0 else 0

    cursor.execute(
        "INSERT INTO user_addresses (user_id, address_line, city, pincode, phone, is_default) VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, address_line, city, pincode, phone, is_default)
    )
    conn.commit()
    cursor.close()
    conn.close()

    flash("New address added successfully!", "success")
    return redirect(request.form.get('next', '/user/profile'))


# ---------------------------------------------------------
# ROUTE: SET DEFAULT ADDRESS
# ---------------------------------------------------------
@app.route('/user/set-default-address/<int:address_id>')
def set_default_address(address_id):
    if 'user_id' not in session:
        return redirect('/user-login')

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    # Reset all default for this user
    cursor.execute("UPDATE user_addresses SET is_default = 0 WHERE user_id = ?", (user_id,))
    # Set this one as default
    cursor.execute("UPDATE user_addresses SET is_default = 1 WHERE address_id = ? AND user_id = ?", (address_id, user_id))

    conn.commit()
    cursor.close()
    conn.close()

    flash("Default address updated.", "success")
    return redirect('/user/profile')


# ---------------------------------------------------------
# ROUTE: DELETE ADDRESS
# ---------------------------------------------------------
@app.route('/user/delete-address/<int:address_id>')
def delete_address(address_id):
    if 'user_id' not in session:
        return redirect('/user-login')

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM user_addresses WHERE address_id = ? AND user_id = ?", (address_id, user_id))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Address deleted successfully!", "info")
    return redirect('/user/profile')


















# =================================================================
# ROUTE: USER ORDERS
# =================================================================
@app.route('/user/orders')
def user_orders():
    if 'user_id' not in session:
        return redirect('/user-login')

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch orders for this user
    cursor.execute("SELECT * FROM orders_table WHERE user_id = ? ORDER BY order_date DESC", (user_id,))
    orders_rows = cursor.fetchall()
    
    orders = []
    for row in orders_rows:
        order = dict(row)
        cursor.execute("""
            SELECT oi.*, p.name, p.image, p.price 
            FROM order_items_table oi 
            JOIN products p ON oi.product_id = p.product_id 
            WHERE oi.order_id = ?
        """, (order['order_id'],))
        order['items'] = cursor.fetchall()
        orders.append(order)
    
    cursor.close()
    conn.close()

    return render_template("user/user_orders.html", orders=orders)


# =================================================================
# HELPER: GENERATE INVOICE PDF DATA
# =================================================================
def generate_invoice_pdf_data(order_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.*, u.name as user_name, u.email as user_email 
        FROM orders_table o 
        JOIN users u ON o.user_id = u.user_id 
        WHERE o.order_id = ? AND o.user_id = ?
    """, (order_id, user_id))
    order = cursor.fetchone()
    if not order:
        return None, None
    cursor.execute("""
        SELECT oi.*, p.name as product_name, p.price 
        FROM order_items_table oi 
        JOIN products p ON oi.product_id = p.product_id 
        WHERE oi.order_id = ?
    """, (order_id,))
    items = cursor.fetchall()
    cursor.close()
    conn.close()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(200, 15, "Elite Cart Invoice", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(100, 10, f"Order ID: {order['order_id']}")
    pdf.cell(100, 10, f"Date: {order['order_date']}", ln=True, align='R')
    pdf.ln(5)
    pdf.cell(100, 10, f"Customer: {order['user_name']}")
    pdf.cell(100, 10, f"Email: {order['user_email']}", ln=True, align='R')
    pdf.ln(5)
    pdf.cell(100, 10, f"Payment ID: {order['payment_id']}")
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(200, 8, "Shipping Address:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 6, f"{order.get('address', 'N/A')}", ln=True)
    pdf.cell(200, 6, f"{order.get('city', 'N/A')} - {order.get('pincode', 'N/A')}", ln=True)
    pdf.cell(200, 6, f"Phone: {order.get('phone', 'N/A')}", ln=True)
    pdf.ln(10)
    pdf.set_fill_color(26, 86, 219)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(100, 10, " Product", 1, 0, 'L', True)
    pdf.cell(30, 10, " Qty", 1, 0, 'C', True)
    pdf.cell(30, 10, " Price", 1, 0, 'C', True)
    pdf.cell(30, 10, " Total", 1, 1, 'C', True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 11)
    for item in items:
        pdf.cell(100, 10, f" {item['product_name']}", 1)
        pdf.cell(30, 10, f" {item['quantity']}", 1, 0, 'C')
        pdf.cell(30, 10, f" INR {item['price']}", 1, 0, 'C')
        pdf.cell(30, 10, f" INR {item['price'] * item['quantity']}", 1, 1, 'C')
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 12, f"Grand Total: INR {order['amount']}", 0, 1, 'R')
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, "Thank you for shopping with Elite Cart!", 0, 0, 'C')
    output = io.BytesIO()
    pdf_content = pdf.output(dest='S')
    if isinstance(pdf_content, str):
        output.write(pdf_content.encode('latin-1'))
    else:
        output.write(pdf_content)
    output.seek(0)
    return output, f"Elite_Cart_Invoice_{order_id}.pdf"

# =================================================================
# ROUTE: DOWNLOAD INVOICE (PDF)
# =================================================================
@app.route('/user/download-invoice/<int:order_id>')
def download_invoice(order_id):
    if 'user_id' not in session:
        return redirect('/user-login')
    
    pdf_data, filename = generate_invoice_pdf_data(order_id, session['user_id'])
    if not pdf_data:
        flash("Order not found or unauthorized.", "danger")
        return redirect('/user-dashboard')

    return send_file(
        pdf_data,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )


# =================================================================
# ROUTE: SUPERADMIN - ADMIN APPROVAL PANEL
# =================================================================
@app.route('/admin/manage-admins')
def manage_admins():
    if 'admin_id' not in session or not session.get('is_superadmin'):
        flash("Unauthorized access!", "danger")
        return redirect('/admin-dashboard')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admin WHERE is_superadmin = 0")
    admins = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("admin/manage_admins.html", admins=admins)


# =================================================================
# ROUTE: SUPERADMIN - APPROVE ADMIN
# =================================================================
@app.route('/admin/approve/<int:target_id>')
def approve_admin(target_id):
    if 'admin_id' not in session or not session.get('is_superadmin'):
        flash("Unauthorized!", "danger")
        return redirect('/admin-dashboard')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE admin SET is_approved = 1 WHERE admin_id = ?", (target_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Admin approved successfully!", "success")
    return redirect('/admin/manage-admins')


# =================================================================
# ROUTE: SUPERADMIN - DELETE ADMIN
# =================================================================
@app.route('/admin/delete-admin/<int:target_id>')
def delete_admin(target_id):
    if 'admin_id' not in session or not session.get('is_superadmin'):
        flash("Unauthorized!", "danger")
        return redirect('/admin-dashboard')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admin WHERE admin_id = ?", (target_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash("Admin access denied and account removed.", "info")
    return redirect('/admin/manage-admins')


# =================================================================
# FORGOT PASSWORD LOGIC (FOR BOTH USERS & ADMINS)
# =================================================================

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        role = request.args.get('role', 'user')
        session['reset_role'] = role
        return render_template('user/forgot_password.html', role=role)
    
    email = request.form['email']
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Check in both tables
    cursor.execute("SELECT email FROM admin WHERE email = ?", (email,))
    admin = cursor.fetchone()
    cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if not admin and not user:
        flash("Email address not found in our records!", "danger")
        cursor.close()
        conn.close()
        return redirect('/forgot-password')
    
    # 2. Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    print(f"DEBUG: Generated OTP for {email} is {otp}")
    
    # 3. Save OTP in database
    cursor.execute("INSERT INTO otp_reset (email, otp) VALUES (?, ?)", (email, otp))
    conn.commit()
    cursor.close()
    conn.close()
    
    # 4. Send Email
    try:
        msg = Message(
            subject="SmartCart - Password Reset OTP",
            sender=app.config.get('MAIL_DEFAULT_SENDER'),
            recipients=[email]
        )
        msg.body = f"Hello,\n\nYou requested a password reset for your SmartCart account.\nYour 6-digit OTP is: {otp}\n\nThis OTP is valid for 10 minutes. If you did not request this, please ignore this email.\n\nBest Regards,\nSmartCart Team"
        mail.send(msg)
        
        session['reset_email'] = email
        flash(f"A 6-digit OTP has been successfully sent to {email}.", "info")
        return redirect('/verify-otp')
    except Exception as e:
        error_msg = str(e)
        print(f"MAIL ERROR: {error_msg}")
        
        # Friendly suggestion for common Gmail 535 error
        if "(535," in error_msg:
            flash("Authentication Failed! Please ensure you are using a correct 16-character 'Gmail App Password' (without spaces).", "danger")
        else:
            safe_error = error_msg.replace(otp, "[OTP]")
            flash(f"Email Error: {safe_error}", "danger")
        return redirect('/forgot-password')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if 'reset_email' not in session:
        return redirect('/forgot-password')
        
    if request.method == 'GET':
        return render_template('user/verify_otp.html', email=session['reset_email'], role=session.get('reset_role', 'user'))
    
    otp_entered = request.form['otp']
    email = session['reset_email']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    # Fetch most recent unused OTP for this email
    cursor.execute("""
        SELECT * FROM otp_reset 
        WHERE email = ? AND otp = ? AND is_used = 0 
        AND created_at >= datetime('now', '-10 minutes')
        ORDER BY id DESC LIMIT 1
    """, (email, otp_entered))
    otp_row = cursor.fetchone()
    
    if otp_row:
        # Mark OTP as used immediately
        cursor.execute("UPDATE otp_reset SET is_used = 1 WHERE id = ?", (otp_row['id'],))
        conn.commit()
        cursor.close()
        conn.close()
        
        session['otp_verified'] = True
        return redirect('/reset-password')
    else:
        cursor.close()
        conn.close()
        flash("Invalid OTP! Please check your email and try again.", "danger")
        return redirect('/verify-otp')

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if not session.get('otp_verified') or 'reset_email' not in session:
        flash("Unauthorized access. Please start the reset process again.", "danger")
        return redirect('/forgot-password')
        
    if request.method == 'GET':
        return render_template('user/reset_password.html', role=session.get('reset_role', 'user'))
    
    password = request.form['password']
    confirm = request.form['confirm_password']
    
    if password != confirm:
        flash("Passwords do not match!", "danger")
        return redirect('/reset-password')
    
    email = session['reset_email']
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update across all relevant tables
    cursor.execute("UPDATE admin SET password = ? WHERE email = ?", (hashed_pw, email))
    cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_pw, email))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash("Password changed successfully. Please login again.", "success")
    role = session.pop('reset_role', 'user')
    session.pop('reset_email', None)
    session.pop('otp_verified', None)
    
    if role == 'admin':
        return redirect('/admin-login')
    return redirect('/user-login')


if __name__ == '__main__':
    app.run(debug=True)








# if __name__ == '__main__':
#     app.run(debug=True)