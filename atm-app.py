import streamlit as st
import random
import json
import os

class User:
    def __init__(self, card_number, pin, balance):
        self.card_number = card_number
        self.pin = pin
        self.balance = balance
        self.transaction_history = []

class ATM:
    def __init__(self):
        self.users = {}
        self.load_users()

    def generate_card_number(self):
        return random.randint(1000_0000_0000, 9999_9999_9999)

    def generate_pin(self):
        return random.randint(1000, 9999)

    def save_users(self):
        with open("users.json", "w") as f:
            json.dump({k: v.__dict__ for k, v in self.users.items()}, f)

    def load_users(self):
        if os.path.exists("users.json"):
            with open("users.json", "r") as f:
                users_data = json.load(f)
                for card_number, user_data in users_data.items():
                    user = User(user_data["card_number"], user_data["pin"], user_data["balance"])
                    user.transaction_history = user_data["transaction_history"]
                    self.users[int(card_number)] = user

    def register_user(self, balance):
        card_number = self.generate_card_number()
        pin = self.generate_pin()
        new_user = User(card_number, pin, balance)
        self.users[card_number] = new_user
        self.save_users()
        return card_number, pin

    def validate_user(self, card_number, pin):
        return card_number in self.users and self.users[card_number].pin == pin

    def perform_transactions(self, user):
        st.write(f"Welcome! Your current balance is {user.balance}")

        if "option" not in st.session_state:
            st.session_state.option = "Account balance"

        option = st.selectbox("Choose an option", ["Account balance", "Cash withdrawal", "Cash deposit", "PIN change", "Transaction history", "Exit"], key="option")

        if option == "Account balance":
            st.write(f"Your account balance is {user.balance}")
            user.transaction_history.append(f"Checked account balance: {user.balance}")
            self.save_users()

        elif option == "Cash withdrawal":
            withdraw_amount = st.number_input("Please enter your amount:", min_value=0, step=1, key="withdraw_amount")
            if st.button("Withdraw"):
                if withdraw_amount > user.balance:
                    st.write("Insufficient balance.")
                    user.transaction_history.append(f"Failed withdrawal attempt: {withdraw_amount} (Insufficient balance)")
                else:
                    user.balance -= withdraw_amount
                    st.write(f"{withdraw_amount} is debited from your account")
                    st.write(f"Your current balance is {user.balance}")
                    user.transaction_history.append(f"Withdraw: {withdraw_amount}")
                self.save_users()

        elif option == "Cash deposit":
            deposit_amount = st.number_input("Please enter your amount:", min_value=0, step=1, key="deposit_amount")
            if st.button("Deposit"):
                user.balance += deposit_amount
                st.write(f"{deposit_amount} is credited to your account")
                st.write(f"Your current balance is {user.balance}")
                user.transaction_history.append(f"Deposited: {deposit_amount}")
                self.save_users()

        elif option == "PIN change":
            old_pin = st.number_input("Enter your old PIN:", min_value=0, step=1, key="old_pin")
            new_pin = st.number_input("Enter your new PIN:", min_value=0, step=1, key="new_pin")
            if st.button("Change PIN"):
                if old_pin == user.pin:
                    user.pin = new_pin
                    st.write("PIN successfully changed.")
                    user.transaction_history.append("PIN changed")
                else:
                    st.write("Incorrect old PIN.")
                    user.transaction_history.append("Failed PIN change attempt due to incorrect old PIN")
                self.save_users()

        elif option == "Transaction history":
            if user.transaction_history:
                st.write("Transaction History:")
                for transaction in user.transaction_history:
                    st.write(transaction)
            else:
                st.write("No transactions yet.")

        elif option == "Exit":
            st.write("Thank you for using our ATM")
            st.session_state.logged_in_user = None
            st.stop()

def main():
    st.title("ATM Machine")
    atm = ATM()

    if "logged_in_user" not in st.session_state:
        st.session_state.logged_in_user = None

    menu = ["Register", "Login"]
    choice = st.sidebar.selectbox("Menu", menu)

    if st.session_state.logged_in_user is None:
        if choice == "Register":
            st.subheader("Register User")
            balance = st.number_input("Enter initial balance:", min_value=0, step=1, key="balance")
            if st.button("Register"):
                card_number, pin = atm.register_user(balance)
                st.success(f"User registered successfully! Your card number: {card_number}, Your PIN: {pin}")

        elif choice == "Login":
            st.subheader("User Login")
            try:
                card_number = int(st.text_input("Enter your card number:", key="card_number"))
                pin = int(st.text_input("Enter your PIN:", type="password", key="pin"))
                if st.button("Login"):
                    if atm.validate_user(card_number, pin):
                        st.success("Login successful!")
                        st.session_state.logged_in_user = atm.users[card_number]
                    else:
                        st.error("Invalid card number or PIN.")
            except ValueError:
                st.error("Invalid input. Please enter numbers only.")

    if st.session_state.logged_in_user:
        atm.perform_transactions(st.session_state.logged_in_user)

if __name__ == "__main__":
    main()
