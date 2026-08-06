from multiprocessing.dummy import connection

from flask import Flask, jsonify, request
import sqlite3
from datetime import date


app = Flask(__name__) # Instance of Flask

DB_NAME = "budget_manager.db"

def init_db():
    connection = sqlite3.connect(DB_NAME) # Open a connection to the DB named 'budget_manager.db'
    cursor = connection.cursor() # Creates a cursor/tool that lets you send commands (SELECT,INSERT,...) to the DB

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          username TEXT UNIQUE NOT NULL,
          password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT NOT NULL,
            amount INTEGER NOT NULL,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    connection.commit() # Save changes to the DB
    connection.close() # Close the connection to the DB

# ----- USERS -----
@app.post("/api/users")
def register():
    new_user = request.get_json()
    print(new_user)

    username = new_user["username"]
    password = new_user["password"]

    connection = sqlite3.connect(DB_NAME) # Open a connection to the DB named 'budget_manager.db'
    cursor = connection.cursor() # Creates a cursor/tool that lets you send commands (SELECT,INSERT,...) to the DB
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    connection.commit() # Save the changes to the DB
    connection.close() # Close the connection

    return jsonify({
        "success": True,
        "message": "User created successfully"
    }), 201 # Created

@app.get("/api/health")
def health_check():
    return jsonify({
        "status": "OK"
    }), 200


# GET 
@app.get("/api/users")
def get_users():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row #allows column values to be retrieved by name
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    print(dict(rows))
    connection.close()


    users = []
    for row in rows:
        print(dict(row))
        users.append(dict(row))

    return jsonify ({
        "success":True,
        "message": "users retrieved succesfully",
        "data": users
    }),200

@app.post("/api/expenses")
def create_expense():
    new_expense = request.get_json()
    print(new_expense)

    title = new_expense["title"]
    description = new_expense["description"]
    amount = new_expense["amount"]
    date_expense = date.today()
    category = new_expense["category"]
    user_id = new_expense["user_id"]

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO expenses (title, description, amount, date, category, user_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, description, amount, date_expense, category, user_id))
    connection.commit()
    connection.close()

    return jsonify ({
        "success": True,
        "message": "Expense created successfully"
    }),201

init_db()
app.run(debug=True)