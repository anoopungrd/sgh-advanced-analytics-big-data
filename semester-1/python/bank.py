class Customer:
    last_id = 0
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
        Customer.last_id = Customer.last_id + 1
        self.id = Customer.last_id

    def __repr__(self):
        return f"C({self.id}, {self.first_name}, {self.last_name})"

class Account:
    last_id = 1000

    def __init__(self, customer, currency='PLN'):
        self.customer = customer
        self._balance = 0
        Account.last_id += 1
        self.id = Account.last_id
        self.currency = currency


    def __repr__(self):
        return f"A({self.id}, {self.customer.last_name}, {self._balance} {self.currency})"


class Bank:
    def __init__(self, name):
        self.name = name
        self.customers = []
        self.accounts = []

    def create_customer(self, first_name, last_name):
        customer = Customer(first_name, last_name)
        self.customers.append(customer)
        return customer

    def create_account(self, customer, currency = 'PLN'):
        account = Account(customer, currency)
        self.accounts.append(account)
        return account

    def __repr__(self):
        return f"B({self.name}, \n{self.customers}, \n{self.accounts})"

    # def bank_withdrawal(self, amount):
    #     self.amount = amount