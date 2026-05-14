from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_mail import Mail, Message
from itsdangerous import SignatureExpired, BadSignature, URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

# ---------------- APP ----------------

app = Flask(__name__)
app.secret_key = "secret123"

DATABASE = "company.db"

# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role     TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS employee (
                eid     INTEGER PRIMARY KEY AUTOINCREMENT,
                ename   TEXT    NOT NULL,
                edept   TEXT    NOT NULL,
                esalary REAL    NOT NULL,
                ephone  TEXT    NOT NULL
            );
        ''')

with app.app_context():
    init_db()

# ---------------- MAIL CONFIGURATION ----------------

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'subhashklvs@gmail.com'
app.config['MAIL_PASSWORD'] = 'xlgz oujn trco kqai'

mail = Mail(app)

# ---------------- TOKEN SERIALIZER ----------------

s = URLSafeTimedSerializer(app.secret_key)

# =========================================================
# REGISTER
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        uname = request.form["username"]
        pwd   = generate_password_hash(request.form["password"])
        role  = request.form["role"]

        try:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                    (uname, pwd, role)
                )
            flash("Registration successful! Please login.", "success")
            return redirect("/")
        except sqlite3.IntegrityError:
            flash("Username already exists.", "danger")
            return redirect("/register")

    return render_template("register.html")

# =========================================================
# LOGIN
# =========================================================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["username"]
        pwd   = request.form["password"]

        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ?", (uname,)
            ).fetchone()

        if user and check_password_hash(user["password"], pwd):
            session["admin"] = uname
            flash("Login successful!", "success")
            return redirect("/dashboard")
        else:
            flash("Invalid username or password!", "danger")
            return render_template("login.html")

    return render_template("login.html")

# =========================================================
# FORGOT PASSWORD
# =========================================================

@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        token = s.dumps(email, salt='password-reset-salt')
        reset_url = url_for('reset_password', token=token, _external=True)

        msg = Message(
            'Password Reset Request',
            sender='subhashklvs@gmail.com',
            recipients=[email]
        )
        msg.body = f'Click the link below to reset your password:\n\n{reset_url}'
        mail.send(msg)

        flash("Reset link sent successfully!", "success")
        return redirect("/forgot")

    return render_template('forgot.html')

# =========================================================
# RESET PASSWORD
# =========================================================

@app.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=300)
    except SignatureExpired:
        flash("Reset link expired!", "danger")
        return redirect("/forgot")
    except BadSignature:
        flash("Invalid reset link!", "danger")
        return redirect("/forgot")

    if request.method == 'POST':
        new_password = generate_password_hash(request.form['password'])
        with get_db() as conn:
            conn.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (new_password, email)
            )
        flash("Password updated successfully!", "success")
        return redirect("/")

    return render_template('reset_password.html')

# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():
    if "admin" not in session:
        return redirect("/")
    return render_template("dashboard.html")

# =========================================================
# ADD EMPLOYEE
# =========================================================

@app.route("/add", methods=["GET", "POST"])
def add():
    if "admin" not in session:
        return redirect("/")

    if request.method == "POST":
        with get_db() as conn:
            conn.execute(
                "INSERT INTO employee (ename, edept, esalary, ephone) VALUES (?, ?, ?, ?)",
                (
                    request.form["ename"],
                    request.form["edept"],
                    request.form["esalary"],
                    request.form["ephone"]
                )
            )
        flash("Employee added successfully!", "success")
        return redirect("/view")

    return render_template("add_employee.html")

# =========================================================
# VIEW EMPLOYEES
# =========================================================

@app.route("/view")
def view():
    if "admin" not in session:
        return redirect("/")

    search_query = request.args.get("q", "")
    
    with get_db() as conn:
        if search_query:
            data = conn.execute(
                "SELECT * FROM employee WHERE ename LIKE ? OR edept LIKE ? OR ephone LIKE ?", 
                (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%")
            ).fetchall()
        else:
            data = conn.execute("SELECT * FROM employee").fetchall()

    # Convert to plain tuples so templates work with e[0], e[1] etc.
    employees = [tuple(row) for row in data]

    return render_template("view_employee.html", employees=employees)

# =========================================================
# EDIT EMPLOYEE
# =========================================================

@app.route("/edit/<eid>")
def edit(eid):
    if "admin" not in session:
        return redirect("/")

    with get_db() as conn:
        emp = conn.execute(
            "SELECT * FROM employee WHERE eid = ?", (eid,)
        ).fetchone()

    return render_template("edit_employee.html", emp=tuple(emp))

# =========================================================
# UPDATE EMPLOYEE
# =========================================================

@app.route("/update", methods=["POST"])
def update():
    if "admin" not in session:
        return redirect("/")

    try:
        original_eid = int(request.form["original_eid"])
        new_eid      = int(request.form["eid"])
    except (KeyError, ValueError):
        flash("Invalid Employee ID!", "danger")
        return redirect("/view")

    try:
        with get_db() as conn:
            conn.execute(
                """
                UPDATE employee
                SET eid=?, ename=?, edept=?, esalary=?, ephone=?
                WHERE eid=?
                """,
                (
                    new_eid,
                    request.form["ename"],
                    request.form["edept"],
                    request.form["esalary"],
                    request.form["ephone"],
                    original_eid
                )
            )
        flash("Employee updated successfully!", "success")
    except sqlite3.Error as err:
        flash(f"Update failed: {err}", "danger")
        return redirect(f"/edit/{original_eid}")

    return redirect("/view")

# =========================================================
# DELETE EMPLOYEE
# =========================================================

@app.route("/delete/<eid>", methods=["POST"])
def delete(eid):
    if "admin" not in session:
        return redirect("/")

    with get_db() as conn:
        conn.execute("DELETE FROM employee WHERE eid = ?", (eid,))

    flash("Employee deleted successfully!", "danger")
    return redirect("/view")

# =========================================================
# ABOUT
# =========================================================

@app.route("/about")
def about():
    return render_template("about.html")

# =========================================================
# CONTACT
# =========================================================

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name")
        phone = request.form.get("phone")
        email = request.form.get("email")
        user_message = request.form.get("message")

        try:
            msg = Message(
                f'New Contact Message from {name}',
                sender='subhashklvs@gmail.com',
                recipients=['subhashklvs@gmail.com']
            )
            msg.body = f"Name: {name}\nEmail: {email}\nPhone: {phone}\n\nMessage:\n{user_message}"
            mail.send(msg)
            flash("Message sent successfully!", "success")
        except Exception as e:
            flash(f"An error occurred while sending the message: {e}", "danger")
            
        return redirect("/contact")
    return render_template("contact.html")

# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect("/")

# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
    

