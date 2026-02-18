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
        customer = cls(name, email, company, phone, status)
        cls.customers.append(customer)
        return customer

    @classmethod
    def get_all_customers(cls):
        return cls.customers

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
    # the update_customer method is defined as a class method
    # it retrieves the customer by ID and updates its attributes
    # the reason for using class method is to maintain consistency with other methods
    # it allows direct access to the class-level customer list

    @classmethod
    def delete_customer(cls, customer_id):
        customer = cls.get_customer_by_id(customer_id)
        if customer:
            cls.customers.remove(customer)

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
