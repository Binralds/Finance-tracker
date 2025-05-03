import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

def apkopot_terinus(transakcijas):
    kategoriju_izdevumi = defaultdict(float)
    for kategorija, summa, _ in transakcijas:
        kategoriju_izdevumi[kategorija] += summa

    print("\nSummary: ")
    for kategorija, summa in kategoriju_izdevumi.items():
        print(f"{kategorija}: {summa:.2f} EUR")

    if kategoriju_izdevumi:
        dominant_kategorija = max(kategoriju_izdevumi, key=kategoriju_izdevumi.get)
        print(f"\nMost money spent on: {dominant_kategorija} ({kategoriju_izdevumi[dominant_kategorija]:.2f} EUR)")
    else:
        print("\nNo data in given timestamp")

def create_transaction_table(cursor, user):
    cursor.execute(f"""CREATE TABLE IF NOT EXISTS {user}_transactions (
                        category TEXT,
                        amount REAL,
                        date INTEGER)""")

def add_transaction(cursor, user):
    try:
        category = input("Enter category >> ").strip().lower()
        if not category:
            print("❌ Category cannot be empty.")
            return

        amount_input = input("Enter amount (e.g., 6.56) >> ").strip()
        if not amount_input:
            print("❌ Amount cannot be empty.")
            return

        amount = float(amount_input)
        date = int(datetime.today().strftime('%Y%m%d'))

        create_transaction_table(cursor, user)
        cursor.execute(f"INSERT INTO {user}_transactions (category, amount, date) VALUES (?, ?, ?)",
                       (category, amount, date))
        cursor.execute(f"SELECT * FROM {user}_transactions ORDER BY rowid DESC LIMIT 1")
        latest_entry = cursor.fetchone()
        print("\nTransaction registered:")
        print(f"Category: {latest_entry[0]}, Amount: {latest_entry[1]:.2f} EUR, Date: {latest_entry[2]}")
    except ValueError:
        print("❌ Invalid amount format.")
    except Exception as e:
        print(f"❌ Error: {e}")

def review_transactions(cursor, connection, user):
    cursor.execute("SELECT review_timer FROM Users WHERE username = ?", (user,))
    result = cursor.fetchone()
    if not result:
        print("❌ No review timer set.")
        return

    timer = result[0]
    review_timer_days = timer * 30
    review_timer_now = int((datetime.now() - timedelta(days=review_timer_days)).strftime('%Y%m%d'))
    command = f"SELECT * FROM {user}_transactions WHERE date >= {review_timer_now};"
    df_transactions = pd.read_sql(command, connection)

    if not df_transactions.empty:
        df_summed = df_transactions.groupby("category", as_index=False)["amount"].sum()
        sns.barplot(data=df_summed, x="category", y="amount", errorbar=None)
        plt.title(f"{user}'s expenses")
        plt.xlabel("Category")
        plt.ylabel("Amount (EUR)")
        plt.show()

        menu3 = input("\nWould you like to see the expense summary? (Y/N): ").strip().upper()
        if menu3 == "Y":
            transactions_list = df_transactions.to_records(index=False).tolist()
            apkopot_terinus(transactions_list)
    else:
        print("No transactions found in the given period.")

def custom_period_review(cursor, connection, user):
    try:
        start_date_str = input("Enter start date (YYYYMMDD): ").strip()
        end_date_str = input("Enter end date (YYYYMMDD): ").strip()

        if not (start_date_str and end_date_str):
            print("❌ Both dates must be entered.")
            return

        start_date = int(start_date_str)
        end_date = int(end_date_str)

        if start_date > end_date:
            print("❌ Start date cannot be after end date.")
            return

        command = f"SELECT * FROM {user}_transactions WHERE date BETWEEN {start_date} AND {end_date};"
        df_transactions = pd.read_sql(command, connection)

        if not df_transactions.empty:
            df_summed = df_transactions.groupby("category", as_index=False)["amount"].sum()
            sns.barplot(data=df_summed, x="category", y="amount", errorbar=None)
            plt.title(f"{user}'s expenses from {start_date} to {end_date}")
            plt.xlabel("Category")
            plt.ylabel("Amount (EUR)")
            plt.show()

            transactions_list = df_transactions.to_records(index=False).tolist()
            apkopot_terinus(transactions_list)
        else:
            print("No transactions found for the selected period.")
    except ValueError:
        print("❌ Invalid date format. Please enter in YYYYMMDD format.")

def login_user(cursor):
    user = input("Enter your username: ").strip()
    if not user:
        print("❌ Username cannot be empty.")
        return None
    password = input("Enter your password: ").strip()
    if not password:
        print("❌ Password cannot be empty.")
        return None

    cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?", (user, password))
    if cursor.fetchone():
        print(f"Welcome, {user}!")
        return user
    else:
        print("Incorrect username or password!")
        return None

def register_user(cursor):
    user = input("Enter your username: ").strip()
    if not user:
        print("❌ Username cannot be empty.")
        return None
    cursor.execute("SELECT * FROM Users WHERE username = ?", (user,))
    if cursor.fetchone():
        print("Username already exists.")
        return None

    password = input("Enter your password: ").strip()
    if not password:
        print("❌ Password cannot be empty.")
        return None
    password2 = input("Confirm your password: ").strip()
    if password != password2:
        print("Passwords do not match!")
        return None

    try:
        timer_input = input("After how many months would you like to see a review? ").strip()
        if not timer_input:
            print("❌ Review timer cannot be empty.")
            return None
        timer = int(timer_input)
        cursor.execute("INSERT INTO Users (username, password, review_timer) VALUES (?, ?, ?)",
                       (user, password, timer))
        print("User registered successfully!")
        return user
    except ValueError:
        print("❌ Invalid input! Please enter a number for the review timer.")
        return None

def main_menu(cursor, connection, user):
    while True:
        print("\nMain Menu:")
        print("1. Add a new transaction")
        print("2. View transaction review (automatic period)")
        print("3. View transaction review (custom period)")
        print("4. Exit")
        choice = input("Choose an option (1/2/3/4): ").strip()

        if choice == "1":
            add_transaction(cursor, user)
        elif choice == "2":
            review_transactions(cursor, connection, user)
        elif choice == "3":
            custom_period_review(cursor, connection, user)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1, 2, 3, or 4.")

        connection.commit()

def main():
    connection = sqlite3.connect('userdata_test.db')
    cursor = connection.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS Users(
        username TEXT PRIMARY KEY,
        password TEXT,
        review_timer INTEGER);""")

    while True:
        registerOrLogin = input("Do you already have an account? (Y/N): ").strip().upper()
        if registerOrLogin == "Y":
            user = login_user(cursor)
            if user:
                break
        elif registerOrLogin == "N":
            user = register_user(cursor)
            if user:
                break
        else:
            print("❌ Invalid option. Please enter Y or N.")

    main_menu(cursor, connection, user)
    connection.close()

if __name__ == "__main__":
    main()
