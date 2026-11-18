import decimal
import datetime

CREDIT_TYPES = {"Deposit", "Transfer in", "Interest"}        # increase the balance
DEBIT_TYPES = {"Withdrawal", "Transfer out"}                 # decrease the balance
TRANSACTION_TYPES = CREDIT_TYPES | DEBIT_TYPES               # all valid types

class Customer:
    last_id = 0
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name
        Customer.last_id = Customer.last_id + 1
        self.id = Customer.last_id

    def __repr__(self):
        return f"C({self.id}, {self.first_name}, {self.last_name})"

class AccountTransaction:
    """History of operations, and it is read only"""
    last_id = 0

    def __init__(self, account_id, transaction_type, amount, balance_after, currency,
                 description="", related_account_id=None):
        if transaction_type not in TRANSACTION_TYPES:
            raise BankException(f"Unknown transaction type: {transaction_type!r}")
        AccountTransaction.last_id += 1
        # object.__setattr__ is used because __setattr__ is blocked below
        for name, value in (("id", AccountTransaction.last_id),
                            ("timestamp", datetime.datetime.now()),  # exact date and time
                            ("account_id", account_id),
                            ("transaction_type", transaction_type),
                            ("amount", amount),  # always positive
                            ("balance_after", balance_after),  # balance after this operation
                            ("currency", currency),
                            ("description", description),
                            ("related_account_id", related_account_id)):  # other side of a transfer
            object.__setattr__(self, name, value)

    def __setattr__(self, name, value):
        raise AttributeError("AccountTransaction is read-only")

    def signed_amount(self):
        """+amount for operations that add money, -amount for those that remove it."""
        return self.amount if self.transaction_type in CREDIT_TYPES else -self.amount

    def __str__(self):
        when = self.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]  # to milliseconds
        return (f"#{self.id:<4} {when}  {self.transaction_type:<13} "
                f"{self.signed_amount():>+14,.2f} {self.currency}  "
                f"balance: {self.balance_after:>14,.2f}  {self.description}")

    def __repr__(self):
        return (f"T({self.id}, {self.transaction_type}, {self.signed_amount()} "
                f"{self.currency}, {self.timestamp.isoformat()})")


class Account:
    last_id = 1000
    yearly_interest_rate = 0.02  # TODO - will be used to update the interest rate
    days_in_year = 365
    days = 30
    max_transaction_amt = 1000000

    def __init__(self, customer, currency='PLN'):
        self.customer = customer
        self._balance = decimal.Decimal('0.00')
        Account.last_id += 1
        self.id = Account.last_id
        self.currency = currency
        self.transactions = [] # Added for full history of AccountTransaction objects

    def balance(self):
        return self._balance

    # TODO DONE - ADDED CODE TO VALIDATE AMOUNT
    def _validate_amount(self,amount):
        if isinstance(amount, bool) or not isinstance(amount, (int, float, decimal.Decimal)):
            raise InvalidAmountException(
                f"Amount must be a number")
        value = decimal.Decimal(str(amount))

        if value < 0:
            raise InvalidAmountException(f"Amount must be greater than zero")

        if value > self.max_transaction_amt:
            raise InvalidAmountException(f"Amount must be less than {self.max_transaction_amt}")

        rounded = value.quantize(decimal.Decimal('0.00'))
        if value != rounded:
            raise InvalidAmountException(f"Amount must have at most 2 decimal places")

        return rounded

    def _record_transaction(self, transaction_type, amount, description="", related_account_id=None):
        """Create an AccountTransaction and add it to this account's history.Must be called right AFTER the balance was changed, so that
        balance_after in the record is correct.
        """
        transaction = AccountTransaction(self.id, transaction_type, amount, self._balance,
                                         self.currency, description, related_account_id)
        self.transactions.append(transaction)
        return transaction

    def deposit(account, amount):
        amount = account._validate_amount(amount)
        account._balance += amount
        print(f"Deposited {amount} to {account}")

    # code for creating withdraw method
    def withdraw(account, amount):
        amount = account._validate_amount(amount)
        if account._balance >= amount:
            account._balance -= amount
            print(f"Withdrew {amount} from {account}")
        else:
            #p = 5546 + 'fsdfg'
            raise InsufficientBalanceException(f'Insufficient balance to withdraw: {amount}')
            #print("Insufficient funds")

    # Add one day of simple interest to this account and return the amount added.
    # Simple interest rate = principal * daily_rate * days
    def add_daily_interest(self):
        rate = self.yearly_interest_rate
        if isinstance(rate, bool) or not isinstance(rate, (int, float, decimal.Decimal)) \
                or not (0 <= rate <= 1):
            raise BankException(f"Invalid yearly interest rate: {rate!r} (expected 0 <= rate < 1)")

        if isinstance(self.days_in_year, bool) or not isinstance(self.days_in_year, int) \
                or self.days_in_year <= 0:
            raise BankException(f"Invalid days_in_year: {self.days_in_year!r}")

        if isinstance(self.days, bool) or not isinstance(self.days, int) or self.days <= 0:
            raise BankException(f"days must be a positive integer, got {self.days!r}")

        # convert the float rate to Decimal
        #daily_rate = (self.yearly_interest_rate / self.days_in_year).quantize(decimal.Decimal("0.01"), rounding=decimal.ROUND_HALF_UP)
        daily_rate = decimal.Decimal(str(rate)) / self.days_in_year
        #Round the final amount
        interest = (self._balance * daily_rate * self.days).quantize(decimal.Decimal("0.01"), rounding=decimal.ROUND_HALF_UP)
        self._balance += interest
        # Recorded on every run, also when the interest is 0.00
        self._record_transaction("Interest", interest,
                                 f"Daily interest ({decimal.Decimal(str(rate)) * 100:.2f}% p.a.)")
        return interest

    # Checking ACCOUNT HISTORY
    def get_transactions(self, transaction_type=None, start=None, end=None):
        """Return this account's transactions (oldest first).
        Optional filters are only one type (e.g. "Interest"), and/or only those between
        the datetimes `start` and `end` (both inclusive).
        """
        if transaction_type is not None and transaction_type not in TRANSACTION_TYPES:
            raise BankException(f"transaction_type must be one of {sorted(TRANSACTION_TYPES)}, "
                                f"got {transaction_type!r}")
        for name, value in (("start", start), ("end", end)):
            if value is not None and not isinstance(value, datetime.datetime):
                raise BankException(f"{name} must be a datetime, got {value!r}")
            return [t for t in self.transactions
                    if (transaction_type is None or t.transaction_type == transaction_type)
                    and (start is None or t.timestamp >= start)
                    and (end is None or t.timestamp <= end)]

    def get_statement(self, transaction_type=None, start=None, end=None):
        """Full historical report of the account as a printable string."""
        line = "-" * 110
        lines = [f"Statement of account {self.id} ({self.customer.first_name} "
                 f"{self.customer.last_name}, {self.currency})", line]
        transactions = self.get_transactions(transaction_type, start, end)
        lines += [str(t) for t in transactions] or ["(no transactions)"]
        lines += [line, f"Current balance: {self._balance:,.2f} {self.currency}"]
        return "\n".join(lines)

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

    def transfer_money(self, from_account_id, to_account_id, amount):
        # TODO - as part of the home assignment please implement this method - as names suggest the input parameters are
        # ids of the accounts to transfer money from and to and amount to transfer. You may need a helper method to find
        # those accounts based on their ids.
        #Find both accounts and validate the ids:
        from_account = self.find_account(from_account_id)
        to_account = self.find_account(to_account_id)

        # Business Rules:
        if from_account is to_account:
            raise InvalidTransferException("Cannot transfer money to the same account")
        if from_account.currency != to_account.currency:
            raise InvalidTransferException(f"Currency mismatch: {from_account.currency} -> {to_account.currency} "
                                           "(currency conversion is not supported)")
        # Amount validation uses same rules as deposit and withdraw
        amount = from_account._validate_amount(amount)
        if amount > from_account._balance:
            raise InsufficientBalanceException(
                f"Insufficient balance to transfer: {amount} (available: {from_account._balance})")

        from_account._balance -= amount
        to_account._balance += amount
        from_account._record_transaction("Transfer out", amount,
                                         f"Transfer to account {to_account.id}", to_account.id)
        to_account._record_transaction("Transfer in", amount,
                                       f"Transfer from account {from_account.id}", from_account.id)

        print(f"Transferred {amount} {from_account.currency} from {from_account} to {to_account}")

    def run_daily_interest_updater(self):
        # TODO - as part of the home assignment please implement this method
        # Calculating simple interest using simple daily rate formula
        # Simple interest rate = principal * daily_rate * days
        totals = {}
        for account in self.accounts:
            interest = account.add_daily_interest()
            totals[account.currency] = totals.get(account.currency, decimal.Decimal("0.00")) + interest
        print(f"Daily interest paid by {self.name}: {({c: str(v) for c, v in totals.items()})}")
        return totals

        #pass

    # Return the account with the given id, or raise AccountNotFoundException.
    def find_account(self, account_id):

        if isinstance(account_id, bool) or not isinstance(account_id, int):
            raise InvalidTransferException(f"Account id must be an integer, got {account_id!r}")

        for account in self.accounts:
            if account.id == account_id:
                return account
        raise AccountNotFoundException(f"Account {account_id} not found in {self.name}")

    def __repr__(self):
        return f"B({self.name}, \n{self.customers}, \n{self.accounts})"

class BankException(Exception):
    pass

class InsufficientBalanceException(BankException):
    pass

class InvalidAmountException(Exception):
    pass

class AccountNotFoundException(BankException):
    pass

class InvalidTransferException(BankException):
    pass


##############################################################################
## Testing the bank functions
# bank = Bank("SGH Bank")
# anoop = bank.create_customer("anoop","surendran")
# aadi = bank.create_customer("aadi","roblox")
# acc_anoop = bank.create_account(anoop)  ## default PLN currency
# acc_aadi = bank.create_account(aadi)  ## one more account with default PLN currency
# acc_aadi_euro = bank.create_account(aadi, 'EUR')  ## Multi-currency for the customer
# print(bank)

## Testing deposits and withdrawals
# acc_anoop.deposit(1000)
# acc_anoop.deposit(200.50)  ## Storing decimals as well
#
# acc_anoop.withdraw(500)
# acc_aadi.deposit(50)

## Transfer between two accounts
# bank.transfer_money(acc_anoop.id, acc_aadi.id, 300)  ##Accounts found by ID
# print(bank)

## VALIDATION: EVERY UNSAFE OPERATION IS REJECTED. I RAN WITHOUT THE TRY BLOCK, BUT IT RESETS
## THE OBJECTS TO 0.00. HENCE, I AM PUTTING IT IN A TRY CATCH BLOCK
# try:
#     acc_anoop.deposit(-50)       # expected to fail
# except BankException as e:
#     print("Rejected:", e)

## RUNNING ALL ERROR TESTS WITH TRY BLOCK TO AVOID OBJECT RESETS TO 0.00 BALANCE
# try:
#     acc_anoop.deposit("10")   # expected to fail
# except BankException as e:
#     print("Rejected:", e)

# try:
#     acc_anoop.deposit("nan")  #expected to fail
# except BankException as e:
#     print("Rejected:", e)

# try:
#     acc_anoop.deposit(5000000000)    # Trying to deposit a huge amount above the limit
# except BankException as e:
#     print("Rejected:", e)

# try:
#     bank.transfer_money(acc_anoop.id, 9999, 10)   # Trying to deposit a huge amount above the limit.
# except BankException as e:                                            # No transfer happens
#     print("Rejected:", e)

#Transfer to a wrong id will not update the amount
# try:
#     bank.transfer_money("1000", acc_aadi, 10)   # Trying to deposit a huge amount above the limit.
# except InvalidTransferException as e:                                            # No transfer happens
#     print("Rejected:", e)

#Transfer between different currencies. No transfer happens
# try:
#     bank.transfer_money(acc_anoop.id, acc_aadi_euro.id, 10)
# except InvalidTransferException as e:
#     print("Rejected:", e)

#Transfer money above balance. Throws error and no transfer happens
# try:
#     bank.transfer_money(acc_aadi.id, acc_anoop.id, 99_999)
# except InvalidTransferException as e:
#     print("Rejected:", e)

# Daily interest calculation for 3 days and update the account
# for day in range(1, 4):
#         print(f"Day {day}:", end=" ")
#         bank.run_daily_interest_updater()

# Checking transaction history
#print(acc_anoop.get_statement(), "\n")
#print(acc_aadi.get_statement(), "\n")

# Transaction history cannot be modified
# Error: Rejected - modifying a recorded transaction: AttributeError: AccountTransaction is read-only
# try:
#     acc_anoop.transactions[0].amount = 1
# except AttributeError as e:
#         print(f"  Rejected - modifying a recorded transaction: AttributeError: {e}")

# print(bank)
