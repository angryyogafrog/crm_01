# Comprehensive Flask Framework Guide: Building a Customer Relationship Management (CRM) System

## Table of Contents
1. [Introduction to Flask](#introduction-to-flask)
2. [Understanding the MVC Pattern](#understanding-the-mvc-pattern)
3. [Project Structure](#project-structure)
4. [Complete CRM Example](#complete-crm-example)
5. [How to Run](#how-to-run)
6. [Key Concepts](#key-concepts)
7. [Best Practices](#best-practices)

---

## Introduction to Flask

Flask is a **lightweight Python web framework** that makes it easy to build web applications. Unlike heavier frameworks like Django, Flask gives you the flexibility to structure your project as you like while providing essential tools for:

- **Routing** - mapping URLs to Python functions
- **Templating** - generating dynamic HTML pages
- **Form handling** - collecting and processing user input
- **Static files** - serving CSS, JavaScript, and images

### Why Flask?

- **Minimal and flexible** - start small, scale as needed
- **Excellent documentation** - easy to learn and troubleshoot
- **Extensible** - add libraries as your needs grow
- **Perfect for learning** - understand web fundamentals clearly
- **Production-ready** - used by real companies worldwide

---

## Understanding the MVC Pattern

The **Model-View-Controller (MVC)** pattern is a design approach that separates your application into three interconnected components:

### 1. **Model** (Data & Business Logic)

- Represents your data structure
- Contains business logic and data validation
- In Flask: Python classes that define your entities
- Example: `Customer`, `Contact`, `Lead`, `Pipeline`

**Key responsibilities:**
- Define data attributes
- Implement CRUD operations (Create, Read, Update, Delete)
- Validate data integrity
- Provide methods for data access

### 2. **View** (Presentation Layer)

- Displays data to the user
- Handles the visual layout and design
- In Flask: HTML templates in the `templates/` folder using Jinja2 syntax

**Key responsibilities:**
- Structure HTML markup
- Display model data dynamically
- Collect user input through forms
- Provide visual feedback

### 3. **Controller** (Request Handler)

- Receives user input/requests
- Processes requests using models
- Selects appropriate views to display
- In Flask: Functions decorated with `@app.route()` that handle HTTP requests

**Key responsibilities:**
- Handle HTTP requests
- Call model methods to fetch/modify data
- Prepare data for templates
- Return appropriate responses

### Why MVC?

| Benefit | Explanation |
|---------|-------------|
| **Separation of Concerns** | Each component has a specific responsibility |
| **Maintainability** | Easier to update one part without affecting others |
| **Reusability** | Models can be used across different views |
| **Testability** | Components can be tested independently |
| **Scalability** | Easy to add new features |

### MVC Flow Diagram

```
User Request
    ↓
Controller (Route Handler)
    ↓
Model (Business Logic & Data)
    ↓
View (Template Rendering)
    ↓
HTML Response to User
```

---

## Project Structure

Here's the recommended folder structure for a Flask CRM application:

```
crm_system/
├── app.py              # Main Flask application (Controller)
├── models.py           # Data models (Model)
├── static/
│   ├── css/
│   │   └── style.css   # Styling
│   └── js/
│       └── script.js   # Optional JavaScript
└── templates/
    ├── base.html       # Base template (extends, blocks)
    ├── index.html      # Home page
    ├── customers.html  # Customer list
    ├── add_customer.html # Add customer form
    ├── edit_customer.html # Edit customer form
    ├── leads.html      # Sales leads list
    ├── contacts.html   # Contact list
    └── 404.html        # Error page
```

### Folder Purposes

- **app.py** - Contains all route handlers (controllers) and Flask initialization
- **models.py** - Contains data classes (Customer, Lead, Contact, etc.)
- **static/** - Public files (CSS, JavaScript, images) served directly
- **templates/** - HTML templates using Jinja2 syntax

---

## Complete CRM Example

### 1. Model Layer (`models.py`)

```python
# models.py
"""
Customer Relationship Management (CRM) Models
Handles data structures and business logic
"""

class Customer:
    """Customer model representing customer data"""
    
    # Class variables for in-memory storage
    customers = []
    next_id = 1
    
    def __init__(self, name, email, company, phone, status="prospect"):
        """Initialize a new customer"""
        self.id = Customer.next_id
        Customer.next_id += 1
        self.name = name
        self.email = email
        self.company = company
        self.phone = phone
        self.status = status  # prospect, active, inactive
    
    def to_dict(self):
        """Convert customer to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'company': self.company,
            'phone': self.phone,
            'status': self.status
        }
    
    @classmethod
    def add_customer(cls, name, email, company, phone, status="prospect"):
        """Add a new customer"""
        customer = cls(name, email, company, phone, status)
        cls.customers.append(customer)
        return customer
    
    @classmethod
    def get_all_customers(cls):
        """Get all customers"""
        return cls.customers
    
    @classmethod
    def get_customer_by_id(cls, customer_id):
        """Find customer by ID"""
        for customer in cls.customers:
            if customer.id == customer_id:
                return customer
        return None
    
    @classmethod
    def update_customer(cls, customer_id, name, email, company, phone, status):
        """Update existing customer"""
        customer = cls.get_customer_by_id(customer_id)
        if customer:
            customer.name = name
            customer.email = email
            customer.company = company
            customer.phone = phone
            customer.status = status
            return True
        return False
    
    @classmethod
    def delete_customer(cls, customer_id):
        """Delete customer by ID"""
        customer = cls.get_customer_by_id(customer_id)
        if customer:
            cls.customers.remove(customer)
            return True
        return False
    
    def __repr__(self):
        return f"<Customer {self.id}: {self.name} ({self.company})>"


class Lead:
    """Sales lead model"""
    
    leads = []
    next_id = 1
    
    def __init__(self, name, email, company, value, source):
        """Initialize a new lead"""
        self.id = Lead.next_id
        Lead.next_id += 1
        self.name = name
        self.email = email
        self.company = company
        self.value = value  # Estimated deal value
        self.source = source  # Website, Email, Referral, etc.
        self.status = "new"  # new, contacted, qualified, lost
    
    @classmethod
    def add_lead(cls, name, email, company, value, source):
        """Add a new lead"""
        lead = cls(name, email, company, value, source)
        cls.leads.append(lead)
        return lead
    
    @classmethod
    def get_all_leads(cls):
        """Get all leads"""
        return cls.leads
    
    @classmethod
    def get_lead_by_id(cls, lead_id):
        """Find lead by ID"""
        for lead in cls.leads:
            if lead.id == lead_id:
                return lead
        return None
    
    @classmethod
    def delete_lead(cls, lead_id):
        """Delete lead by ID"""
        lead = cls.get_lead_by_id(lead_id)
        if lead:
            cls.leads.remove(lead)
            return True
        return False
    
    def __repr__(self):
        return f"<Lead {self.id}: {self.name} (${self.value})>"


class Contact:
    """Contact model for customer communication tracking"""
    
    contacts = []
    next_id = 1
    
    def __init__(self, customer_id, contact_type, notes):
        """Initialize a new contact record"""
        self.id = Contact.next_id
        Contact.next_id += 1
        self.customer_id = customer_id
        self.contact_type = contact_type  # phone, email, meeting, etc.
        self.notes = notes
        self.date = __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')
    
    @classmethod
    def add_contact(cls, customer_id, contact_type, notes):
        """Add a new contact record"""
        contact = cls(customer_id, contact_type, notes)
        cls.contacts.append(contact)
        return contact
    
    @classmethod
    def get_contacts_by_customer(cls, customer_id):
        """Get all contacts for a specific customer"""
        return [c for c in cls.contacts if c.customer_id == customer_id]
    
    def __repr__(self):
        return f"<Contact {self.id}: {self.contact_type} on {self.date}>"
```

### 2. Controller Layer (`app.py`)

```python
# app.py
"""
Flask CRM Application
Main application file with routes (controllers)
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from models import Customer, Lead, Contact

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production!

# Initialize with sample data
def init_sample_data():
    """Add sample data for testing"""
    Customer.add_customer("Anna Müller", "anna@example.com", "Tech Corp", "0650 123456", "active")
    Customer.add_customer("Max Schmidt", "max@example.com", "Design Studio", "0650 234567", "prospect")
    Customer.add_customer("Lisa Weber", "lisa@example.com", "Marketing Pro", "0650 345678", "inactive")
    
    Lead.add_lead("John Software", "john@startup.com", "StartupXYZ", 50000, "Website")
    Lead.add_lead("Sarah Digital", "sarah@agency.com", "Digital Agency", 75000, "Referral")
    
    Contact.add_contact(1, "email", "Initial inquiry about our services")
    Contact.add_contact(1, "phone", "Discussed project requirements")
    Contact.add_contact(2, "meeting", "Met for proposal presentation")

init_sample_data()


@app.route('/')
def index():
    """Home page with dashboard"""
    total_customers = len(Customer.get_all_customers())
    total_leads = len(Lead.get_all_leads())
    active_customers = len([c for c in Customer.get_all_customers() if c.status == "active"])
    
    stats = {
        'total_customers': total_customers,
        'total_leads': total_leads,
        'active_customers': active_customers
    }
    
    return render_template('index.html', stats=stats)


# =====================
# CUSTOMER ROUTES
# =====================

@app.route('/customers')
def customers():
    """Display all customers"""
    all_customers = Customer.get_all_customers()
    return render_template('customers.html', customers=all_customers)


@app.route('/customers/add', methods=['GET', 'POST'])
def add_customer():
    """Add a new customer"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        company = request.form.get('company')
        phone = request.form.get('phone')
        status = request.form.get('status', 'prospect')
        
        # Validation
        if not all([name, email, company, phone]):
            flash('All fields are required!', 'error')
            return redirect(url_for('add_customer'))
        
        # Create customer
        Customer.add_customer(name, email, company, phone, status)
        flash(f'Customer {name} added successfully!', 'success')
        return redirect(url_for('customers'))
    
    return render_template('add_customer.html')


@app.route('/customers/edit/<int:customer_id>', methods=['GET', 'POST'])
def edit_customer(customer_id):
    """Edit existing customer"""
    customer = Customer.get_customer_by_id(customer_id)
    
    if not customer:
        flash('Customer not found!', 'error')
        return redirect(url_for('customers'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        company = request.form.get('company')
        phone = request.form.get('phone')
        status = request.form.get('status')
        
        if Customer.update_customer(customer_id, name, email, company, phone, status):
            flash(f'Customer {name} updated successfully!', 'success')
        else:
            flash('Failed to update customer!', 'error')
        
        return redirect(url_for('customers'))
    
    return render_template('edit_customer.html', customer=customer)


@app.route('/customers/delete/<int:customer_id>')
def delete_customer(customer_id):
    """Delete a customer"""
    if Customer.delete_customer(customer_id):
        flash('Customer deleted successfully!', 'success')
    else:
        flash('Customer not found!', 'error')
    
    return redirect(url_for('customers'))


@app.route('/customers/<int:customer_id>')
def customer_detail(customer_id):
    """View customer details with contact history"""
    customer = Customer.get_customer_by_id(customer_id)
    
    if not customer:
        flash('Customer not found!', 'error')
        return redirect(url_for('customers'))
    
    contacts = Contact.get_contacts_by_customer(customer_id)
    return render_template('customer_detail.html', customer=customer, contacts=contacts)


# =====================
# LEAD ROUTES
# =====================

@app.route('/leads')
def leads():
    """Display all leads"""
    all_leads = Lead.get_all_leads()
    return render_template('leads.html', leads=all_leads)


@app.route('/leads/add', methods=['GET', 'POST'])
def add_lead():
    """Add a new lead"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        company = request.form.get('company')
        value = float(request.form.get('value', 0))
        source = request.form.get('source')
        
        if not all([name, email, company, source]):
            flash('All fields are required!', 'error')
            return redirect(url_for('add_lead'))
        
        Lead.add_lead(name, email, company, value, source)
        flash(f'Lead {name} added successfully!', 'success')
        return redirect(url_for('leads'))
    
    return render_template('add_lead.html')


@app.route('/leads/delete/<int:lead_id>')
def delete_lead(lead_id):
    """Delete a lead"""
    if Lead.delete_lead(lead_id):
        flash('Lead deleted successfully!', 'success')
    else:
        flash('Lead not found!', 'error')
    
    return redirect(url_for('leads'))


# =====================
# CONTACT ROUTES
# =====================

@app.route('/customers/<int:customer_id>/contact/add', methods=['POST'])
def add_contact(customer_id):
    """Add contact record for customer"""
    contact_type = request.form.get('contact_type')
    notes = request.form.get('notes')
    
    if customer_id and contact_type and notes:
        Contact.add_contact(customer_id, contact_type, notes)
        flash('Contact recorded successfully!', 'success')
    
    return redirect(url_for('customer_detail', customer_id=customer_id))


# =====================
# ERROR HANDLERS
# =====================

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 error page"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    """Custom 500 error page"""
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
```

### 3. Base Template (`templates/base.html`)

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}CRM System{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <!-- Navigation Bar -->
    <nav class="navbar">
        <div class="container">
            <div class="nav-brand">
                <h1>💼 CRM System</h1>
            </div>
            <ul class="nav-menu">
                <li><a href="{{ url_for('index') }}" class="nav-link">Dashboard</a></li>
                <li><a href="{{ url_for('customers') }}" class="nav-link">Customers</a></li>
                <li><a href="{{ url_for('leads') }}" class="nav-link">Leads</a></li>
                <li><a href="{{ url_for('add_customer') }}" class="nav-link btn-primary">+ Add Customer</a></li>
            </ul>
        </div>
    </nav>

    <!-- Flash Messages -->
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            <div class="container">
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">
                        {{ message }}
                        <button class="close-btn" onclick="this.parentElement.style.display='none'">&times;</button>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
    {% endwith %}

    <!-- Main Content -->
    <main class="container">
        {% block content %}{% endblock %}
    </main>

    <!-- Footer -->
    <footer class="footer">
        <div class="container">
            <p>&copy; 2025 Customer Relationship Management System | Built with Flask & Python</p>
        </div>
    </footer>

    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
```

### 4. Home Page Template (`templates/index.html`)

```html
{% extends 'base.html' %}

{% block title %}Dashboard - CRM System{% endblock %}

{% block content %}
<div class="hero">
    <h1>Welcome to Your CRM Dashboard</h1>
    <p class="lead">Manage customers, track leads, and grow your business</p>
    <div class="hero-buttons">
        <a href="{{ url_for('customers') }}" class="btn btn-primary">View All Customers</a>
        <a href="{{ url_for('add_customer') }}" class="btn btn-secondary">Add New Customer</a>
    </div>
</div>

<section class="dashboard-stats">
    <h2>Overview</h2>
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-number">{{ stats.total_customers }}</div>
            <div class="stat-label">Total Customers</div>
            <div class="stat-description">All registered customers</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ stats.active_customers }}</div>
            <div class="stat-label">Active Customers</div>
            <div class="stat-description">Currently active accounts</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ stats.total_leads }}</div>
            <div class="stat-label">Open Leads</div>
            <div class="stat-description">Sales opportunities</div>
        </div>
    </div>
</section>

<section class="features">
    <h2>Key Features</h2>
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">👥</div>
            <h3>Customer Management</h3>
            <p>Organize and track all your customer information in one place</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <h3>Lead Tracking</h3>
            <p>Monitor potential sales opportunities and conversion rates</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📞</div>
            <h3>Contact History</h3>
            <p>Keep detailed records of all customer interactions</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Analytics</h3>
            <p>View insights and metrics to improve your sales strategy</p>
        </div>
    </div>
</section>
{% endblock %}
```

### 5. Customers List Template (`templates/customers.html`)

```html
{% extends 'base.html' %}

{% block title %}Customers - CRM System{% endblock %}

{% block content %}
<div class="page-header">
    <h1>All Customers</h1>
    <a href="{{ url_for('add_customer') }}" class="btn btn-primary">+ Add New Customer</a>
</div>

{% if customers %}
<div class="table-container">
    <table class="table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Company</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for customer in customers %}
            <tr>
                <td>{{ customer.id }}</td>
                <td><strong>{{ customer.name }}</strong></td>
                <td>{{ customer.company }}</td>
                <td>{{ customer.email }}</td>
                <td>{{ customer.phone }}</td>
                <td>
                    <span class="badge {% if customer.status == 'active' %}badge-success{% elif customer.status == 'prospect' %}badge-warning{% else %}badge-error{% endif %}">
                        {{ customer.status }}
                    </span>
                </td>
                <td class="actions">
                    <a href="{{ url_for('customer_detail', customer_id=customer.id) }}" class="btn btn-sm btn-secondary">View</a>
                    <a href="{{ url_for('edit_customer', customer_id=customer.id) }}" class="btn btn-sm btn-secondary">Edit</a>
                    <a href="{{ url_for('delete_customer', customer_id=customer.id) }}" class="btn btn-sm btn-danger" onclick="return confirm('Delete this customer?')">Delete</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% else %}
<div class="empty-state">
    <p>No customers found. <a href="{{ url_for('add_customer') }}">Add your first customer</a></p>
</div>
{% endif %}
{% endblock %}
```

### 6. Add Customer Form (`templates/add_customer.html`)

```html
{% extends 'base.html' %}

{% block title %}Add Customer - CRM System{% endblock %}

{% block content %}
<div class="page-header">
    <h1>Add New Customer</h1>
</div>

<div class="form-container">
    <form method="POST" action="{{ url_for('add_customer') }}" class="form">
        <div class="form-group">
            <label for="name">Full Name *</label>
            <input type="text" id="name" name="name" class="form-control" required placeholder="Enter customer name">
        </div>

        <div class="form-group">
            <label for="email">Email Address *</label>
            <input type="email" id="email" name="email" class="form-control" required placeholder="customer@example.com">
        </div>

        <div class="form-group">
            <label for="company">Company Name *</label>
            <input type="text" id="company" name="company" class="form-control" required placeholder="Company name">
        </div>

        <div class="form-group">
            <label for="phone">Phone Number *</label>
            <input type="tel" id="phone" name="phone" class="form-control" required placeholder="+43 650 123456">
        </div>

        <div class="form-group">
            <label for="status">Customer Status *</label>
            <select id="status" name="status" class="form-control" required>
                <option value="prospect">Prospect</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
            </select>
        </div>

        <div class="form-actions">
            <button type="submit" class="btn btn-primary">Add Customer</button>
            <a href="{{ url_for('customers') }}" class="btn btn-secondary">Cancel</a>
        </div>
    </form>
</div>
{% endblock %}
```

### 7. Edit Customer Form (`templates/edit_customer.html`)

```html
{% extends 'base.html' %}

{% block title %}Edit Customer - CRM System{% endblock %}

{% block content %}
<div class="page-header">
    <h1>Edit Customer</h1>
</div>

<div class="form-container">
    <form method="POST" action="{{ url_for('edit_customer', customer_id=customer.id) }}" class="form">
        <div class="form-group">
            <label for="name">Full Name *</label>
            <input type="text" id="name" name="name" class="form-control" required value="{{ customer.name }}">
        </div>

        <div class="form-group">
            <label for="email">Email Address *</label>
            <input type="email" id="email" name="email" class="form-control" required value="{{ customer.email }}">
        </div>

        <div class="form-group">
            <label for="company">Company Name *</label>
            <input type="text" id="company" name="company" class="form-control" required value="{{ customer.company }}">
        </div>

        <div class="form-group">
            <label for="phone">Phone Number *</label>
            <input type="tel" id="phone" name="phone" class="form-control" required value="{{ customer.phone }}">
        </div>

        <div class="form-group">
            <label for="status">Customer Status *</label>
            <select id="status" name="status" class="form-control" required>
                <option value="prospect" {% if customer.status == 'prospect' %}selected{% endif %}>Prospect</option>
                <option value="active" {% if customer.status == 'active' %}selected{% endif %}>Active</option>
                <option value="inactive" {% if customer.status == 'inactive' %}selected{% endif %}>Inactive</option>
            </select>
        </div>

        <div class="form-actions">
            <button type="submit" class="btn btn-primary">Update Customer</button>
            <a href="{{ url_for('customers') }}" class="btn btn-secondary">Cancel</a>
        </div>
    </form>
</div>
{% endblock %}
```

### 8. Customer Detail Page (`templates/customer_detail.html`)

```html
{% extends 'base.html' %}

{% block title %}{{ customer.name }} - CRM System{% endblock %}

{% block content %}
<div class="page-header">
    <h1>{{ customer.name }}</h1>
    <div class="header-actions">
        <a href="{{ url_for('edit_customer', customer_id=customer.id) }}" class="btn btn-secondary">Edit</a>
        <a href="{{ url_for('delete_customer', customer_id=customer.id) }}" class="btn btn-danger" onclick="return confirm('Delete this customer?')">Delete</a>
    </div>
</div>

<div class="detail-container">
    <div class="detail-section">
        <h2>Customer Information</h2>
        <div class="info-grid">
            <div class="info-item">
                <label>Name</label>
                <p>{{ customer.name }}</p>
            </div>
            <div class="info-item">
                <label>Email</label>
                <p><a href="mailto:{{ customer.email }}">{{ customer.email }}</a></p>
            </div>
            <div class="info-item">
                <label>Company</label>
                <p>{{ customer.company }}</p>
            </div>
            <div class="info-item">
                <label>Phone</label>
                <p><a href="tel:{{ customer.phone }}">{{ customer.phone }}</a></p>
            </div>
            <div class="info-item">
                <label>Status</label>
                <p>
                    <span class="badge {% if customer.status == 'active' %}badge-success{% elif customer.status == 'prospect' %}badge-warning{% else %}badge-error{% endif %}">
                        {{ customer.status }}
                    </span>
                </p>
            </div>
        </div>
    </div>

    <div class="detail-section">
        <h2>Contact History</h2>
        {% if contacts %}
        <div class="contact-timeline">
            {% for contact in contacts %}
            <div class="timeline-item">
                <div class="timeline-date">{{ contact.date }}</div>
                <div class="timeline-content">
                    <strong>{{ contact.contact_type|title }}</strong>
                    <p>{{ contact.notes }}</p>
                </div>
            </div>
            {% endfor %}
        </div>
        {% else %}
        <p class="text-muted">No contact history yet.</p>
        {% endif %}

        <div class="contact-form">
            <h3>Add Contact Record</h3>
            <form method="POST" action="{{ url_for('add_contact', customer_id=customer.id) }}">
                <div class="form-group">
                    <label for="contact_type">Contact Type</label>
                    <select id="contact_type" name="contact_type" class="form-control" required>
                        <option value="">Select type</option>
                        <option value="phone">Phone Call</option>
                        <option value="email">Email</option>
                        <option value="meeting">Meeting</option>
                        <option value="note">Note</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="notes">Notes</label>
                    <textarea id="notes" name="notes" class="form-control" required rows="3"></textarea>
                </div>
                <button type="submit" class="btn btn-primary">Record Contact</button>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

### 9. Leads List Template (`templates/leads.html`)

```html
{% extends 'base.html' %}

{% block title %}Leads - CRM System{% endblock %}

{% block content %}
<div class="page-header">
    <h1>Sales Leads</h1>
    <a href="{{ url_for('add_lead') }}" class="btn btn-primary">+ Add New Lead</a>
</div>

{% if leads %}
<div class="table-container">
    <table class="table">
        <thead>
            <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Company</th>
                <th>Email</th>
                <th>Value</th>
                <th>Source</th>
                <th>Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for lead in leads %}
            <tr>
                <td>{{ lead.id }}</td>
                <td><strong>{{ lead.name }}</strong></td>
                <td>{{ lead.company }}</td>
                <td>{{ lead.email }}</td>
                <td><strong>€{{ "{:,.2f}".format(lead.value) }}</strong></td>
                <td>{{ lead.source }}</td>
                <td>
                    <span class="badge {% if lead.status == 'new' %}badge-warning{% else %}badge-secondary{% endif %}">
                        {{ lead.status }}
                    </span>
                </td>
                <td class="actions">
                    <a href="{{ url_for('delete_lead', lead_id=lead.id) }}" class="btn btn-sm btn-danger" onclick="return confirm('Delete this lead?')">Delete</a>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<div class="stats-card">
    <h3>Lead Statistics</h3>
    <p><strong>Total Leads:</strong> {{ leads|length }}</p>
    <p><strong>Total Pipeline Value:</strong> €{{ "{:,.2f}".format(leads|sum(attribute='value')) }}</p>
</div>
{% else %}
<div class="empty-state">
    <p>No leads found. <a href="{{ url_for('add_lead') }}">Add your first lead</a></p>
</div>
{% endif %}
{% endblock %}
```

### 10. Add Lead Form (`templates/add_lead.html`)

```html
{% extends 'base.html' %}

{% block title %}Add Lead - CRM System{% endblock %}

{% block content %}
<div class="page-header">
    <h1>Add New Lead</h1>
</div>

<div class="form-container">
    <form method="POST" action="{{ url_for('add_lead') }}" class="form">
        <div class="form-group">
            <label for="name">Lead Name *</label>
            <input type="text" id="name" name="name" class="form-control" required placeholder="Enter contact name">
        </div>

        <div class="form-group">
            <label for="email">Email Address *</label>
            <input type="email" id="email" name="email" class="form-control" required placeholder="lead@example.com">
        </div>

        <div class="form-group">
            <label for="company">Company Name *</label>
            <input type="text" id="company" name="company" class="form-control" required placeholder="Company name">
        </div>

        <div class="form-group">
            <label for="value">Estimated Deal Value (€) *</label>
            <input type="number" id="value" name="value" class="form-control" min="0" step="0.01" required placeholder="0.00">
        </div>

        <div class="form-group">
            <label for="source">Lead Source *</label>
            <select id="source" name="source" class="form-control" required>
                <option value="">Select source</option>
                <option value="Website">Website</option>
                <option value="Email">Email</option>
                <option value="Phone">Phone Call</option>
                <option value="Referral">Referral</option>
                <option value="Social Media">Social Media</option>
                <option value="Trade Show">Trade Show</option>
            </select>
        </div>

        <div class="form-actions">
            <button type="submit" class="btn btn-primary">Add Lead</button>
            <a href="{{ url_for('leads') }}" class="btn btn-secondary">Cancel</a>
        </div>
    </form>
</div>
{% endblock %}
```

### 11. Error Pages (`templates/404.html` and `templates/500.html`)

**404.html:**
```html
{% extends 'base.html' %}

{% block title %}Page Not Found - CRM System{% endblock %}

{% block content %}
<div class="error-page">
    <h1>404</h1>
    <h2>Page Not Found</h2>
    <p>The page you're looking for doesn't exist.</p>
    <a href="{{ url_for('index') }}" class="btn btn-primary">Go to Dashboard</a>
</div>
{% endblock %}
```

**500.html:**
```html
{% extends 'base.html' %}

{% block title %}Server Error - CRM System{% endblock %}

{% block content %}
<div class="error-page">
    <h1>500</h1>
    <h2>Server Error</h2>
    <p>Something went wrong on our end. Please try again later.</p>
    <a href="{{ url_for('index') }}" class="btn btn-primary">Go to Dashboard</a>
</div>
{% endblock %}
```

### 12. Modern CSS Styling (`static/css/style.css`)

```css
/* ===========================
   CSS Variables & Theme
   =========================== */

:root {
    --primary-color: #3b82f6;
    --primary-dark: #1e40af;
    --secondary-color: #64748b;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --error-color: #ef4444;
    --background: #f8fafc;
    --surface: #ffffff;
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --border-color: #e2e8f0;
    --shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    --transition: all 0.3s ease;
}

/* ===========================
   Reset & Base Styles
   =========================== */

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    line-height: 1.6;
    color: var(--text-primary);
    background-color: var(--background);
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* ===========================
   Navigation
   =========================== */

.navbar {
    background-color: var(--surface);
    box-shadow: var(--shadow);
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 1000;
}

.navbar .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-brand h1 {
    font-size: 1.5rem;
    color: var(--primary-color);
}

.nav-menu {
    display: flex;
    list-style: none;
    gap: 1rem;
    align-items: center;
    flex-wrap: wrap;
}

.nav-link {
    text-decoration: none;
    color: var(--text-primary);
    padding: 0.5rem 1rem;
    border-radius: 6px;
    transition: var(--transition);
}

.nav-link:hover {
    background-color: var(--background);
    color: var(--primary-color);
}

/* ===========================
   Buttons
   =========================== */

.btn {
    display: inline-block;
    padding: 0.625rem 1.25rem;
    border-radius: 6px;
    text-decoration: none;
    font-weight: 500;
    transition: var(--transition);
    border: none;
    cursor: pointer;
    font-size: 0.9rem;
}

.btn-primary {
    background-color: var(--primary-color);
    color: white;
}

.btn-primary:hover {
    background-color: var(--primary-dark);
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

.btn-secondary {
    background-color: var(--secondary-color);
    color: white;
}

.btn-secondary:hover {
    background-color: #475569;
}

.btn-danger {
    background-color: var(--error-color);
    color: white;
}

.btn-danger:hover {
    background-color: #dc2626;
}

.btn-sm {
    padding: 0.375rem 0.75rem;
    font-size: 0.875rem;
}

/* ===========================
   Alerts & Notifications
   =========================== */

.alert {
    padding: 1rem;
    border-radius: 6px;
    margin: 1rem 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    animation: slideDown 0.3s ease;
}

@keyframes slideDown {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.alert-success {
    background-color: #d1fae5;
    color: #065f46;
    border-left: 4px solid var(--success-color);
}

.alert-error {
    background-color: #fee2e2;
    color: #991b1b;
    border-left: 4px solid var(--error-color);
}

.close-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    cursor: pointer;
    color: inherit;
    opacity: 0.7;
}

.close-btn:hover {
    opacity: 1;
}

/* ===========================
   Main Content
   =========================== */

main {
    min-height: calc(100vh - 200px);
    padding: 2rem 0;
}

/* ===========================
   Hero Section
   =========================== */

.hero {
    text-align: center;
    padding: 4rem 2rem;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 12px;
    margin-bottom: 3rem;
}

.hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.hero .lead {
    font-size: 1.25rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}

.hero-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}

/* ===========================
   Dashboard Stats
   =========================== */

.dashboard-stats {
    margin: 3rem 0;
}

.dashboard-stats h2 {
    font-size: 2rem;
    margin-bottom: 2rem;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
}

.stat-card {
    background: var(--surface);
    padding: 2rem;
    border-radius: 12px;
    box-shadow: var(--shadow);
    text-align: center;
    border-left: 4px solid var(--primary-color);
    transition: var(--transition);
}

.stat-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-lg);
}

.stat-number {
    font-size: 3rem;
    font-weight: bold;
    color: var(--primary-color);
    margin-bottom: 0.5rem;
}

.stat-label {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}

.stat-description {
    font-size: 0.9rem;
    color: var(--text-secondary);
}

/* ===========================
   Features Section
   =========================== */

.features {
    margin: 3rem 0;
}

.features h2 {
    text-align: center;
    font-size: 2rem;
    margin-bottom: 2rem;
}

.feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
}

.feature-card {
    background: var(--surface);
    padding: 2rem;
    border-radius: 12px;
    box-shadow: var(--shadow);
    text-align: center;
    transition: var(--transition);
}

.feature-card:hover {
    transform: translateY(-5px);
    box-shadow: var(--shadow-lg);
}

.feature-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.feature-card h3 {
    margin-bottom: 0.5rem;
    color: var(--primary-color);
}

.feature-card p {
    color: var(--text-secondary);
}

/* ===========================
   Page Header
   =========================== */

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid var(--border-color);
    flex-wrap: wrap;
    gap: 1rem;
}

.page-header h1 {
    font-size: 2rem;
}

.header-actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

/* ===========================
   Tables
   =========================== */

.table-container {
    background: var(--surface);
    border-radius: 12px;
    box-shadow: var(--shadow);
    overflow-x: auto;
    margin-bottom: 2rem;
}

.table {
    width: 100%;
    border-collapse: collapse;
}

.table thead {
    background-color: var(--primary-color);
    color: white;
}

.table th,
.table td {
    padding: 1rem;
    text-align: left;
}

.table tbody tr {
    border-bottom: 1px solid var(--border-color);
    transition: background-color 0.2s ease;
}

.table tbody tr:hover {
    background-color: var(--background);
}

.table .actions {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}

/* ===========================
   Badges
   =========================== */

.badge {
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 500;
    display: inline-block;
}

.badge-success {
    background-color: #d1fae5;
    color: #065f46;
}

.badge-warning {
    background-color: #fef3c7;
    color: #92400e;
}

.badge-error {
    background-color: #fee2e2;
    color: #991b1b;
}

.badge-secondary {
    background-color: #e2e8f0;
    color: #475569;
}

/* ===========================
   Stats Card
   =========================== */

.stats-card {
    background: var(--surface);
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: var(--shadow);
    margin-top: 2rem;
}

.stats-card h3 {
    margin-bottom: 1rem;
    color: var(--primary-color);
}

.stats-card p {
    margin: 0.5rem 0;
}

/* ===========================
   Forms
   =========================== */

.form-container {
    max-width: 600px;
    margin: 0 auto;
    background: var(--surface);
    padding: 2rem;
    border-radius: 12px;
    box-shadow: var(--shadow);
}

.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: var(--text-primary);
}

.form-control {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    font-size: 1rem;
    transition: var(--transition);
    font-family: inherit;
}

.form-control:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

textarea.form-control {
    resize: vertical;
    min-height: 100px;
}

.form-actions {
    display: flex;
    gap: 1rem;
    margin-top: 2rem;
    flex-wrap: wrap;
}

.form-actions .btn {
    flex: 1;
    min-width: 150px;
    text-align: center;
}

/* ===========================
   Detail View
   =========================== */

.detail-container {
    display: grid;
    grid-template-columns: 1fr;
    gap: 2rem;
}

.detail-section {
    background: var(--surface);
    padding: 2rem;
    border-radius: 12px;
    box-shadow: var(--shadow);
}

.detail-section h2 {
    margin-bottom: 1.5rem;
    color: var(--primary-color);
    border-bottom: 2px solid var(--border-color);
    padding-bottom: 0.5rem;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
}

.info-item label {
    display: block;
    font-weight: 600;
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-bottom: 0.25rem;
}

.info-item p {
    font-size: 1rem;
    color: var(--text-primary);
}

.info-item a {
    color: var(--primary-color);
    text-decoration: none;
}

.info-item a:hover {
    text-decoration: underline;
}

/* ===========================
   Contact Timeline
   =========================== */

.contact-timeline {
    margin-bottom: 2rem;
}

.timeline-item {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    padding-left: 1rem;
    border-left: 3px solid var(--primary-color);
}

.timeline-date {
    font-weight: 600;
    color: var(--text-secondary);
    font-size: 0.9rem;
    min-width: 120px;
}

.timeline-content strong {
    color: var(--text-primary);
}

.timeline-content p {
    color: var(--text-secondary);
    margin-top: 0.25rem;
}

.contact-form {
    background-color: var(--background);
    padding: 1.5rem;
    border-radius: 12px;
    margin-top: 2rem;
}

.contact-form h3 {
    margin-bottom: 1rem;
    color: var(--text-primary);
}

/* ===========================
   Empty State
   =========================== */

.empty-state {
    text-align: center;
    padding: 3rem;
    color: var(--text-secondary);
}

/* ===========================
   Error Page
   =========================== */

.error-page {
    text-align: center;
    padding: 4rem 2rem;
}

.error-page h1 {
    font-size: 6rem;
    color: var(--primary-color);
    margin-bottom: 1rem;
}

.error-page h2 {
    font-size: 2rem;
    margin-bottom: 1rem;
}

/* ===========================
   Footer
   =========================== */

.footer {
    background-color: var(--surface);
    padding: 2rem 0;
    margin-top: 4rem;
    text-align: center;
    color: var(--text-secondary);
    box-shadow: 0 -1px 3px rgba(0, 0, 0, 0.1);
}

/* ===========================
   Responsive Design
   =========================== */

@media (max-width: 768px) {
    .navbar .container {
        flex-direction: column;
        gap: 1rem;
    }

    .nav-menu {
        justify-content: center;
    }

    .hero h1 {
        font-size: 2rem;
    }

    .hero-buttons {
        flex-direction: column;
    }

    .hero-buttons .btn {
        width: 100%;
    }

    .page-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .page-header h1 {
        width: 100%;
    }

    .table-container {
        font-size: 0.9rem;
    }

    .table th,
    .table td {
        padding: 0.75rem 0.5rem;
    }

    .form-actions {
        flex-direction: column;
    }

    .form-actions .btn {
        width: 100%;
    }

    .stats-grid {
        grid-template-columns: 1fr;
    }

    .feature-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 480px) {
    .container {
        padding: 0 10px;
    }

    .hero h1 {
        font-size: 1.5rem;
    }

    .page-header h1 {
        font-size: 1.5rem;
    }

    .btn-sm {
        padding: 0.25rem 0.5rem;
        font-size: 0.75rem;
    }

    .table .actions {
        flex-direction: column;
    }

    .table .actions .btn-sm {
        width: 100%;
    }
}
```

### 13. JavaScript Enhancements (`static/js/script.js`)

```javascript
// script.js
// Optional JavaScript for enhanced interactivity

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.3s ease';
            setTimeout(() => {
                alert.style.display = 'none';
            }, 300);
        }, 5000);
    });

    // Add active state to navbar links
    const currentLocation = location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });
});
```

---

## How to Run the Application

### Installation & Setup

#### Step 1: Create Project Directory

```bash
mkdir crm_system
cd crm_system
```

#### Step 2: Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

#### Step 3: Install Flask

```bash
pip install flask
```

#### Step 4: Create Project Structure

```bash
# Create folders
mkdir static
mkdir static/css
mkdir static/js
mkdir templates

# Create files
touch app.py
touch models.py
touch static/css/style.css
touch static/js/script.js
```

#### Step 5: Copy Code into Files

Copy the code from sections 1-13 above into their respective files.

#### Step 6: Run the Application

```bash
python app.py
```

#### Step 7: Access the Application

Open your browser and navigate to: **http://127.0.0.1:5000/**

---

## Key Concepts Explained

### 1. Jinja2 Templating

Flask uses Jinja2 for templating, which allows you to:

**Template Inheritance:**
```html
<!-- base.html defines the structure -->
{% block content %}{% endblock %}

<!-- child template extends base -->
{% extends 'base.html' %}
{% block content %}
    <!-- Child content here -->
{% endblock %}
```

**Variables & Expressions:**
```html
<!-- Display variables -->
{{ variable_name }}

<!-- Filters -->
{{ customer.name|upper }}
{{ price|round(2) }}

<!-- URL generation -->
<a href="{{ url_for('customer_detail', customer_id=customer.id) }}">View</a>
```

**Control Structures:**
```html
<!-- Loops -->
{% for customer in customers %}
    <p>{{ customer.name }}</p>
{% endfor %}

<!-- Conditionals -->
{% if customer.status == 'active' %}
    <span>Active</span>
{% elif customer.status == 'prospect' %}
    <span>Prospect</span>
{% else %}
    <span>Inactive</span>
{% endif %}
```

### 2. Routing & Request Handling

```python
# Basic route
@app.route('/path')
def function_name():
    return render_template('template.html')

# Route with methods
@app.route('/path', methods=['GET', 'POST'])
def handle_request():
    if request.method == 'POST':
        # Process form data
        data = request.form.get('field_name')
    return render_template('template.html')

# Route with URL parameters
@app.route('/customers/<int:customer_id>')
def customer_detail(customer_id):
    customer = Customer.get_customer_by_id(customer_id)
    return render_template('detail.html', customer=customer)

# URL with query parameters
@app.route('/search')
def search():
    query = request.args.get('q')
    # Process search
```

### 3. Flash Messages for User Feedback

```python
# In controller
from flask import flash

@app.route('/add', methods=['POST'])
def add_item():
    # ... create item ...
    flash('Item added successfully!', 'success')
    return redirect(url_for('list_items'))
```

```html
<!-- In template -->
{% with messages = get_flashed_messages(with_categories=true) %}
    {% for category, message in messages %}
        <div class="alert alert-{{ category }}">
            {{ message }}
        </div>
    {% endfor %}
{% endwith %}
```

### 4. Static Files

```html
<!-- CSS -->
<link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">

<!-- JavaScript -->
<script src="{{ url_for('static', filename='js/script.js') }}"></script>

<!-- Images -->
<img src="{{ url_for('static', filename='images/logo.png') }}">
```

### 5. Class Methods & Data Management

```python
class Customer:
    customers = []  # Class variable
    
    def __init__(self, name):
        self.name = name
    
    @classmethod
    def add_customer(cls, name):
        customer = cls(name)
        cls.customers.append(customer)
        return customer
    
    @classmethod
    def get_all_customers(cls):
        return cls.customers
```

---

## Best Practices

### 1. **Separation of Concerns**
- Keep models, controllers, and views separate
- Each file has a single responsibility
- Models handle data, controllers handle requests, views display data

### 2. **Template Best Practices**
- Use template inheritance (base.html) to avoid repetition
- Use Jinja2 filters and tags effectively
- Keep business logic out of templates

### 3. **Form Handling**
- Always validate user input on the server side
- Use flash messages for user feedback
- Handle POST requests properly with redirects

### 4. **Error Handling**
- Create custom error pages (404, 500)
- Validate data before processing
- Provide meaningful error messages

### 5. **CSS & Styling**
- Use CSS variables for consistent theming
- Implement responsive design with media queries
- Use modern layout techniques (Flexbox, Grid)

### 6. **Security**
- Set a strong `secret_key` (don't use default values)
- Never commit sensitive data to version control
- Validate all user inputs
- Use environment variables for configuration

### 7. **Code Organization**
- Use meaningful function and variable names
- Add docstrings to functions
- Keep functions focused and single-purpose
- Add comments for complex logic

### 8. **Development Workflow**
- Only use `debug=True` in development
- Use a version control system (Git)
- Test frequently during development
- Document your code

---

## Extension Ideas

Here are ways to extend this CRM system:

1. **Database Integration** - Replace in-memory storage with SQLite/PostgreSQL
2. **User Authentication** - Add login/logout functionality
3. **Search & Filtering** - Allow users to search customers
4. **Export to CSV** - Generate reports
5. **Email Integration** - Send notifications
6. **Dashboard Charts** - Visualize business metrics
7. **Customer Notes** - Add detailed notes to customers
8. **Pipeline Management** - Track deal stages
9. **Mobile Responsiveness** - Already included!
10. **API Endpoints** - Build a REST API

---

## Troubleshooting

### Common Issues

**Issue:** Flask app won't start
- Check that Flask is installed: `pip list | grep flask`
- Verify Python version: `python --version`
- Ensure you're in the virtual environment

**Issue:** Templates not found
- Check folder names (must be `templates/`, not `template/`)
- Verify file paths in `render_template()`

**Issue:** CSS/JS not loading
- Clear browser cache (Ctrl+Shift+Del)
- Check console for errors (F12)
- Verify file paths with `url_for()`

**Issue:** Form data not being sent
- Ensure form method is POST: `<form method="POST">`
- Check that form fields have `name` attributes
- Verify CSRF token if implementing security

---

## Summary

This comprehensive Flask CRM guide covers:
✅ MVC pattern explanation with real examples
✅ Complete working CRM application
✅ Template inheritance (base.html)
✅ Modern, responsive CSS design
✅ CRUD operations
✅ Form handling & validation
✅ Flash messages for user feedback
✅ Error handling & custom pages
✅ Best practices & security
✅ Code organization & structure

Use this guide as a teaching resource to help students understand Flask fundamentals and build professional web applications!

---

**Happy teaching! 🎓**