import sqlite3

DB_NAME = "crm.db"


class Customer:
    customers = []
    next_id = 1

    def __init__(self, name, email, company, phone, status="prospect"):
        self.id = Customer.next_id
        Customer.next_id += 1
        self.name = name
        self.email = email
        self.company = company
        self.phone = phone
        self.status = status

    @classmethod
    def add_customer(cls, name, email, company, phone, status="prospect"):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO customers (name, email, company, phone, status)
            VALUES (?, ?, ?, ?, ?)
        """, (name, email, company, phone, status))

        conn.commit()
        customer_id = cursor.lastrowid
        conn.close()

        customer = cls(name, email, company, phone, status)
        customer.id = customer_id
        cls.customers.append(customer)
        return customer

    #Zmieniam gdzie zapisuje nowo dodanych uzytkownikkow 

    @classmethod
    def get_all_customers(cls):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("SELECT id, name, email, company, phone, status FROM customers")
        rows = cursor.fetchall()
        conn.close()

        customers = []
        for row in rows:
            customer = cls(row[1], row[2], row[3], row[4], row[5])
            customer.id = row[0]
            customers.append(customer)

        return customers

    # teraz dane będą pobierane z tabeli customers w crm.db 


    @classmethod
    def get_customer_by_id(cls, customer_id):
        for customer in cls.customers:
            if customer.id == customer_id:
                return customer
        return None

    @classmethod
    def update_customer(cls, customer_id, name, email, company, phone, status):
        customer = cls.get_customer_by_id(customer_id)
        if customer:
            customer.name = name
            customer.email = email
            customer.company = company
            customer.phone = phone
            customer.status = status




# dziala usuwanie customers z listy
# podmieniam ta linie zeby mi sie w kolko nie zapisywali ci sami customers od nowa

    @classmethod
    def delete_customer(cls, customer_id):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))

        conn.commit()
        conn.close()


class Lead:
    leads = []
    next_id = 1

    def __init__(self, name, email, company, value, source):
        self.id = Lead.next_id
        Lead.next_id += 1
        self.name = name
        self.email = email
        self.company = company
        self.value = value
        self.source = source
        self.status = "new"

    @classmethod
    def add_lead(cls, name, email, company, value, source):
        lead = cls(name, email, company, value, source)
        cls.leads.append(lead)
        return lead

    @classmethod
    def get_all_leads(cls):
        return cls.leads

    @classmethod
    def get_lead_by_id(cls, lead_id):
        for lead in cls.leads:
            if lead.id == lead_id:
                return lead
        return None

    @classmethod
    def delete_lead(cls, lead_id):
        lead = cls.get_lead_by_id(lead_id)
        if lead:
            cls.leads.remove(lead)


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        company TEXT,
        phone TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()