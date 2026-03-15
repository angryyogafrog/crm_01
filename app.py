from functools import wraps
from io import BytesIO
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, abort, jsonify, make_response, send_file
)
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_swagger_ui import get_swaggerui_blueprint
import pandas as pd
from models import db, Customer, Lead, User

app = Flask(__name__)
app.config["SECRET_KEY"] = "super_secret_key_change_this"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///crm.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message = "Please log in first."
login_manager.init_app(app)

SWAGGER_URL = "/api/docs"
API_URL = "/openapi.json"

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "CRM REST API"}
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return login_manager.unauthorized()

        if not current_user.is_admin():
            abort(403)

        return f(*args, **kwargs)
    return decorated_function


def customer_dataframe():
    customers = Customer.query.order_by(Customer.id.desc()).all()
    data = [customer.to_dict() for customer in customers]
    return pd.DataFrame(data)


def lead_dataframe():
    leads = Lead.query.order_by(Lead.id.desc()).all()
    data = [lead.to_dict() for lead in leads]
    return pd.DataFrame(data)


def csv_download_response(df, filename):
    csv_data = df.to_csv(index=False)
    response = make_response(csv_data)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    return response


def excel_download_response(df, filename):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Data")
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def read_uploaded_table(uploaded_file):
    filename = uploaded_file.filename.lower()

    if filename.endswith(".csv"):
        return pd.read_csv(uploaded_file), "csv"

    if filename.endswith(".xlsx"):
        return pd.read_excel(uploaded_file), "xlsx"

    return None, None


def normalize_value(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def import_customers_from_dataframe(df):
    required_columns = {"name", "email"}
    available_columns = {col.strip().lower() for col in df.columns}

    if not required_columns.issubset(available_columns):
        missing = sorted(required_columns - available_columns)
        return {
            "success": False,
            "message": f"Missing required columns: {', '.join(missing)}"
        }

    df.columns = [col.strip().lower() for col in df.columns]

    imported_count = 0
    skipped_count = 0
    errors = []

    for index, row in df.iterrows():
        name = normalize_value(row.get("name"))
        email = normalize_value(row.get("email"))
        company = normalize_value(row.get("company"))
        phone = normalize_value(row.get("phone"))
        status = normalize_value(row.get("status")) or "prospect"

        if not name or not email:
            skipped_count += 1
            errors.append(f"Row {index + 2}: name and email are required")
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

    return {
        "success": True,
        "entity": "customers",
        "imported_count": imported_count,
        "skipped_count": skipped_count,
        "total_rows": len(df),
        "errors": errors
    }


def import_leads_from_dataframe(df):
    required_columns = {"name", "email"}
    available_columns = {col.strip().lower() for col in df.columns}

    if not required_columns.issubset(available_columns):
        missing = sorted(required_columns - available_columns)
        return {
            "success": False,
            "message": f"Missing required columns: {', '.join(missing)}"
        }

    df.columns = [col.strip().lower() for col in df.columns]

    imported_count = 0
    skipped_count = 0
    errors = []

    for index, row in df.iterrows():
        name = normalize_value(row.get("name"))
        email = normalize_value(row.get("email"))
        company = normalize_value(row.get("company"))
        phone = normalize_value(row.get("phone"))
        source = normalize_value(row.get("source"))

        if not name or not email:
            skipped_count += 1
            errors.append(f"Row {index + 2}: name and email are required")
            continue

        lead = Lead(
            name=name,
            email=email,
            company=company,
            phone=phone,
            source=source
        )
        db.session.add(lead)
        imported_count += 1

    db.session.commit()

    return {
        "success": True,
        "entity": "leads",
        "imported_count": imported_count,
        "skipped_count": skipped_count,
        "total_rows": len(df),
        "errors": errors
    }


@app.route("/openapi.json", methods=["GET"])
def openapi_spec():
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "CRM REST API",
            "version": "1.0.0",
            "description": "API for managing customers and leads in the CRM system."
        },
        "servers": [{"url": "http://127.0.0.1:5000"}],
        "components": {
            "schemas": {
                "Customer": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "example": 1},
                        "name": {"type": "string", "example": "Anna Nowak"},
                        "email": {"type": "string", "example": "anna@test.com"},
                        "company": {"type": "string", "example": "Test Company"},
                        "phone": {"type": "string", "example": "123456789"},
                        "status": {"type": "string", "example": "prospect"}
                    }
                },
                "CustomerInput": {
                    "type": "object",
                    "required": ["name", "email"],
                    "properties": {
                        "name": {"type": "string", "example": "Anna Nowak"},
                        "email": {"type": "string", "example": "anna@test.com"},
                        "company": {"type": "string", "example": "Test Company"},
                        "phone": {"type": "string", "example": "123456789"},
                        "status": {"type": "string", "example": "prospect"}
                    }
                },
                "Lead": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "example": 1},
                        "name": {"type": "string", "example": "Max Mustermann"},
                        "email": {"type": "string", "example": "max@test.com"},
                        "company": {"type": "string", "example": "Demo GmbH"},
                        "phone": {"type": "string", "example": "987654321"},
                        "source": {"type": "string", "example": "Website"}
                    }
                },
                "LeadInput": {
                    "type": "object",
                    "required": ["name", "email"],
                    "properties": {
                        "name": {"type": "string", "example": "Max Mustermann"},
                        "email": {"type": "string", "example": "max@test.com"},
                        "company": {"type": "string", "example": "Demo GmbH"},
                        "phone": {"type": "string", "example": "987654321"},
                        "source": {"type": "string", "example": "Website"}
                    }
                },
                "Health": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string", "example": "ok"}
                    }
                },
                "Message": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "example": "Deleted successfully"}
                    }
                },
                "Error": {
                    "type": "object",
                    "properties": {
                        "error": {"type": "string", "example": "Customer not found"}
                    }
                }
            }
        },
        "paths": {
            "/api/health": {
                "get": {
                    "summary": "Health check",
                    "responses": {
                        "200": {
                            "description": "API is running",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Health"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/customers": {
                "get": {
                    "summary": "Get all customers",
                    "responses": {
                        "200": {
                            "description": "List of customers",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Customer"}
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "summary": "Create customer",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CustomerInput"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Customer created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Customer"}
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid input",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/customers/{customer_id}": {
                "get": {
                    "summary": "Get customer by ID",
                    "parameters": [
                        {
                            "name": "customer_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Customer found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Customer"}
                                }
                            }
                        },
                        "404": {
                            "description": "Customer not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                },
                "put": {
                    "summary": "Update customer",
                    "parameters": [
                        {
                            "name": "customer_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/CustomerInput"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Customer updated",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Customer"}
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid input",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        },
                        "404": {
                            "description": "Customer not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                },
                "delete": {
                    "summary": "Delete customer",
                    "parameters": [
                        {
                            "name": "customer_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Customer deleted",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Message"}
                                }
                            }
                        },
                        "404": {
                            "description": "Customer not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/leads": {
                "get": {
                    "summary": "Get all leads",
                    "responses": {
                        "200": {
                            "description": "List of leads",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"$ref": "#/components/schemas/Lead"}
                                    }
                                }
                            }
                        }
                    }
                },
                "post": {
                    "summary": "Create lead",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/LeadInput"}
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Lead created",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Lead"}
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid input",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            },
            "/api/leads/{lead_id}": {
                "get": {
                    "summary": "Get lead by ID",
                    "parameters": [
                        {
                            "name": "lead_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Lead found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Lead"}
                                }
                            }
                        },
                        "404": {
                            "description": "Lead not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                },
                "put": {
                    "summary": "Update lead",
                    "parameters": [
                        {
                            "name": "lead_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/LeadInput"}
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Lead updated",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Lead"}
                                }
                            }
                        },
                        "400": {
                            "description": "Invalid input",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        },
                        "404": {
                            "description": "Lead not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                },
                "delete": {
                    "summary": "Delete lead",
                    "parameters": [
                        {
                            "name": "lead_id",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"}
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Lead deleted",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Message"}
                                }
                            }
                        },
                        "404": {
                            "description": "Lead not found",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Error"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    return jsonify(spec)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if not username or not password or not confirm_password:
            flash("All fields are required.", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("register"))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.", "error")
            return redirect(url_for("register"))

        user_count = User.query.count()
        role = "admin" if user_count == 0 else "user"

        user = User(username=username, role=role)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Registration successful. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("customers"))

        flash("Invalid username or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.", "success")
    return redirect(url_for("index"))


@app.route("/customers")
@login_required
def customers():
    all_customers = Customer.query.order_by(Customer.id.desc()).all()
    return render_template("customers.html", customers=all_customers)


@app.route("/customers/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_customer():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        company = request.form["company"].strip()
        phone = request.form["phone"].strip()
        status = request.form["status"].strip()

        if not name or not email:
            flash("Name and email are required.", "error")
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

        flash("Customer added successfully.", "success")
        return redirect(url_for("customers"))

    return render_template("add_customer.html")


@app.route("/customers/<int:customer_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)

    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        company = request.form["company"].strip()
        phone = request.form["phone"].strip()
        status = request.form["status"].strip()

        if not name or not email:
            flash("Name and email are required.", "error")
            return redirect(url_for("edit_customer", customer_id=customer_id))

        customer.name = name
        customer.email = email
        customer.company = company
        customer.phone = phone
        customer.status = status

        db.session.commit()

        flash("Customer updated successfully.", "success")
        return redirect(url_for("customers"))

    return render_template("edit_customer.html", customer=customer)


@app.route("/customers/<int:customer_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)

    db.session.delete(customer)
    db.session.commit()

    flash("Customer deleted successfully.", "success")
    return redirect(url_for("customers"))


@app.route("/customers/export/csv")
@login_required
def export_customers_csv():
    df = customer_dataframe()
    return csv_download_response(df, "customers_export.csv")


@app.route("/customers/export/excel")
@login_required
def export_customers_excel():
    df = customer_dataframe()
    return excel_download_response(df, "customers_export.xlsx")


@app.route("/leads")
@login_required
def leads():
    all_leads = Lead.query.order_by(Lead.id.desc()).all()
    return render_template("leads.html", leads=all_leads)


@app.route("/leads/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_lead():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        company = request.form["company"].strip()
        phone = request.form["phone"].strip()
        source = request.form["source"].strip()

        if not name or not email:
            flash("Name and email are required.", "error")
            return redirect(url_for("add_lead"))

        lead = Lead(
            name=name,
            email=email,
            company=company,
            phone=phone,
            source=source
        )

        db.session.add(lead)
        db.session.commit()

        flash("Lead added successfully.", "success")
        return redirect(url_for("leads"))

    return render_template("add_lead.html")


@app.route("/leads/<int:lead_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_lead(lead_id):
    lead = Lead.query.get_or_404(lead_id)

    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        company = request.form["company"].strip()
        phone = request.form["phone"].strip()
        source = request.form["source"].strip()

        if not name or not email:
            flash("Name and email are required.", "error")
            return redirect(url_for("edit_lead", lead_id=lead_id))

        lead.name = name
        lead.email = email
        lead.company = company
        lead.phone = phone
        lead.source = source

        db.session.commit()

        flash("Lead updated successfully.", "success")
        return redirect(url_for("leads"))

    return render_template("edit_lead.html", lead=lead)


@app.route("/leads/<int:lead_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_lead(lead_id):
    lead = Lead.query.get_or_404(lead_id)

    db.session.delete(lead)
    db.session.commit()

    flash("Lead deleted successfully.", "success")
    return redirect(url_for("leads"))


@app.route("/leads/export/csv")
@login_required
def export_leads_csv():
    df = lead_dataframe()
    return csv_download_response(df, "leads_export.csv")


@app.route("/leads/export/excel")
@login_required
def export_leads_excel():
    df = lead_dataframe()
    return excel_download_response(df, "leads_export.xlsx")


@app.route("/import", methods=["GET", "POST"])
@login_required
@admin_required
def import_data():
    if request.method == "POST":
        entity = request.form.get("entity", "").strip()
        uploaded_file = request.files.get("file")

        if entity not in ["customers", "leads"]:
            flash("Please choose a valid import type.", "error")
            return redirect(url_for("import_data"))

        if not uploaded_file or uploaded_file.filename == "":
            flash("Please select a file.", "error")
            return redirect(url_for("import_data"))

        df, file_type = read_uploaded_table(uploaded_file)

        if df is None:
            flash("Only CSV and XLSX files are supported.", "error")
            return redirect(url_for("import_data"))

        if entity == "customers":
            report = import_customers_from_dataframe(df)
        else:
            report = import_leads_from_dataframe(df)

        if not report["success"]:
            flash(report["message"], "error")
            return redirect(url_for("import_data"))

        report["file_type"] = file_type
        report["filename"] = uploaded_file.filename

        return render_template("import_report.html", report=report)

    return render_template("import_data.html")


@app.route("/api/health", methods=["GET"])
def api_health():
    return jsonify({"status": "ok"}), 200


@app.route("/api/customers", methods=["GET"])
def api_get_customers():
    customers = Customer.query.order_by(Customer.id.desc()).all()
    return jsonify([customer.to_dict() for customer in customers]), 200


@app.route("/api/customers/<int:customer_id>", methods=["GET"])
def api_get_customer(customer_id):
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify(customer.to_dict()), 200


@app.route("/api/customers", methods=["POST"])
def api_create_customer():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    company = data.get("company", "").strip()
    phone = data.get("phone", "").strip()
    status = data.get("status", "prospect").strip()

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    customer = Customer(
        name=name,
        email=email,
        company=company,
        phone=phone,
        status=status
    )

    db.session.add(customer)
    db.session.commit()

    return jsonify(customer.to_dict()), 201


@app.route("/api/customers/<int:customer_id>", methods=["PUT"])
def api_update_customer(customer_id):
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    name = data.get("name", customer.name).strip()
    email = data.get("email", customer.email).strip()
    company = data.get("company", customer.company or "").strip()
    phone = data.get("phone", customer.phone or "").strip()
    status = data.get("status", customer.status).strip()

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    customer.name = name
    customer.email = email
    customer.company = company
    customer.phone = phone
    customer.status = status

    db.session.commit()

    return jsonify(customer.to_dict()), 200


@app.route("/api/customers/<int:customer_id>", methods=["DELETE"])
def api_delete_customer(customer_id):
    customer = Customer.query.get(customer_id)

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    db.session.delete(customer)
    db.session.commit()

    return jsonify({"message": "Customer deleted successfully"}), 200


@app.route("/api/leads", methods=["GET"])
def api_get_leads():
    leads = Lead.query.order_by(Lead.id.desc()).all()
    return jsonify([lead.to_dict() for lead in leads]), 200


@app.route("/api/leads/<int:lead_id>", methods=["GET"])
def api_get_lead(lead_id):
    lead = Lead.query.get(lead_id)

    if not lead:
        return jsonify({"error": "Lead not found"}), 404

    return jsonify(lead.to_dict()), 200


@app.route("/api/leads", methods=["POST"])
def api_create_lead():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    company = data.get("company", "").strip()
    phone = data.get("phone", "").strip()
    source = data.get("source", "").strip()

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    lead = Lead(
        name=name,
        email=email,
        company=company,
        phone=phone,
        source=source
    )

    db.session.add(lead)
    db.session.commit()

    return jsonify(lead.to_dict()), 201


@app.route("/api/leads/<int:lead_id>", methods=["PUT"])
def api_update_lead(lead_id):
    lead = Lead.query.get(lead_id)

    if not lead:
        return jsonify({"error": "Lead not found"}), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    name = data.get("name", lead.name).strip()
    email = data.get("email", lead.email).strip()
    company = data.get("company", lead.company or "").strip()
    phone = data.get("phone", lead.phone or "").strip()
    source = data.get("source", lead.source or "").strip()

    if not name or not email:
        return jsonify({"error": "Name and email are required"}), 400

    lead.name = name
    lead.email = email
    lead.company = company
    lead.phone = phone
    lead.source = source

    db.session.commit()

    return jsonify(lead.to_dict()), 200


@app.route("/api/leads/<int:lead_id>", methods=["DELETE"])
def api_delete_lead(lead_id):
    lead = Lead.query.get(lead_id)

    if not lead:
        return jsonify({"error": "Lead not found"}), 404

    db.session.delete(lead)
    db.session.commit()

    return jsonify({"message": "Lead deleted successfully"}), 200


@app.errorhandler(403)
def forbidden(error):
    return render_template("500.html"), 403


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="127.0.0.1", port=5000)