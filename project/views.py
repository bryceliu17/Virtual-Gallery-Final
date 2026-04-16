from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session, abort, current_app 
)
from functools import wraps
from datetime import datetime
import uuid
import re

# Data layer imports
from . import mysql
from .db import (
    get_all_artworks, get_artwork_by_id, search_artworks,
    insert_artwork, delete_artwork, list_artists, list_categories, get_artworks_by_artist
)
from .models import User, Artist, Order, OrderItem, Payment
from .forms import RegisterForm, LoginForm, CheckoutForm
import os
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    """Checks if a file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

bpView = Blueprint('view', __name__)

# Auth decorators
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("view.login", next=request.path))
        return f(*args, **kwargs)
    return wrapper

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in.", "warning")
                return redirect(url_for("view.login", next=request.path))
            if session.get("role") not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Public pages
@bpView.route("/")
def home():
    cur = mysql.connection.cursor()
    cur.execute(
        """
        SELECT
          a.artworkId, a.title, a.imageUrl,
          COALESCE(a.pricePerMonth,0) AS pricePerMonth,
          a.description,
          ar.name AS artistName, c.name AS categoryName, m.name AS mediumName
        FROM artwork a
        LEFT JOIN artist   ar ON a.artistId   = ar.artistId
        LEFT JOIN category c  ON a.categoryId = c.categoryId
        LEFT JOIN medium   m  ON a.mediumId   = m.mediumId
        ORDER BY a.createdAt DESC, a.artworkId DESC
        LIMIT 4
    """
    )
    rows = cur.fetchall()

    cur.execute("SELECT name FROM artist ORDER BY name")
    artists = [r["name"] for r in cur.fetchall()]
    cur.execute("SELECT name FROM category ORDER BY name")
    categories = [r["name"] for r in cur.fetchall()]
    cur.close()

    artworks = [{
        "id": r["artworkId"],
        "title": r["title"],
        "artist": r["artistName"],
        "category": r["categoryName"],
        "medium": r.get("mediumName"),
        "price_per_month": float(r["pricePerMonth"] or 0),
        "desc": r["description"],
        "img": r["imageUrl"],
    } for r in rows]

    return render_template(
        "index.html",
        artworks=artworks,
        artists=artists,
        categories=categories,
    )

@bpView.route("/gallery")
def gallery():
    q         = (request.args.get("q") or "").strip()
    artist    = (request.args.get("artist") or "").strip()
    category  = (request.args.get("category") or "").strip()
    max_price = request.args.get("max_price", type=float)

    sql = """
      SELECT
        a.artworkId, a.title, a.imageUrl,
        COALESCE(a.pricePerMonth,0) AS pricePerMonth,
        a.description,
        ar.name AS artistName, c.name AS categoryName, m.name AS mediumName
      FROM artwork a
      LEFT JOIN artist   ar ON a.artistId   = ar.artistId
      LEFT JOIN category c  ON a.categoryId = c.categoryId
      LEFT JOIN medium   m  ON a.mediumId   = m.mediumId
      WHERE 1=1
    """
    params = []
    if q:
        kw = f"%{q.lower()}%"
        sql += " AND (LOWER(a.title) LIKE %s OR LOWER(IFNULL(a.description,'')) LIKE %s)"
        params += [kw, kw]
    if artist:
        sql += " AND ar.name = %s"
        params.append(artist)
    if category:
        sql += " AND c.name = %s"
        params.append(category)
    if max_price is not None:
        sql += " AND a.pricePerMonth <= %s"
        params.append(max_price)
    sql += " ORDER BY a.artworkId"

    cur = mysql.connection.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()

    cur.execute("SELECT name FROM artist ORDER BY name")
    artists = [r["name"] for r in cur.fetchall()]
    cur.execute("SELECT name FROM category ORDER BY name")
    categories = [r["name"] for r in cur.fetchall()]
    cur.close()

    artworks = [{
        "id": r["artworkId"],
        "title": r["title"],
        "artist": r["artistName"],
        "category": r["categoryName"],
        "medium": r.get("mediumName"),
        "price_per_month": float(r["pricePerMonth"] or 0),
        "desc": r["description"],
        "img": r["imageUrl"],
    } for r in rows]

    return render_template(
        "vendor_gallery.html",
        artworks=artworks,
        artists=artists,
        categories=categories,
    )

@bpView.route("/item/<int:aid>")
def item_details(aid):
    art = get_artwork_by_id(aid)
    if not art:
        abort(404)
    return render_template("item_details.html", art=art)

# Vendor management
@bpView.route("/vendor/manage")
@login_required
@roles_required("artist", "admin")
def vendor_manage():
    user_id = session.get("user_id")
    user_role = session.get("role") # Get the user's role
    artworks = []
    #If user is admin, get all artworks
    if user_role == "admin":
        artworks = get_all_artworks() 
    #If user is artist, get the artworks belong to the artist    
    elif user_role == "artist":
        artist_record = Artist.get_by_user(user_id) 
        artist_id = artist_record.get('artistId') if artist_record else None
        
        if artist_id:
            artworks = get_artworks_by_artist(artist_id) 
        if not artist_id:
             flash("Error: Could not find Artist ID associated with your user account. Please check your profile.", "danger")

    artists = list_artists()      
    categories = list_categories()   
    return render_template(
        "vendor_management.html",
        artworks=artworks,
        artists=artists,
        categories=categories,
    )

@bpView.route("/vendor/create", methods=["POST"])
@login_required
@roles_required("artist", "admin")
def vendor_create():

    title = (request.form.get("title") or "").strip()
    category_id = request.form.get("categoryId", type=int) 
    medium_id = request.form.get("mediumId", type=int) 
    desc = (request.form.get("desc") or "").strip()
    price_raw = (request.form.get("price_per_month") or "").strip()
    price = float(price_raw)
    user_id = session.get("user_id")
    artist_id = None
    
    if user_id:
        artist_record = Artist.get_by_user(user_id) 
        if artist_record:
            artist_id = artist_record['artistId']
    if not title or not artist_id or not category_id or not price_raw or artist_id <= 0 or category_id <= 0:
        flash("Title, Artist ID (from user), Category selection, and Price are required. Please select a Category.", "danger")        
        if not artist_id and not session.get('role') == 'artist':
            flash("Error: Could not find Artist ID associated with your user account. Please check your profile.", "danger")            
        return redirect(url_for("view.vendor_manage"))

    img_url = "img/placeholder.png" # Default URL 

    # Check if a file was uploaded under the name 'image_file' from the HTML form
    if 'image_file' in request.files:
        file = request.files['image_file']
        if file.filename != '' and allowed_file(file.filename):
            try:
                filename = secure_filename(file.filename)
                upload_dir = os.path.join(current_app.root_path, current_app.config['UPLOAD_FOLDER'])
                os.makedirs(upload_dir, exist_ok=True) 
                file_path = os.path.join(upload_dir, filename)
                file.save(file_path)
                img_url = os.path.join('uploads', filename).replace('\\', '/')
            except Exception as e:
                flash(f"File upload failed")
                return redirect(url_for("view.vendor_manage"))
        else:
            flash("Invalid file type.")
            return redirect(url_for("view.vendor_manage"))            
    # Use the retrieved IDs and the final img_url
    insert_artwork(title, artist_id, category_id, img_url, desc, price, medium_id)
    flash("Artwork added successfully.")
    return redirect(url_for("view.vendor_manage"))

@bpView.route("/vendor/delete/<int:aid>", methods=["POST"])
@login_required
@roles_required("artist", "admin")
def vendor_delete(aid):
    success = delete_artwork(aid)
    flash("Artwork removed." if success else "Artwork not found.")
    return redirect(url_for("view.vendor_manage"))

# Cart & checkout 
def _get_basket():
    return session.get("basket", {})

def _save_basket(basket):
    session["basket"] = basket
    session.modified = True

def _basket_view():
    items, grand_total = [], 0
    basket = _get_basket()
    if not basket:
        return items, grand_total

    for sid, months in basket.items():
        try:
            aid = int(sid)
        except ValueError:
            continue
        art = get_artwork_by_id(aid)
        if not art:
            continue
        # Note: All items are leased/rented (price_per_month is used)
        line_total = (months or 0) * (art.get("price_per_month") or 0)
        grand_total += line_total
        items.append({"art": art, "months": months, "line_total": line_total})
    return items, grand_total

@bpView.route("/cart/add/<int:aid>")
def cart_add(aid):
    basket = _get_basket()
    # If the item is already in the cart, do nothing to the month count here, 
    # as item_details has the proper form for adding.
    if str(aid) not in basket:
        basket[str(aid)] = 1 # Set default to 1 month if adding from gallery/direct link
    session.pop('last_order_confirmation', None)
    _save_basket(basket)
    flash("Item added to cart.")
    return redirect(url_for("view.checkout")) # Redirect to checkout now that cart is a page

@bpView.route("/cart/remove/<int:aid>")
def cart_remove(aid):
    basket = _get_basket()
    basket.pop(str(aid), None)
    _save_basket(basket)
    flash("Item removed from cart.")
    return redirect(url_for("view.checkout"))

@bpView.route("/cart")
def cart_view():
    # Since the basket is shown only on the checkout page, we redirect there
    return redirect(url_for("view.checkout"))

@bpView.route("/checkout", methods=["GET", "POST"])
def checkout():
    items, grand_total = _basket_view()

    if request.method == "GET":
        last_order = session.get('last_order_confirmation')
        if last_order:
            return render_template("checkout.html", order=last_order)
        return render_template("checkout.html", items=items, grand_total=grand_total)

    if not items:
        flash("Your basket is empty", "error")
        return redirect(url_for("view.gallery")) # Redirect to gallery on empty cart post

    # Collect form fields
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    phone = (request.form.get("phone") or "").strip()
    address = (request.form.get("address") or "").strip()
    # Collect payment information
    payment_method = request.form.get("payment_method")
    paypal_email = (request.form.get("paypal_email") or "").strip()

    # Payment-specific inputs
    card_number = (request.form.get("card_number") or "").replace(" ", "")
    card_expiry = (request.form.get("card_expiry") or "").strip()
    card_cvv = (request.form.get("card_cvv") or "").strip()
    paypal_password = (request.form.get("paypal_password") or "").strip()

    errors = []
    if not name:
        errors.append("Full name is required")
    else:
        if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ'\-]{2,}(?:\s+[A-Za-zÀ-ÖØ-öø-ÿ'\-]{2,})+$", name):
            errors.append("Full name must include first name and last name with a space, letters only")
    if not (email):
        errors.append("Email is required")
    if email:
        if "@" not in email or "." not in email:
            errors.append("Please enter a valid email address")
    if phone:
        if not re.match(r'^04\d{8}$', phone):
            errors.append("Phone must be an Australian mobile number (10 digits starting with 04)")
    if not address:
        errors.append("Delivery address is required")
    else:
        if not re.match(r'.*\s\d{4}$', address):
            errors.append("Delivery address must end with a 4-digit postcode (e.g. Suburb 4000)")
    if not payment_method:
        errors.append("Please select a payment method")

    # Payment-specific validation
    if payment_method == 'credit_card':
        if not card_number or not re.match(r'^\d{16}$', card_number):
            errors.append("Credit card number must be exactly 16 digits (enter without spaces)")
        if not card_expiry or not re.match(r'^(0[1-9]|1[0-2])\/\d{2}$', card_expiry):
            errors.append("Expiry must be in MM/YY format (e.g. 12/25)")
        if not card_cvv or not re.match(r'^\d{3}$', card_cvv):
            errors.append("CVV must be exactly 3 digits")
    elif payment_method == 'paypal':
        if not paypal_email:
            errors.append("PayPal email is required")
        else:
            if "@" not in paypal_email or "." not in paypal_email:
                errors.append("Please enter a valid PayPal email address")
        if not paypal_password or len(paypal_password) < 6:
            errors.append("PayPal password is required (minimum 6 characters)")

    if errors:
        for e in errors:
            flash(e, "error")
        return render_template(
            "checkout.html",
            items=items,
            grand_total=grand_total,
            form={"name": name, "email": email, "phone": phone, "address": address, "payment_method": payment_method, "paypal_email": paypal_email},
        )

    # Build order summary
    order = {
        "id": uuid.uuid4().hex[:8].upper(),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "customer": {"name": name, "email": email, "phone": phone, "address": address},
        "items": items,
        "total": grand_total,
        "payment_method": payment_method,
    }
    
    # Add PayPal email to order if provided
    if payment_method == 'paypal' and paypal_email:
        order['paypal_email'] = paypal_email
    session['last_order_confirmation'] = order
    session.pop("basket", None)
    session.modified = True

    flash(f"Order submitted successfully!", "success") 
    return redirect(url_for("view.checkout")) 

@bpView.route("/checkout/add/<int:aid>", methods=["GET", "POST"])
def checkout_add(aid):
    months = request.form.get("months", type=int)
    if months is None:
        months = request.args.get("months", type=int)
    if not months or months <= 0:
        flash("Please choose a lease duration (months).")
        return redirect(url_for("view.item_details", aid=aid))

    basket = _get_basket()
    basket[str(aid)] = months
    session.pop('last_order_confirmation', None)
    _save_basket(basket)

    flash("Added to basket.")
    return redirect(url_for("view.checkout"))


@bpView.route("/checkout/update/<int:aid>", methods=["POST"])
def checkout_update(aid):
    months = request.form.get("months", type=int)
    if not months or months <= 0:
        flash("Months must be a positive number.")
        return redirect(url_for("view.checkout"))

    basket = _get_basket()
    basket[str(aid)] = months
    _save_basket(basket)
    return redirect(url_for("view.checkout"))

@bpView.route("/checkout/remove/<int:aid>", methods=["GET", "POST"])
def checkout_remove(aid):
    basket = _get_basket()
    basket.pop(str(aid), None)
    _save_basket(basket)
    return redirect(url_for("view.checkout"))

@bpView.route("/checkout/clear", methods=["GET", "POST"])
def checkout_clear():
    session.pop("basket", None)
    session.modified = True
    return redirect(url_for("view.checkout"))

# Auth routes 
#Register
@bpView.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.get_by_email(form.email.data):
            flash("Email is already registered.", "danger")
            return render_template("auth_register.html", form=form), 400
        try:
            user_id = User.create(
                name=form.name.data.strip(),
                email=form.email.data.strip(),
                password=form.password.data,
                role=form.role.data,
                phone=form.phone.data.strip() if form.phone.data else None,
            )
            if form.role.data == "artist":
                Artist.create(userId=user_id, name=form.name.data.strip())
            flash("Registration successful. Please sign in.", "success")
            return redirect(url_for("view.login"))
        except Exception:
            flash("Registration failed. Please try again.", "danger")
            return render_template("auth_register.html", form=form), 500
    return render_template("auth_register.html", form=form)

#Login 
@bpView.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if not user:
            flash("No account found for that email.")
            return render_template("auth_login.html", form=form)
        if not User.verify_password(user["passwordHash"], form.password.data):
            flash("Incorrect password.")
            return render_template("auth_login.html", form=form)

        session["user_id"] = user["userId"]
        session["name"] = user["name"]
        session["role"] = user["role"]

        flash("Welcome back, " + user["name"] + "!")
        return redirect(url_for("view.home"))

    return render_template("auth_login.html", form=form)

@bpView.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.")
    return redirect(url_for("view.home"))

# Admin
@bpView.route("/admin", endpoint="admin_dashboard")
@login_required
@roles_required("admin")
def admin_panel():
    artist_count = Artist.count_all()
    order_count = Order.count_all()
    all_artists = Artist.list_all()
    submitted_orders = Order.list_submitted()
    return render_template(
        "dashboard.html",
        artist_count=artist_count,
        order_count=order_count,
        all_artists=all_artists,
        submitted_orders=submitted_orders,
    )

@bpView.errorhandler(403)
def forbidden(_):
    user_name = session.get("name")
    return render_template("403.html",user_name=user_name), 403

@bpView.route("/trigger_500")
def trigger_500():
    return 1 / 0

#Portfolio page
@bpView.route("/artists")
def artist_portfolio():
    cur = mysql.connection.cursor()
    cur.execute("""
      SELECT artistId AS id, name, imageUrl AS image,
             specialty, bio, medium, style, experienceYears, location
      FROM artist
      ORDER BY name
    """)
    artists = cur.fetchall()
    cur.close()
    return render_template("artist_portfolio.html", artists=artists)

@bpView.route("/artist/<int:artist_id>")
def artist_detail(artist_id):
    cur = mysql.connection.cursor()
    cur.execute("""
      SELECT artistId AS id, name, imageUrl AS image,
             specialty, bio, medium, style, experienceYears, location
      FROM artist
      WHERE artistId = %s
    """, (artist_id,))
    artist = cur.fetchone()
    if not artist:
        abort(404)

    cur.execute("""
      SELECT artworkId AS id, title, imageUrl AS img,
             COALESCE(pricePerMonth,0) AS price_per_month
      FROM artwork
      WHERE artistId = %s
      ORDER BY artworkId DESC
    """, (artist_id,))
    artworks = cur.fetchall()
    cur.close()

    return render_template("artist_detail.html", artist=artist, artworks=artworks)