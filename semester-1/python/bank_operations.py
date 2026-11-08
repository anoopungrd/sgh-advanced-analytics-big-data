from bank import Customer, Account, Bank

b = Bank('SGH Bank')
c1 = b.create_customer('John', 'Smith')
c2 = b.create_customer('Anne', 'Brown')
a1 = b.create_account(c1, 'USD')
a2 = b.create_account(c2, 'USD')
a3 = b.create_account(c1, 'USD')
a4 = b.create_account(c2, 'USD')
print(b)

# Add deposit and withdraw methods and show how they can be used