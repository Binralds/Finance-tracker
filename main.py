import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from collections import defaultdict
import os
import shutil

kivy.require('2.0.0')

class BudgetTrackerApp(App):
    def build(self):
        self.connection = sqlite3.connect('userdata_test.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS Users(
            username TEXT PRIMARY KEY,
            password TEXT);""")
        self.connection.commit()
        
        if os.path.exists('temp'):
            try:
                shutil.rmtree('temp')
            except:
                pass
                
        if not os.path.exists('temp'):
            os.makedirs('temp')
            
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.show_login_screen()
        return self.main_layout

    def show_login_screen(self):
        self.main_layout.clear_widgets()
        login_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        title_label = Label(text="Welcome to Fe!nance", font_size=24, size_hint_y=None, height=50)
        login_layout.add_widget(title_label)
        
        self.username_input = TextInput(hint_text="Enter Username", multiline=False, size_hint_y=None, height=40)
        login_layout.add_widget(self.username_input)
        
        self.password_input = TextInput(hint_text="Enter Password", password=True, multiline=False, size_hint_y=None, height=40)
        login_layout.add_widget(self.password_input)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        login_button = Button(text="Login")
        login_button.bind(on_press=self.login)
        buttons_layout.add_widget(login_button)
        
        register_button = Button(text="Register")
        register_button.bind(on_press=self.register)
        buttons_layout.add_widget(register_button)
        
        login_layout.add_widget(buttons_layout)
        self.main_layout.add_widget(login_layout)

    def login(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self.show_popup("Error", "Please enter both username and password.")
            return
            
        self.cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?", (username, password))
        if self.cursor.fetchone():
            self.show_popup("Success", f"Welcome, {username}!")
            self.user = username
            self.create_tables(username)
            self.show_main_menu()
        else:
            self.show_popup("Error", "Incorrect username or password!")

    def register(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        
        if not username or not password:
            self.show_popup("Error", "Please enter both username and password.")
            return
            
        self.cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
        if self.cursor.fetchone():
            self.show_popup("Error", "Username already exists.")
            return
            
        self.cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (username, password))
        self.connection.commit()
        self.show_popup("Success", "User registered successfully!")
        self.user = username
        self.create_tables(username)

    def create_tables(self, username):
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {username}_transactions (
                                category TEXT,
                                amount REAL,
                                date INTEGER)""")
                                
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {username}_categories (
                                category TEXT,
                                necessity TEXT)""")
                                
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {username}_budgets (
                                category TEXT,
                                budget REAL,
                                total_budget REAL)""")
        self.connection.commit()

    def show_main_menu(self):
        self.main_layout.clear_widgets()
        menu_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title_label = Label(text=f"{self.user}'s Budget Tracker", font_size=24, size_hint_y=None, height=50)
        menu_layout.add_widget(title_label)
        
        add_transaction_button = Button(text="Add Transaction", size_hint_y=None, height=60)
        add_transaction_button.bind(on_press=self.show_add_transaction)
        menu_layout.add_widget(add_transaction_button)
        
        view_transactions_button = Button(text="View Transactions", size_hint_y=None, height=60)
        view_transactions_button.bind(on_press=self.show_view_transactions)
        menu_layout.add_widget(view_transactions_button)
        
        setup_budget_button = Button(text="Setup Budget", size_hint_y=None, height=60)
        setup_budget_button.bind(on_press=self.show_setup_budget)
        menu_layout.add_widget(setup_budget_button)
        
        logout_button = Button(text="Logout", size_hint_y=None, height=60)
        logout_button.bind(on_press=lambda x: self.show_login_screen())
        menu_layout.add_widget(logout_button)
        
        self.main_layout.add_widget(menu_layout)

    def show_add_transaction(self, instance):
        self.main_layout.clear_widgets()
        transaction_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title_label = Label(text="Add Transaction", font_size=24, size_hint_y=None, height=50)
        transaction_layout.add_widget(title_label)
        
        self.category_input = TextInput(hint_text="Enter Category", multiline=False, size_hint_y=None, height=40)
        transaction_layout.add_widget(self.category_input)
        
        self.amount_input = TextInput(hint_text="Enter Amount (e.g., 6.56)", multiline=False, size_hint_y=None, height=40)
        transaction_layout.add_widget(self.amount_input)
        
        necessity_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        necessity_label = Label(text="Is this a necessity or luxury?")
        necessity_layout.add_widget(necessity_label)
        
        self.necessity_input = TextInput(hint_text="N for necessity, L for luxury", multiline=False)
        necessity_layout.add_widget(self.necessity_input)
        transaction_layout.add_widget(necessity_layout)
        
        submit_button = Button(text="Submit Transaction", size_hint_y=None, height=50)
        submit_button.bind(on_press=self.submit_transaction)
        transaction_layout.add_widget(submit_button)
        
        back_button = Button(text="Back to Main Menu", size_hint_y=None, height=50)
        back_button.bind(on_press=lambda x: self.show_main_menu())
        transaction_layout.add_widget(back_button)
        
        self.main_layout.add_widget(transaction_layout)

    def submit_transaction(self, instance):
        category = self.category_input.text.strip().lower()
        amount_text = self.amount_input.text.strip()
        necessity = self.necessity_input.text.strip().upper()
        
        if not category:
            self.show_popup("Error", "Category cannot be empty.")
            return
            
        if not amount_text:
            self.show_popup("Error", "Amount cannot be empty.")
            return
            
        try:
            amount = float(amount_text)
        except ValueError:
            self.show_popup("Error", "Invalid amount format.")
            return
            
        if necessity not in ['N', 'L']:
            self.show_popup("Error", "Necessity must be 'N' for necessity or 'L' for luxury.")
            return
            
        date = int(datetime.today().strftime('%Y%m%d'))
        
        self.cursor.execute(f"SELECT category FROM {self.user}_categories WHERE category = ?", (category,))
        if not self.cursor.fetchone():
            self.cursor.execute(f"INSERT INTO {self.user}_categories (category, necessity) VALUES (?, ?)",
                                (category, necessity))
        
        self.cursor.execute(f"INSERT INTO {self.user}_transactions (category, amount, date) VALUES (?, ?, ?)",
                            (category, amount, date))
        self.connection.commit()
        
        self.category_input.text = ""
        self.amount_input.text = ""
        self.necessity_input.text = ""
        
        current_month = int(datetime.today().strftime('%Y%m'))
        start_date = current_month * 100 + 1
        end_date = int(datetime.today().strftime('%Y%m%d'))
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        message_label = Label(
            text=f"Transaction added: {category}, {amount:.2f} EUR",
            size_hint_y=None, height=40
        )
        content.add_widget(message_label)
        
        buttons_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=40)
        close_button = Button(text="Close")
        buttons_layout.add_widget(close_button)
        
        view_button = Button(text="View Updated Report")
        buttons_layout.add_widget(view_button)
        
        content.add_widget(buttons_layout)
        
        popup = Popup(title="Success", content=content, size_hint=(0.8, 0.4))
        close_button.bind(on_press=popup.dismiss)
        view_button.bind(on_press=lambda x: self.generate_quick_report(start_date, end_date, popup))
        
        popup.open()

    def show_view_transactions(self, instance):
        self.main_layout.clear_widgets()
        view_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title_label = Label(text="View Transactions", font_size=24, size_hint_y=None, height=50)
        view_layout.add_widget(title_label)
        
        date_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=80)
        start_date_label = Label(text="Start Date (YYYYMMDD):")
        date_layout.add_widget(start_date_label)
        
        self.start_date_input = TextInput(multiline=False)
        self.start_date_input.text = datetime.today().strftime('%Y%m01')
        date_layout.add_widget(self.start_date_input)
        
        end_date_label = Label(text="End Date (YYYYMMDD):")
        date_layout.add_widget(end_date_label)
        
        self.end_date_input = TextInput(multiline=False)
        self.end_date_input.text = datetime.today().strftime('%Y%m%d')
        date_layout.add_widget(self.end_date_input)
        
        view_layout.add_widget(date_layout)
        
        submit_button = Button(text="Show Transactions", size_hint_y=None, height=50)
        submit_button.bind(on_press=self.show_transaction_report)
        view_layout.add_widget(submit_button)
        
        back_button = Button(text="Back to Main Menu", size_hint_y=None, height=50)
        back_button.bind(on_press=lambda x: self.show_main_menu())
        view_layout.add_widget(back_button)
        
        self.main_layout.add_widget(view_layout)

    def generate_quick_report(self, start_date, end_date, popup_to_dismiss=None):
        if popup_to_dismiss:
            popup_to_dismiss.dismiss()
            
        self.cursor.execute(f"SELECT COUNT(*) FROM {self.user}_transactions WHERE date BETWEEN ? AND ?",
                            (start_date, end_date))
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            self.show_popup("No Data", "No transactions found for the selected period.")
            return
            
        self.generate_report_charts(start_date, end_date)

    def show_transaction_report(self, instance):
        start_date_str = self.start_date_input.text.strip()
        end_date_str = self.end_date_input.text.strip()
        
        if not start_date_str or not end_date_str:
            self.show_popup("Error", "Please enter both start and end dates.")
            return
            
        try:
            start_date = int(start_date_str)
            end_date = int(end_date_str)
        except ValueError:
            self.show_popup("Error", "Invalid date format. Please use YYYYMMDD.")
            return
            
        if start_date > end_date:
            self.show_popup("Error", "Start date cannot be after end date.")
            return
            
        self.cursor.execute(f"SELECT COUNT(*) FROM {self.user}_transactions WHERE date BETWEEN ? AND ?",
                            (start_date, end_date))
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            self.show_popup("No Data", "No transactions found for the selected period.")
            return
            
        self.generate_report_charts(start_date, end_date)

    def generate_report_charts(self, start_date, end_date):
        try:
            for chart_file in os.listdir('temp'):
                if chart_file.startswith('transaction_'):
                    try:
                        os.remove(os.path.join('temp', chart_file))
                    except:
                        pass
            
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            bar_chart_path = f'temp/transaction_bar_{timestamp}.png'
            pie_chart_path = f'temp/transaction_pie_{timestamp}.png'
            
            command = f"SELECT * FROM {self.user}_transactions WHERE date BETWEEN {start_date} AND {end_date};"
            df_transactions = pd.read_sql(command, self.connection)
            
            if not df_transactions.empty:
                plt.figure(figsize=(10, 6))
                plt.clf()
                df_summed = df_transactions.groupby("category", as_index=False)["amount"].sum()
                sns.barplot(data=df_summed, x="category", y="amount", errorbar=None)
                plt.title(f"{self.user}'s expenses from {start_date} to {end_date}")
                plt.xlabel("Category")
                plt.ylabel("Amount (EUR)")
                plt.tight_layout()
                plt.savefig(bar_chart_path)
                plt.close()
                
                plt.figure(figsize=(10, 6))
                plt.clf()
                procents = 5
                df_summed["percent"] = (df_summed["amount"] / df_summed["amount"].sum()) * 100
                big_categories = df_summed[df_summed["percent"] >= procents]
                small_categories = df_summed[df_summed["percent"] < procents]
                
                if not small_categories.empty:
                    df_small_categories = pd.DataFrame({
                        "category": ["Other"],
                        "amount": [small_categories["amount"].sum()],
                        "percent": [small_categories["percent"].sum()]
                    })
                    df_all = pd.concat([big_categories, df_small_categories], ignore_index=True)
                else:
                    df_all = df_summed
                    
                plt.pie(df_all["amount"], labels=None, autopct='%.0f%%', pctdistance=0.8)
                plt.legend(df_all["category"], title="Categories", loc="center left", bbox_to_anchor=(1, 0.5))
                plt.tight_layout()
                plt.savefig(pie_chart_path)
                plt.close()
                
                transactions_list = df_transactions.to_records(index=False).tolist()
                summary = self.generate_transaction_summary(transactions_list)
                
                try:
                    query_luxuries = f"SELECT category FROM {self.user}_categories WHERE necessity = 'L';"
                    query_necessities = f"SELECT category FROM {self.user}_categories WHERE necessity = 'N';"
                    
                    df_luxuries = pd.read_sql(query_luxuries, self.connection)
                    df_necessities = pd.read_sql(query_necessities, self.connection)
                    
                    df_luxury_piechart = df_all.merge(df_luxuries, on="category", how="inner")
                    df_necessity_piechart = df_all.merge(df_necessities, on="category", how="inner")
                    
                    df_low_spending = df_all[df_all["percent"] < 10]
                    
                    suggestions = "Suggestions:\n"
                    
                    for _, row in df_luxury_piechart.iterrows():
                        if row["percent"] > 20:
                            suggestions += f"- You spent {row['percent']:.1f}% on '{row['category']}' (luxury). Consider reducing this.\n"
                            
                    for _, row in df_necessity_piechart.iterrows():
                        if row["percent"] < 10:
                            suggestions += f"- You spent only {row['percent']:.1f}% on '{row['category']}' (necessity). Consider allocating more funds here.\n"
                            
                    realloc_list = [row["category"] for _, row in df_low_spending.iterrows()
                                    if row["category"] not in df_necessity_piechart["category"].values]
                                    
                    if realloc_list:
                        suggestions += f"- Other possible reallocation sources (<10% spent): {', '.join(realloc_list)}.\n"
                        
                    if suggestions.strip() != "Suggestions:":
                        self.show_popup("Spending Suggestions", suggestions)
                        
                except Exception as e:
                    print(f"Error generating suggestions: {e}")
                    
                self.show_charts_popup(bar_chart_path, pie_chart_path, summary, start_date, end_date)
                
        except Exception as e:
            self.show_popup("Error", f"Failed to generate report: {str(e)}")

    def show_charts_popup(self, bar_chart_path, pie_chart_path, summary, start_date, end_date):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        title_label = Label(
            text=f"Transaction Analysis ({start_date} to {end_date})",
            font_size=18,
            size_hint_y=None,
            height=40
        )
        content.add_widget(title_label)
        
        scroll_view = ScrollView(size_hint=(1, 1))
        scroll_content = BoxLayout(orientation='vertical', padding=10, spacing=10, size_hint_y=None)
        scroll_content.bind(minimum_height=scroll_content.setter('height'))
        
        bar_chart_label = Label(text="Expenses by Category:", size_hint_y=None, height=30)
        scroll_content.add_widget(bar_chart_label)
        
        bar_chart = Image(source=bar_chart_path, size_hint_y=None, height=300)
        bar_chart.allow_stretch = True
        scroll_content.add_widget(bar_chart)
        
        pie_chart_label = Label(text="Expense Distribution:", size_hint_y=None, height=30)
        scroll_content.add_widget(pie_chart_label)
        
        pie_chart = Image(source=pie_chart_path, size_hint_y=None, height=300)
        pie_chart.allow_stretch = True
        scroll_content.add_widget(pie_chart)
        
        summary_label = Label(
            text=summary,
            size_hint_y=None,
            halign='left',
            valign='top'
        )
        summary_label.bind(texture_size=summary_label.setter('size'))
        scroll_content.add_widget(summary_label)
        
        scroll_view.add_widget(scroll_content)
        content.add_widget(scroll_view)
        
        close_button = Button(text="Close", size_hint_y=None, height=40)
        content.add_widget(close_button)
        
        popup = Popup(title="Transaction Analysis", content=content, size_hint=(0.9, 0.9))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def generate_transaction_summary(self, transactions):
        category_transactions = defaultdict(float)
        for category, amount, _ in transactions:
            category_transactions[category] += amount
            
        summary = "Summary:\n"
        for category, amount in category_transactions.items():
            summary += f"{category}: {amount:.2f} EUR\n"
            
        if category_transactions:
            dominant_category = max(category_transactions, key=category_transactions.get)
            summary += f"\nMost money spent on: {dominant_category} ({category_transactions[dominant_category]:.2f} EUR)"
            
        return summary

    def show_setup_budget(self, instance):
        try:
            command = f"SELECT DISTINCT category FROM {self.user}_transactions"
            df_categories = pd.read_sql(command, self.connection)
            categories_list = df_categories["category"].tolist()
            
            if not categories_list:
                self.show_popup("Error", "No categories found. Please add transactions first.")
                return
                
            self.main_layout.clear_widgets()
            budget_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
            
            title_label = Label(text="Setup Budget", font_size=24, size_hint_y=None, height=50)
            budget_layout.add_widget(title_label)
            
            total_budget_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            total_budget_label = Label(text="Total Budget Amount:")
            total_budget_layout.add_widget(total_budget_label)
            
            self.total_budget_input = TextInput(multiline=False)
            total_budget_layout.add_widget(self.total_budget_input)
            budget_layout.add_widget(total_budget_layout)
            
            scroll_view = ScrollView(size_hint=(1, None), size=(self.main_layout.width, 300))
            self.categories_layout = GridLayout(cols=2, spacing=10, size_hint_y=None)
            self.categories_layout.bind(minimum_height=self.categories_layout.setter('height'))
            
            self.category_budgets = {}
            
            for category in categories_list:
                category_label = Label(text=f"Budget for {category}:", size_hint_y=None, height=40)
                self.categories_layout.add_widget(category_label)
                
                category_input = TextInput(multiline=False, size_hint_y=None, height=40)
                self.categories_layout.add_widget(category_input)
                self.category_budgets[category] = category_input
                
            scroll_view.add_widget(self.categories_layout)
            budget_layout.add_widget(scroll_view)
            
            submit_button = Button(text="Save Budget", size_hint_y=None, height=50)
            submit_button.bind(on_press=self.save_budget)
            budget_layout.add_widget(submit_button)
            
            back_button = Button(text="Back to Main Menu", size_hint_y=None, height=50)
            back_button.bind(on_press=lambda x: self.show_main_menu())
            budget_layout.add_widget(back_button)
            
            self.main_layout.add_widget(budget_layout)
            
        except Exception as e:
            self.show_popup("Error", f"Failed to load categories: {e}")

    def save_budget(self, instance):
        try:
            total_budget_text = self.total_budget_input.text.strip()
            
            if not total_budget_text:
                self.show_popup("Error", "Please enter a total budget amount.")
                return
                
            try:
                total_budget = float(total_budget_text)
            except ValueError:
                self.show_popup("Error", "Invalid total budget format.")
                return
                
            self.cursor.execute(f"DELETE FROM {self.user}_budgets")
            
            self.cursor.execute(
                f"INSERT INTO {self.user}_budgets (category, budget, total_budget) VALUES (NULL, NULL, ?)",
                (total_budget,))
                
            remaining_budget = total_budget
            budget_set = False
            
            for category, input_field in self.category_budgets.items():
                budget_text = input_field.text.strip()
                
                if budget_text:
                    try:
                        budget_amount = float(budget_text)
                        
                        if budget_amount < 0:
                            self.show_popup("Error", f"Budget for {category} cannot be negative.")
                            return
                            
                        remaining_budget -= budget_amount
                        
                        if remaining_budget < 0:
                            self.show_popup("Error", f"Total budget exceeded by {abs(remaining_budget):.2f} EUR.")
                            return
                            
                        self.cursor.execute(
                            f"INSERT INTO {self.user}_budgets (category, budget, total_budget) VALUES (?, ?, NULL)",
                            (category, budget_amount))
                        budget_set = True
                        
                    except ValueError:
                        self.show_popup("Error", f"Invalid budget format for {category}.")
                        return
                        
            if not budget_set:
                self.show_popup("Error", "Please set at least one category budget.")
                return
                
            self.connection.commit()
            
            if remaining_budget > 0:
                self.show_popup("Success", f"Budget set successfully! You have {remaining_budget:.2f} EUR unallocated.")
            else:
                self.show_popup("Success", "Budget set successfully!")
                
        except Exception as e:
            self.show_popup("Error", f"Failed to save budget: {e}")

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        scroll_view = ScrollView()
        message_label = Label(text=message, size_hint_y=None)
        message_label.bind(texture_size=message_label.setter('size'))
        scroll_view.add_widget(message_label)
        content.add_widget(scroll_view)
        
        close_button = Button(text="Close", size_hint_y=None, height=40)
        content.add_widget(close_button)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.8))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def on_stop(self):
        if hasattr(self, 'connection'):
            self.connection.close()
            
        if os.path.exists('temp'):
            try:
                shutil.rmtree('temp')
            except:
                pass

if __name__ == "__main__":
    BudgetTrackerApp().run()
