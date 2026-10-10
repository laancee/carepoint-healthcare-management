import os
from datetime import datetime
from functools import wraps

from bson.objectid import ObjectId
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-development-key")
MONGO_URI = os.getenv("MONGO_URI", "")
DB_NAME = os.getenv("MONGO_DB_NAME", "healthcare_management")

client = None
db = None
patients = None
users = None

if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        db = client[DB_NAME]
        patients = db["patients"]
        users = db["users"]
        users.create_index("username", unique=True)
    except PyMongoError as exc:
        print("MongoDB connection error:", exc)
        client = None
        db = None
        patients = None
        users = None


def database_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if db is None:
            flash("Database is not connected. Check MONGO_URI in your .env file.", "danger")
            return render_template("database_error.html"), 503
        return view(*args, **kwargs)
    return wrapped


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to continue.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def parse_patient_form(form):
    """Return patient data after basic validation. Use fictional data for school demos."""
    name = form.get("name", "").strip()
    age_text = form.get("age", "").strip()
    sex = form.get("sex", "").strip()
    phone = form.get("phone", "").strip()
    email = form.get("email", "").strip()
    blood_type = form.get("blood_type", "").strip()
    allergies = form.get("allergies", "").strip()
    medical_notes = form.get("medical_notes", "").strip()

    if not name:
        raise ValueError("Patient name is required.")
    try:
        age = int(age_text)
        if age < 0 or age > 125:
            raise ValueError
    except ValueError:
        raise ValueError("Age must be a number between 0 and 125.")

    if sex not in ("Female", "Male", "Prefer not to say"):
        raise ValueError("Please select a valid sex option.")
    if blood_type not in ("Unknown", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"):
        raise ValueError("Please select a valid blood type.")

    return {
        "name": name,
        "age": age,
        "sex": sex,
        "phone": phone,
        "email": email,
        "blood_type": blood_type,
        "allergies": allergies,
        "medical_notes": medical_notes,
        "updated_at": datetime.utcnow(),
    }


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
@database_required
def register():
    # For a school/demo deployment, the first user can register.
    # Disable public registration after creating authorized staff accounts.
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if len(username) < 3:
            flash("Username must contain at least 3 characters.", "danger")
        elif len(password) < 8:
            flash("Password must contain at least 8 characters.", "danger")
        elif password != confirm_password:
            flash("Passwords do not match.", "danger")
        else:
            try:
                users.insert_one({
                    "username": username,
                    "password_hash": generate_password_hash(password),
                    "created_at": datetime.utcnow(),
                })
                flash("Account created. You can now sign in.", "success")
                return redirect(url_for("login"))
            except Exception:
                flash("That username may already exist. Try another.", "danger")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
@database_required
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = users.find_one({"username": username})
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = str(user["_id"])
            session["username"] = user["username"]
            session.permanent = True
            flash("Welcome back.", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("You have signed out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
@database_required
def dashboard():
    total = patients.count_documents({})
    recent = list(patients.find().sort("updated_at", -1).limit(5))
    return render_template("dashboard.html", total=total, recent=recent)


@app.route("/patients")
@login_required
@database_required
def patient_list():
    query = request.args.get("q", "").strip()
    filter_query = {}
    if query:
        filter_query = {"name": {"$regex": query, "$options": "i"}}
    records = list(patients.find(filter_query).sort("name", 1).limit(250))
    return render_template("patients.html", patients=records, query=query)


@app.route("/patients/new", methods=["GET", "POST"])
@login_required
@database_required
def patient_new():
    if request.method == "POST":
        try:
            record = parse_patient_form(request.form)
            record["created_at"] = datetime.utcnow()
            record["created_by"] = session.get("username", "staff")
            patients.insert_one(record)
            flash("Patient record added.", "success")
            return redirect(url_for("patient_list"))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("patient_form.html", patient=None, page_title="Add patient")


@app.route("/patients/<patient_id>")
@login_required
@database_required
def patient_detail(patient_id):
    try:
        patient = patients.find_one({"_id": ObjectId(patient_id)})
    except Exception:
        patient = None
    if not patient:
        flash("Patient record was not found.", "warning")
        return redirect(url_for("patient_list"))
    return render_template("patient_detail.html", patient=patient)


@app.route("/patients/<patient_id>/edit", methods=["GET", "POST"])
@login_required
@database_required
def patient_edit(patient_id):
    try:
        object_id = ObjectId(patient_id)
        patient = patients.find_one({"_id": object_id})
    except Exception:
        patient = None
        object_id = None
    if not patient:
        flash("Patient record was not found.", "warning")
        return redirect(url_for("patient_list"))

    if request.method == "POST":
        try:
            updated = parse_patient_form(request.form)
            patients.update_one({"_id": object_id}, {"$set": updated})
            flash("Patient record updated.", "success")
            return redirect(url_for("patient_detail", patient_id=patient_id))
        except ValueError as exc:
            flash(str(exc), "danger")
    return render_template("patient_form.html", patient=patient, page_title="Edit patient")


@app.route("/patients/<patient_id>/delete", methods=["POST"])
@login_required
@database_required
def patient_delete(patient_id):
    try:
        result = patients.delete_one({"_id": ObjectId(patient_id)})
        if result.deleted_count:
            flash("Patient record deleted.", "success")
        else:
            flash("Patient record was not found.", "warning")
    except Exception:
        flash("Invalid patient record ID.", "danger")
    return redirect(url_for("patient_list"))


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    # Debug is for local development only. Use a production WSGI server when deployed.
    app.run(debug=True)
