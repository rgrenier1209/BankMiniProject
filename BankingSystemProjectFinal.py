import csv

# --- Classes for Bank Entities ---

class Customer():
    # Initializes a new customer instance with personal details
    def __init__(self, Customer_ID, First_Name, Last_Name, SSN, Email, Phone_Number, Join_Date):
        self.customer_id = Customer_ID
        self.first_name = First_Name
        self.last_name = Last_Name
        self.ssn = SSN
        self.email = Email
        self.phone_number = Phone_Number
        self.join_date = Join_Date
        self.accounts = []
    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.customer_id})"
    
class Employee():
    # Stores employee information and checks permission levels based on roles
    def __init__(self, staff_id, company, department, first_name, last_name, email, role):
        self.staff_id = staff_id
        self.company = company
        self.department = department
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.role = role

    def can_perform(self, action):
        # Defines the list of authorized actions for each employee role
        permissions = {
            "Teller": ["list_customers", "list_accounts", "deposit_withdraw"],
            "Loan Officer": ["list_customers", "list_accounts", "manage_loans"],
            "Branch Manager": ["list_customers", "list_accounts", "list_employees", "deposit_withdraw", "manage_loans"]
        }
        role_actions = permissions.get(self.role, [])
        return action in role_actions
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.role} ({self.department})"
        
# --- Account Hierarchy ---

class Account():
    # Base class representing the foundation of all account types
    def __init__(self, Account_Number, Customer_ID,Account_Type,Balance):
        self.account_number = Account_Number
        self.customer_id = Customer_ID
        self.account_type = Account_Type
        self._balance = float(Balance)

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        # Logic to ensure balance updates remain non-negative
        if value < 0:
            print("Error: Balance cannot be negative.")
        else:
            self._balance = float(value)

    def __str__(self):
        return f"{self.account_number} {self.account_type} {self.balance} (ID: {self.customer_id})"
    
class Assets(Account):
    # Extension for accounts that allow money in and out
    def __init__(self, Account_Number, Customer_ID,Account_Type,Balance):
        super().__init__(Account_Number, Customer_ID,Account_Type,Balance)
    def deposit (self, amount):
        self.balance = self.balance + amount
        return self.balance
    def withdraw (self, amount):
        # Validation to prevent overdrawing funds
        if self.balance - amount < 0:
            raise ValueError("Insufficient funds: Cannot withdraw more than the balance.")
        else:
            self.balance = self.balance - amount
        return self.balance
    
class Savings(Assets):
    # Specialized account incorporating interest earnings
    def __init__(self, Account_Number, Customer_ID,Account_Type,Balance, InterestAPY):
        super().__init__(Account_Number, Customer_ID,Account_Type,Balance)
        self.interestAPY = InterestAPY

    def apply_interest(self):
        interest_earned = self.balance * self.interestAPY
        self.deposit(interest_earned)
        print(f"Interest of {interest_earned:,.2f} added to account {self.account_number}.")
    
    def __str__(self):
        return f"{self.account_number} ({self.account_type}) | Balance: ${self.balance:,.2f} | APY: {self.interestAPY:.2%} (ID: {self.customer_id})"

class Checking(Assets):
    # Specialized account incorporating monthly maintenance fees
    def __init__(self, Account_Number, Customer_ID,Account_Type,Balance, Monthly_Fee):
        super().__init__(Account_Number, Customer_ID,Account_Type,Balance)
        self.monthly_fee = Monthly_Fee

    def apply_monthly_fee(self):
        if self.balance < 1000:
            self.withdraw(self.monthly_fee)
            print(f"Fee of ${self.monthly_fee:,.2f} charged to {self.account_number}.")
        else:
            print("Balance above $1,000. No fee applied.")
    
    def apply_overdraft_fee(self, fee_amount):
        if self.balance < 0:
            self.withdraw(fee_amount)
            print(f"Overdraft fee of ${fee_amount:,.2f} applied to {self.account_number}.")
        else:
            print("No overdraft fee needed.")

    def __str__(self):
        return f"{self.account_number} ({self.account_type}) | Balance: ${self.balance:,.2f} (ID: {self.customer_id})"

class Debts(Account):
    # Base class for debt-related accounts
    def __init__(self, Account_Number, Customer_ID,Account_Type,Balance, Interest_Rate):
        super().__init__(Account_Number, Customer_ID,Account_Type,Balance)
        self.interest_rate = Interest_Rate

    def make_payment (self, amount):
        self.balance = self.balance - amount
        return self.balance
    
    def add_charge(self, amount):
        self.balance = self.balance + amount
        return self.balance
    
    def apply_interest(self):
        interest = self.balance * (self.interest_rate / 12)
        self.add_charge(interest)
        return self.balance
    
    def __str__(self):
        return f"{self.account_number} ({self.account_type}) | Balance: ${self.balance:,.2f} | Rate: {self.interest_rate:.2%} (ID: {self.customer_id})"    

class CreditCard(Debts):
    # Debt account requiring credit limit enforcement
    def __init__(self, Account_Number, Customer_ID, Account_Type, Balance, Interest_Rate, Credit_Limit, Term_Months):
        super().__init__(Account_Number, Customer_ID, Account_Type, Balance, Interest_Rate)
        self.credit_limit = Credit_Limit

    def add_charge(self, amount):
        if self.balance + amount > self.credit_limit:
            print("Transaction declined: Over credit limit.")
            return self.balance
        else:
            return super().add_charge(amount)

class Loan(Debts):
    # Debt account with term-based payment structures
    def __init__(self, Account_Number, Customer_ID, Account_Type, Balance, Interest_Rate, Term_Months):
        super().__init__(Account_Number, Customer_ID, Account_Type, Balance, Interest_Rate)
        self.term_months = Term_Months

    def get_monthly_payment(self):
        if self.term_months > 0:
            return self.balance / self.term_months
        return 0

# --- Bank System Management ---

class Bank():
    # Manages data aggregation and core banking operations
    def __init__(self,savings_interest_rate = 0.03, Monthly_Fee = 15.00):
        self.accounts = []
        self.customers = []
        self.employees = []
        self.savings_interest_rate = savings_interest_rate
        self.monthly_fee = Monthly_Fee
    
    # Imports customer registry from source CSV
    def loadcustomers(self,filename):
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                new_cust = Customer(
                    row['Customer_ID'].strip(), 
                    row['First_Name'].strip(), 
                    row['Last_Name'].strip(), 
                    row['SSN'].strip(), 
                    row['Email'].strip(), 
                    row['Phone_Number'].strip(), 
                    row['Join_Date'].strip()
                )
                self.customers.append(new_cust)
    
    # Imports employee registry from source CSV
    def loademployees(self, filename):
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                new_emp = Employee(
                    row['staff id'].strip(),
                    row['company'].strip(),
                    row['organization department'].strip(),
                    row['1st name'].strip(),
                    row['last name'].strip(),
                    row['email'].strip(),
                    row['role'].strip()
                )
                self.employees.append(new_emp)

    # Loads and categorizes account types from CSV
    def loadaccounts(self, filename):
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['Account_Type'] == 'Savings':
                        new_acc = Savings(row['Account_Number'].strip(), 
                                          row['Customer_ID'].strip(), 
                                          row['Account_Type'].strip(), 
                                          row['Balance'].strip(), 
                                          InterestAPY = self.savings_interest_rate)
                        self.accounts.append(new_acc)
                elif row['Account_Type'] == 'Checking':
                        new_acc = Checking(row['Account_Number'].strip(), 
                                           row['Customer_ID'].strip(), 
                                           row['Account_Type'].strip(), 
                                           row['Balance'].strip(), 
                                           Monthly_Fee=self.monthly_fee)
                        self.accounts.append(new_acc)
                elif row['Account_Type'] == 'Credit Card':
                        new_acc = CreditCard(row['Account_Number'].strip(), 
                                             row['Customer_ID'].strip(), 
                                             row['Account_Type'].strip(), 
                                             row['Balance'].strip(), 
                                             float(row['Interest_Rate']), 
                                             float(row['Credit_Limit']), 
                                             row['Term_Months'].strip())
                        self.accounts.append(new_acc)
                elif row['Account_Type'] == 'Loan':
                        new_acc = Loan(row['Account_Number'].strip(), 
                                       row['Customer_ID'].strip(), 
                                       row['Account_Type'].strip(), 
                                       row['Balance'].strip(), 
                                       float(row['Interest_Rate']), 
                                       int(row['Term_Months']))
                        self.accounts.append(new_acc)
        print(f"DEBUG: Finished loading. Total accounts in list: {len(self.accounts)}")

    # Updates the persistent CSV file with latest in-memory account data
    def saveaccounts(self, filename):
        with open(filename, mode='w', newline='') as file:
            fieldnames = ['Account_Number', 'Customer_ID', 'Account_Type', 'Balance', 'Interest_Rate', 'Credit_Limit', 'Term_Months']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for acc in self.accounts:
                row = {
                    'Account_Number': acc.account_number,
                    'Customer_ID': acc.customer_id,
                    'Account_Type': acc.account_type,
                    'Balance': acc.balance
                }
                if isinstance(acc, Debts):
                    row['Interest_Rate'] = acc.interest_rate
                if isinstance(acc, CreditCard):
                    row['Credit_Limit'] = acc.credit_limit
                if isinstance(acc, Loan):
                    row['Term_Months'] = acc.term_months
                writer.writerow(row)
        print("Data saved successfully.")

# --- Main Program Execution ---

def main():
    # Initializes bank instance and loads all initial datasets
    my_bank = Bank()
    my_bank.loadcustomers('Customers.csv')
    my_bank.loadaccounts('Accounts.csv')
    my_bank.loademployees('Employees.csv')

    # Performs secure ID-based login
    print("--- Bank Employee Login ---")
    staff_id = input("Enter Staff ID: ")
    current_employee = next((e for e in my_bank.employees if e.staff_id == staff_id), None)
    
    if not current_employee:
        print("Employee not found. Access denied.")
        return 
    
    print(f"Welcome, {current_employee.first_name}. Your role is: {current_employee.role}")

    # Maintains active menu loop for continuous operations
    while True:
        print("\n--- Banking System Menu ---")
        print("1. List Customers | 2. List Employees | 3. List Accounts | 4. Transactions | 6. Exit")
        choice = input("Enter your choice: ")
        
        # Manages menu selections and permission-based routing
        if choice == '1':
            for c in my_bank.customers: print(c)
        elif choice == '2':
            if current_employee.can_perform("list_employees"):
                for e in my_bank.employees: print(e)
            else:
                print("Access Denied.")
        elif choice == '3':
            if current_employee.can_perform("list_accounts"):
                if not my_bank.accounts:
                    print("No accounts loaded.")
                else:
                    for a in my_bank.accounts:
                        print(a)
            else:
                print("Access Denied.")
        elif choice == '4':
            if current_employee.can_perform("deposit_withdraw"):
                acc_num = input("Enter Account Number: ")
                target_acc = next((a for a in my_bank.accounts if a.account_number == acc_num), None)
                if target_acc and isinstance(target_acc, Assets):
                    action = input("Enter 'd' for deposit or 'w' for withdraw: ").lower()
                    amount = float(input("Enter amount: "))
                    if action == 'd':
                        target_acc.deposit(amount)
                    elif action == 'w':
                        target_acc.withdraw(amount)
                    # Syncs updated state back to CSV
                    my_bank.saveaccounts('Accounts.csv')
                    print(f"Success! New balance: ${target_acc.balance:,.2f}")
                else:
                    print("Account not found or invalid account type.")
            else:
                print("Access Denied.")
        elif choice == '6':
            break

if __name__ == "__main__":
    main()