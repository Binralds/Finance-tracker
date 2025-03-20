import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict


def apkopot_terinus(transakcijas):

    kategoriju_izdevumi = defaultdict(float)

    for kategorija, summa, _ in transakcijas:
        kategoriju_izdevumi[kategorija] += summa

    print("\nSummary: ")
    for kategorija, summa in kategoriju_izdevumi.items():
        print(f"{kategorija}: {summa:.2f} EUR")

    if kategoriju_izdevumi:
        dominantā_kategorija = max(kategoriju_izdevumi, key=kategoriju_izdevumi.get)
        print(
            f"\n Most money spent on :  {dominantā_kategorija} ({kategoriju_izdevumi[dominantā_kategorija]:.2f} EUR)")
    else:
        print("\nNo data in given timestamp")

#connects do database
connection = sqlite3.connect('userdata_test.db')
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS Users(
    username TEXT PRIMARY KEY,
    password TEXT,
    review_timer INTEGER);""")
# registeration/login
registerOrLogin = input("Do you already have an account? (Y/N):").strip().upper()

while True:
    if registerOrLogin == "Y":
        user = input("Enter your username:").strip()
        password = input("Enter your password:").strip()
        cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?", (user, password))
        if cursor.fetchone():
            print(f"Welcome, {user}!")
        else:
            print("Incorrect username or password!")
            exit()
    else:
        user = input("Enter your username: ").strip()
        cursor.execute("SELECT * FROM Users WHERE username = ?", (user,))
        if cursor.fetchone():
            print("Username already exists.")
        else:
            password = input("Enter your password: ").strip()
            password2 = input("Confirm your password: ").strip()

            if password != password2:
                print("Passwords do not match!")
            else:
                try:
                    timer = int(input("After how many months would you like to see a review? ").strip())

                    cursor.execute("INSERT INTO Users (username, password, review_timer) VALUES (?, ?, ?)",
                                   (user, password, timer))

                    print("User registered successfully!")
                except ValueError:
                    print("Invalid input! Please enter a number for the review timer.")
                    exit()


#registering a new data entry
    menu = input("Would you like to save a new transaction? (Y/N):").strip().upper()

    if menu == "Y":
        category = input("Please enter the corresponding category >> ").strip()
        amount = float(input("Please enter the amount spent (e.g., 6.56) >> ").strip())
        date = int(datetime.today().strftime('%Y%m%d'))

        cursor.execute(f"""CREATE TABLE IF NOT EXISTS {user}_transactions (
                        category TEXT,
                        amount REAL,
                        date INTEGER)""")

        cursor.execute(f"INSERT INTO {user}_transactions (category, amount, date) VALUES (?, ?, ?)",
                       (category, amount, date))
        connection.commit()

        cursor.execute(f"SELECT * FROM {user}_transactions ORDER BY rowid DESC LIMIT 1")
        latest_entry = cursor.fetchone()

        if latest_entry:
            print("Transaction successfully registered:")
            print(f"Category: {latest_entry[0]}, Amount: {latest_entry[1]:.2f} EUR, Date: {latest_entry[2]}")

# table data review in the form of a graph and a string
    else:
        menu2 = input("Do you wish to see transaction review? (Y/N):").strip().upper()

        if menu2 == "Y":
            cursor.execute("SELECT review_timer FROM Users WHERE username = ?", (user,))
            result = cursor.fetchone()
            timer = result[0]

            review_timer_days = timer * 30
            review_timer_now = int((datetime.now() - timedelta(days=review_timer_days)).strftime('%Y%m%d'))
            command = f"SELECT * FROM {user}_transactions WHERE date >= {review_timer_now};"
            df_transactions = pd.read_sql(command, connection)

            if not df_transactions.empty:
                df_summed = df_transactions.groupby("category", as_index=False)["amount"].sum()
                sns.barplot(data=df_summed, x="category", y="amount", errorbar=None)

                plt.title(f" {user}'s expenses")
                plt.xlabel("Category")
                plt.ylabel("Amount (EUR)")
                plt.show()
            else:
                print("No transactions found in the given period.")

            # ✅ Pievienota jauna izvēle pēc Transaction Review
            menu3 = input("\nWould you like to see the expense summary? (Y/N):").strip().upper()

            if menu3 == "Y" and not df_transactions.empty:
                transactions_list = df_transactions.to_records(index=False).tolist()
                apkopot_terinus(transactions_list)
            else:
                print("An error ocurred, if permanent, please contact the developers")

    connection.commit()
    connection.close()
    break
