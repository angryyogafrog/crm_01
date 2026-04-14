from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restx import Api, Resource, fields
from werkzeug.utils import secure_filename
from models import db, User, Customer, Lead
import os
import io
import pandas as pd

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config["SECRET_KEY"] = "super-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///crm.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = "uploads"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

ALLOWED_EXTENSIONS = {"csv", "xlsx"}

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def normalize_status(value):
    value = str(value).strip().lower()
    if value in {"prospect", "active", "inactive"}:
        return value
    return "prospect"


def clean_value(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("login"))
        if not current_user.is_admin:
            flash("Only admin can perform this action.")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


@app.route("/")
@login_required
def index():
    total_customers = Customer.query.count()
    total_leads = Lead.query.count()
    return render_template("index.html", total_customers=total_customers, total_leads=total_leads)


@app.route("/api/docs/")
def api_docs_redirect():
    return redirect("/api/docs")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("register"))

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("Username or email already exists.")
            return redirect(url_for("register"))

        role = "admin" if User.query.count() == 0 else "user"

        user = User(username=username, email=email, role=role)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        if role == "admin":
            flash("Registration successful. This account is the admin account.")
        else:
            flash("Registration successful.")

        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("index"))

        flash("Invalid username or password.")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/customers")
@login_required
def customers():
    customers = Customer.query.all()
    return render_template("customers.html", customers=customers)


@app.route("/customers/export/csv")
@login_required
def export_customers_csv():
    customers = Customer.query.all()

    data = []
    for c in customers:
        data.append({
            "name": c.name,
            "email": c.email,
            "company": c.company,
            "phone": c.phone,
            "status": c.status
        })

    df = pd.DataFrame(data)

    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="customers_export.csv"
    )


@app.route("/customers/export/xlsx")
@login_required
def export_customers_xlsx():
    customers = Customer.query.all()

    data = []
    for c in customers:
        data.append({
            "name": c.name,
            "email": c.email,
            "company": c.company,
            "phone": c.phone,
            "status": c.status
        })

    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Customers")
    output.seek(0)

    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="customers_export.xlsx"
    )


@app.route("/customers/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_customer():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        company = request.form.get("company", "").strip()
        phone = request.form.get("phone", "").strip()
        status = request.form.get("status", "prospect").strip()

        if not all([name, email, company, phone]):
            flash("All fields are required.")
            return redirect(url_for("add_customer"))

        customer = Customer(
            name=name,
            email=email,
            company=company,
            phone=phone,
            status=status
        )
        db.session.add(customer)
        db.session.commit()

        flash("Customer added successfully.")
        return redirect(url_for("customers"))

    return render_template("add_customer.html")


@app.route("/customers/import", methods=["GET", "POST"])
@login_required
@admin_required
def import_customers():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file selected.")
            return redirect(url_for("import_customers"))

        file = request.files["file"]

        if file.filename == "":
            flash("No file selected.")
            return redirect(url_for("import_customers"))

        if not allowed_file(file.filename):
            flash("Only .csv and .xlsx files are allowed.")
            return redirect(url_for("import_customers"))

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

        try:
            file.save(filepath)

            if filename.lower().endswith(".csv"):
                df = pd.read_csv(filepath)
            else:
                df = pd.read_excel(filepath, engine="openpyxl")

            df.columns = [str(col).strip().lower() for col in df.columns]

            required_columns = ["name", "email", "company", "phone", "status"]
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                flash("Missing required columns: " + ", ".join(missing_columns))
                return redirect(url_for("import_customers"))

            imported_count = 0
            skipped_count = 0

            for _, row in df.iterrows():
                name = clean_value(row.get("name"))
                email = clean_value(row.get("email"))
                company = clean_value(row.get("company"))
                phone = clean_value(row.get("phone"))
                status = normalize_status(row.get("status"))

                if not all([name, email, company, phone]):
                    skipped_count += 1
                    continue

                customer = Customer(
                    name=name,
                    email=email,
                    company=company,
                    phone=phone,
                    status=status
                )
                db.session.add(customer)
                imported_count += 1

            db.session.commit()
            flash(f"Import completed. Added: {imported_count}, skipped: {skipped_count}.")
            return redirect(url_for("customers"))

        except Exception as e:
            flash(f"Import failed: {str(e)}")
            return redirect(url_for("import_customers"))

        finally:
            if os.path.exists(filepath):
                os.remove(filepath)

    return render_template("import_customers.html")


@app.route("/customers/<int:customer_id>")
@login_required
def customer_detail(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        flash("Customer not found.")
        return redirect(url_for("customers"))
    return render_template("customer_detail.html", customer=customer)


@app.route("/customers/<int:customer_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        flash("Customer not found.")
        return redirect(url_for("customers"))

    if request.method == "POST":
        customer.name = request.form.get("name", "").strip()
        customer.email = request.form.get("email", "").strip()
        customer.company = request.form.get("company", "").strip()
        customer.phone = request.form.get("phone", "").strip()
        customer.status = request.form.get("status", "prospect").strip()

        db.session.commit()
        flash("Customer updated successfully.")
        return redirect(url_for("customer_detail", customer_id=customer.id))

    return render_template("edit_customer.html", customer=customer)


@app.route("/customers/<int:customer_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if customer:
        db.session.delete(customer)
        db.session.commit()
        flash("Customer deleted successfully.")
    return redirect(url_for("customers"))


@app.route("/leads")
@login_required
def leads():
    leads = Lead.query.all()
    return render_template("leads.html", leads=leads)


@app.route("/leads/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_lead():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        company = request.form.get("company", "").strip()
        value = request.form.get("value", "").strip()
        source = request.form.get("source", "").strip()

        if not all([name, email, company, value, source]):
            flash("All fields are required.")
            return redirect(url_for("add_lead"))

        try:
            value = float(value)
        except ValueError:
            flash("Value must be a number.")
            return redirect(url_for("add_lead"))

        lead = Lead(
            name=name,
            email=email,
            company=company,
            value=value,
            source=source
        )
        db.session.add(lead)
        db.session.commit()

        flash("Lead added successfully.")
        return redirect(url_for("leads"))

    return render_template("add_lead.html")


@app.route("/leads/<int:lead_id>")
@login_required
def lead_detail(lead_id):
    lead = Lead.query.get(lead_id)
    if not lead:
        flash("Lead not found.")
        return redirect(url_for("leads"))
    return render_template("lead_detail.html", lead=lead)


@app.route("/leads/<int:lead_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_lead(lead_id):
    lead = Lead.query.get(lead_id)
    if not lead:
        flash("Lead not found.")
        return redirect(url_for("leads"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        company = request.form.get("company", "").strip()
        value = request.form.get("value", "").strip()
        source = request.form.get("source", "").strip()

        if not all([name, email, company, value, source]):
            flash("All fields are required.")
            return redirect(url_for("edit_lead", lead_id=lead.id))

        try:
            value = float(value)
        except ValueError:
            flash("Value must be a number.")
            return redirect(url_for("edit_lead", lead_id=lead.id))

        lead.name = name
        lead.email = email
        lead.company = company
        lead.value = value
        lead.source = source

        db.session.commit()
        flash("Lead updated successfully.")
        return redirect(url_for("lead_detail", lead_id=lead.id))

    return render_template("edit_lead.html", lead=lead)


@app.route("/leads/<int:lead_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_lead(lead_id):
    lead = Lead.query.get(lead_id)
    if lead:
        db.session.delete(lead)
        db.session.commit()
        flash("Lead deleted successfully.")
    return redirect(url_for("leads"))


api_bp = Blueprint("api", __name__, url_prefix="/api")

api = Api(
    api_bp,
    version="1.0",
    title="CRM REST API",
    description="Simple Flask CRM API",
    doc="/docs"
)

customer_input = api.model("CustomerInput", {
    "name": fields.String(required=True),
    "email": fields.String(required=True),
    "company": fields.String(required=True),
    "phone": fields.String(required=True),
    "status": fields.String(required=True)
})

customer_output = api.model("CustomerOutput", {
    "id": fields.Integer,
    "name": fields.String,
    "email": fields.String,
    "company": fields.String,
    "phone": fields.String,
    "status": fields.String
})

lead_input = api.model("LeadInput", {
    "name": fields.String(required=True),
    "email": fields.String(required=True),
    "company": fields.String(required=True),
    "value": fields.Float(required=True),
    "source": fields.String(required=True)
})

lead_output = api.model("LeadOutput", {
    "id": fields.Integer,
    "name": fields.String,
    "email": fields.String,
    "company": fields.String,
    "value": fields.Float,
    "source": fields.String
})


@api.route("/customers")
class CustomerListApi(Resource):
    @api.marshal_list_with(customer_output)
    def get(self):
        return Customer.query.all()

    @api.expect(customer_input, validate=True)
    @api.marshal_with(customer_output, code=201)
    def post(self):
        if not current_user.is_authenticated or not current_user.is_admin:
            api.abort(403, "Only admin can add customers")

        data = api.payload

        customer = Customer(
            name=data["name"],
            email=data["email"],
            company=data["company"],
            phone=data["phone"],
            status=data["status"]
        )
        db.session.add(customer)
        db.session.commit()
        return customer, 201


@api.route("/customers/<int:customer_id>")
class CustomerApi(Resource):
    @api.marshal_with(customer_output)
    def get(self, customer_id):
        customer = Customer.query.get(customer_id)
        if not customer:
            api.abort(404, "Customer not found")
        return customer

    @api.expect(customer_input, validate=True)
    @api.marshal_with(customer_output)
    def put(self, customer_id):
        if not current_user.is_authenticated or not current_user.is_admin:
            api.abort(403, "Only admin can edit customers")

        customer = Customer.query.get(customer_id)
        if not customer:
            api.abort(404, "Customer not found")

        data = api.payload
        customer.name = data["name"]
        customer.email = data["email"]
        customer.company = data["company"]
        customer.phone = data["phone"]
        customer.status = data["status"]

        db.session.commit()
        return customer

    def delete(self, customer_id):
        if not current_user.is_authenticated or not current_user.is_admin:
            api.abort(403, "Only admin can delete customers")

        customer = Customer.query.get(customer_id)
        if not customer:
            api.abort(404, "Customer not found")

        db.session.delete(customer)
        db.session.commit()
        return {"message": "Customer deleted"}, 200


@api.route("/leads")
class LeadListApi(Resource):
    @api.marshal_list_with(lead_output)
    def get(self):
        return Lead.query.all()

    @api.expect(lead_input, validate=True)
    @api.marshal_with(lead_output, code=201)
    def post(self):
        if not current_user.is_authenticated or not current_user.is_admin:
            api.abort(403, "Only admin can add leads")

        data = api.payload

        lead = Lead(
            name=data["name"],
            email=data["email"],
            company=data["company"],
            value=data["value"],
            source=data["source"]
        )
        db.session.add(lead)
        db.session.commit()
        return lead, 201


@api.route("/leads/<int:lead_id>")
class LeadApi(Resource):
    @api.marshal_with(lead_output)
    def get(self, lead_id):
        lead = Lead.query.get(lead_id)
        if not lead:
            api.abort(404, "Lead not found")
        return lead

    @api.expect(lead_input, validate=True)
    @api.marshal_with(lead_output)
    def put(self, lead_id):
        if not current_user.is_authenticated or not current_user.is_admin:
            api.abort(403, "Only admin can edit leads")

        lead = Lead.query.get(lead_id)
        if not lead:
            api.abort(404, "Lead not found")

        data = api.payload
        lead.name = data["name"]
        lead.email = data["email"]
        lead.company = data["company"]
        lead.value = data["value"]
        lead.source = data["source"]

        db.session.commit()
        return lead

    def delete(self, lead_id):
        if not current_user.is_authenticated or not current_user.is_admin:
            api.abort(403, "Only admin can delete leads")

        lead = Lead.query.get(lead_id)
        if not lead:
            api.abort(404, "Lead not found")

        db.session.delete(lead)
        db.session.commit()
        return {"message": "Lead deleted"}, 200


app.register_blueprint(api_bp)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)