import sqlite3
import os
import bcrypt

class Database:
    def __init__(self):
        script_dir = os.path.dirname(__file__)
        db_path = os.path.join(script_dir, '../database/smart_home.db')
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT,
                            password_hash TEXT)''')
        self.conn.commit()

    def add_user(self, username, password):
        # Hash the password before storing
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        self.conn.commit()
        
    def check_username_exists(self, username):
        self.cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        return self.cur.fetchone() is not None
    
    def authenticate_user(self, username, password):
        self.cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = self.cur.fetchone()
        if user:
            # Verify the hashed password
            if bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
                return True
        return False
