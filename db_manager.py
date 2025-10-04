import sqlite3

class DBManager:
    def __init__(self, db_name='expense_tracker.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,          -- Date the expense occurred (YYYY-MM-DD)
                type TEXT,          -- 'Income' or 'Expense'
                category TEXT,      -- e.g., 'Food', 'Rent', 'Salary'
                amount REAL,        -- Monetary value
                description TEXT
            )
        ''')
        self.conn.commit()

    def add_transaction(self, date, type, category, amount, description):
        self.cursor.execute('''
            INSERT INTO transactions (date, type, category, amount, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (date, type, category, amount, description))
        self.conn.commit()
        return "Transaction added successfully."

    def fetch_all_transactions(self):
        self.cursor.execute("SELECT * FROM transactions ORDER BY date DESC")
        return self.cursor.fetchall()

    def fetch_transactions_by_date(self, start_date, end_date):
        # SQL query to select records where the date is BETWEEN the start and end dates.
        self.cursor.execute('''
            SELECT * FROM transactions 
            WHERE date BETWEEN ? AND ? 
            ORDER BY date DESC
        ''', (start_date, end_date))
        return self.cursor.fetchall()

    def update_transaction(self, id, date, type, category, amount, description):
        self.cursor.execute('''
            UPDATE transactions 
            SET date=?, type=?, category=?, amount=?, description=?
            WHERE id=?
        ''', (date, type, category, amount, description, id))
        self.conn.commit()

    def delete_transaction(self, id):
        self.cursor.execute("DELETE FROM transactions WHERE id = ?", (id,))
        self.conn.commit()

    def __del__(self):
        self.conn.close()