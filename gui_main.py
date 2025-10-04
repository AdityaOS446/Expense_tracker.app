import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 
from fpdf import FPDF 
from db_manager import DBManager 
from tkcalendar import DateEntry

# Note: ttkthemes is imported in main.py to apply the theme to the entire app

class TrackerApp:
    def __init__(self, master):
        self.master = master
        master.title("Personal Expense Tracker")
        self.db = DBManager() 
        self.setup_ui()

    def setup_ui(self):
        # --- 1. Variables and Data Setup ---
        self.amount_var = tk.StringVar()  # Allow float input
        self.desc_var = tk.StringVar()
        self.type_var = tk.StringVar(value='Expense')
        self.category_var = tk.StringVar()
        self.date_var = tk.StringVar()
        self.edit_id = None 

        self.filter_start_var = tk.StringVar()
        self.filter_end_var = tk.StringVar()
        
        self.category_options = ['Food', 'Rent', 'Salary', 'Transport', 'Entertainment', 'Other']

        # --- 2. Input Frame (Left Panel) ---
        input_frame = ttk.Frame(self.master, padding="15")
        input_frame.pack(side=tk.LEFT, fill=tk.Y)

        ttk.Label(input_frame, text="New Transaction", font=('Arial', 14, 'bold')).pack(pady=10)

        ttk.Label(input_frame, text="Date (YYYY-MM-DD):").pack(pady=2, anchor='w')
        self.date_entry = DateEntry(input_frame, textvariable=self.date_var, date_pattern='yyyy-mm-dd', width=22)
        self.date_entry.pack(pady=2)

        # Amount Entry with float validation
        def validate_float(P):
            if P == "":
                return True
            try:
                float(P)
                return True
            except ValueError:
                return False
        vcmd = (self.master.register(validate_float), '%P')
        ttk.Label(input_frame, text="Amount:").pack(pady=2, anchor='w')
        ttk.Entry(input_frame, textvariable=self.amount_var, width=25, validate='key', validatecommand=vcmd).pack(pady=2)

        ttk.Label(input_frame, text="Description:").pack(pady=2, anchor='w')
        ttk.Entry(input_frame, textvariable=self.desc_var, width=25).pack(pady=2)

        ttk.Label(input_frame, text="Type:").pack(pady=2, anchor='w')
        type_options = ['Expense', 'Income']
        ttk.Combobox(input_frame, textvariable=self.type_var, values=type_options, width=22).pack(pady=2)

        ttk.Label(input_frame, text="Category:").pack(pady=2, anchor='w')
        ttk.Combobox(input_frame, textvariable=self.category_var, values=self.category_options, width=22).pack(pady=2)
        
        self.add_button = ttk.Button(input_frame, text="Add Transaction", command=self.add_transaction)
        self.add_button.pack(pady=15, fill=tk.X)
        
        ttk.Button(input_frame, text="Edit Selected", command=self.start_edit).pack(pady=5, fill=tk.X)
        ttk.Button(input_frame, text="Delete Selected", command=self.delete_transaction).pack(pady=5, fill=tk.X)
        
        filter_separator = ttk.Separator(input_frame, orient='horizontal')
        filter_separator.pack(fill='x', pady=10)
        
        ttk.Label(input_frame, text="Filter By Date", font=('Arial', 12, 'bold')).pack(pady=5, anchor='w')
        
        ttk.Label(input_frame, text="Start Date (YYYY-MM-DD):").pack(pady=2, anchor='w')
        self.filter_start_entry = DateEntry(input_frame, textvariable=self.filter_start_var, date_pattern='yyyy-mm-dd', width=22)
        self.filter_start_entry.pack(pady=2)
        
        ttk.Label(input_frame, text="End Date (YYYY-MM-DD):").pack(pady=2, anchor='w')
        self.filter_end_entry = DateEntry(input_frame, textvariable=self.filter_end_var, date_pattern='yyyy-mm-dd', width=22)
        self.filter_end_entry.pack(pady=2)
        
        ttk.Button(input_frame, text="Apply Filter", command=self.apply_filter).pack(pady=10, fill=tk.X)
        ttk.Button(input_frame, text="Clear Filter", command=self.load_transactions).pack(pady=2, fill=tk.X)
        
        report_separator = ttk.Separator(input_frame, orient='horizontal')
        report_separator.pack(fill='x', pady=10)
        ttk.Button(input_frame, text="View Charts & Summary", command=self.show_charts).pack(pady=5, fill=tk.X)
        ttk.Button(input_frame, text="Save Analysis as PDF", command=self.save_pdf_report).pack(pady=5, fill=tk.X)

        display_frame = ttk.Frame(self.master, padding="15")
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(display_frame, text="Transaction History", font=('Arial', 14, 'bold')).pack(pady=10)

        columns = ('id', 'date', 'type', 'category', 'amount', 'description')
        self.tree = ttk.Treeview(display_frame, columns=columns, show='headings')

        column_widths = {'id': 30, 'date': 80, 'type': 70, 'category': 90, 'amount': 80, 'description': 180}
        for col in columns:
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=column_widths[col], anchor=tk.W)
        self.tree.column('id', anchor=tk.CENTER) 

        self.tree.pack(fill=tk.BOTH, expand=True)
        self.load_transactions() 

    # ===================================================================
    # --- CORE METHODS (CRUD) ---
    # ===================================================================
    
    def load_transactions(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        transactions = self.db.fetch_all_transactions()
        for row in transactions:
            self.tree.insert('', tk.END, values=row)

    def reset_form(self):
        self.date_var.set('')
        self.amount_var.set('')
        self.desc_var.set('')
        self.type_var.set('Expense')
        self.category_var.set('')
        self.add_button.config(text="Add Transaction", command=self.add_transaction)
        self.edit_id = None 

    def add_transaction(self):
        try:
            amount = self.amount_var.get()
            desc = self.desc_var.get()
            if not all([self.date_var.get(), amount, self.type_var.get(), self.category_var.get(), desc]):
                messagebox.showerror("Input Error", "All fields are required!")
                return
            try:
                amount_val = float(amount)
            except ValueError:
                messagebox.showerror("Input Error", "Amount must be a number.")
                return
            self.db.add_transaction(
                self.date_var.get(), 
                self.type_var.get(), 
                self.category_var.get(), 
                amount_val, 
                desc
            )
            self.load_transactions() 
            self.reset_form() 
            messagebox.showinfo("Success", "Transaction recorded.")
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add transaction: {e}")
            
    def delete_transaction(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a transaction to delete.")
            return
        item_values = self.tree.item(selected_item)['values']
        transaction_id = item_values[0] 
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Transaction ID: {transaction_id}?"):
            self.db.delete_transaction(transaction_id)
            self.load_transactions() 
            messagebox.showinfo("Success", "Transaction deleted.")

    def start_edit(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a transaction to edit.")
            return
        item_values = self.tree.item(selected_item)['values']
        self.edit_id = item_values[0] 
        self.date_var.set(item_values[1])
        self.type_var.set(item_values[2])
        self.category_var.set(item_values[3])
        self.amount_var.set(str(item_values[4]))
        self.desc_var.set(item_values[5])
        self.add_button.config(text="Update Transaction", command=self.run_update)

    def run_update(self):
        try:
            if not self.edit_id:
                messagebox.showerror("Error", "No transaction selected for update.")
                return
            amount = self.amount_var.get()
            if not self.date_var.get() or not amount:
                messagebox.showerror("Input Error", "Date and Amount are required!")
                return
            try:
                amount_val = float(amount)
            except ValueError:
                messagebox.showerror("Input Error", "Amount must be a number.")
                return
            self.db.update_transaction(
                self.edit_id,
                self.date_var.get(), 
                self.type_var.get(), 
                self.category_var.get(), 
                amount_val, 
                self.desc_var.get()
            )
            self.load_transactions()
            self.reset_form()
            messagebox.showinfo("Success", f"Transaction ID {self.edit_id} updated.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update transaction: {e}")

    # ===================================================================
    # --- DATA FILTERING METHOD ---
    # ===================================================================

    def apply_filter(self):
        start_date = self.filter_start_var.get()
        end_date = self.filter_end_var.get()
        if not start_date or not end_date:
            messagebox.showwarning("Filter Error", "Please enter both a Start and End Date.")
            return
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            transactions = self.db.fetch_transactions_by_date(start_date, end_date)
            if transactions:
                for row in transactions:
                    self.tree.insert('', tk.END, values=row)
                messagebox.showinfo("Filter Success", f"Displayed {len(transactions)} transactions.")
            else:
                messagebox.showinfo("No Results", "No transactions found in the selected date range.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not apply filter. Ensure dates are YYYY-MM-DD format. Error: {e}")

    # ===================================================================
    # --- REPORTING METHODS ---
    # ===================================================================

    def calculate_summary(self, df):
        total_income = df[df['type'] == 'Income']['amount'].sum()
        total_expense = df[df['type'] == 'Expense']['amount'].sum()
        total_balance = total_income - total_expense
        return total_income, total_expense, total_balance

    def show_charts(self):
        all_transactions = self.db.fetch_all_transactions()
        if not all_transactions:
            messagebox.showinfo("No Data", "No transactions found to generate charts.")
            return
        columns = ['id', 'date', 'type', 'category', 'amount', 'description']
        df = pd.DataFrame(all_transactions, columns=columns)
        total_income, total_expense, total_balance = self.calculate_summary(df)
        expense_df = df[df['type'] == 'Expense']
        if expense_df.empty:
            messagebox.showinfo("No Expenses", "No expenses recorded to create a pie chart.")
            return
        spending_by_category = expense_df.groupby('category')['amount'].sum()
        chart_window = tk.Toplevel(self.master)
        chart_window.title("Financial Summary and Charts")
        chart_window.geometry("700x700")
        summary_label = ttk.Label(chart_window, 
                                  text=f"Total Income: {total_income:.2f} | Total Expense: {total_expense:.2f} | Net Balance: {total_balance:.2f}", 
                                  font=('Arial', 14, 'bold'))
        summary_label.pack(pady=20)
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.pie(spending_by_category, 
               labels=spending_by_category.index, 
               autopct='%1.1f%%', 
               startangle=90)
        ax.set_title('Expense Breakdown by Category', fontsize=16)
        canvas = FigureCanvasTkAgg(fig, master=chart_window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        canvas.draw()
        
    def save_pdf_report(self):
        all_transactions = self.db.fetch_all_transactions()
        if not all_transactions:
            messagebox.showinfo("No Data", "No transactions found to generate a PDF report.")
            return
        columns = ['id', 'date', 'type', 'category', 'amount', 'description']
        df = pd.DataFrame(all_transactions, columns=columns)
        total_income, total_expense, total_balance = self.calculate_summary(df)
        pdf = FPDF('P', 'mm', 'A4')
        pdf.add_page()
        pdf.set_font("Arial", size=16)
        pdf.cell(200, 10, txt="Personal Expense Tracker Report", ln=1, align="C")
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 8, txt=f"Date Generated: {pd.Timestamp('today').strftime('%Y-%m-%d')}", ln=1)
        pdf.cell(200, 8, txt=f"Total Income: {total_income:.2f}", ln=1)
        pdf.cell(200, 8, txt=f"Total Expense: {total_expense:.2f}", ln=1)
        pdf.cell(200, 8, txt=f"Net Balance: {total_balance:.2f}", ln=1)
        pdf.cell(200, 5, txt="", ln=1)
        pdf.set_font("Arial", 'B', size=10)
        col_widths = [10, 25, 20, 30, 20, 75] 
        header = ["ID", "Date", "Type", "Category", "Amount", "Description"]
        for i, h in enumerate(header):
            pdf.cell(col_widths[i], 7, h, 1, 0, 'C') 
        pdf.ln() 
        pdf.set_font("Arial", size=9)
        for row in all_transactions:
            data = [str(row[0]), row[1], row[2], row[3], f"{row[4]:.2f}", row[5]]
            for i, item in enumerate(data):
                pdf.cell(col_widths[i], 6, item, 1, 0, 'L')
            pdf.ln()
        file_name = f"Expense_Report_{pd.Timestamp('today').strftime('%Y%m%d_%H%M%S')}.pdf"
        try:
            pdf.output(file_name)
            messagebox.showinfo("Success", f"PDF report saved as:\n{file_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF. Check file permissions. Error: {e}")