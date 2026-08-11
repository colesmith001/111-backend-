from multiprocessing.dummy import connection

from flask import Flask, jsonify, request, render_template
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



#GET http://127.0.0.1:5000/api/users

@app.get("/api/users/<int:user_id>")
def get_user_by_id(user_id):
    #logic here
    print(user_id)

    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    row =cursor.fetchone()
    

    if not row:
            connection.close()
            return jsonify({
                "success": False,
                "message": "User with ID not found"
            }), 404
    
    print(dict(row))
    user_information = dict(row)
    connection.close()


    return jsonify({
        "success": True,
        "message": f"User with ID {user_id} retrieved successfully",
        "data": user_information
    }),200


#update
@app.put("/api/users/<int:user_id>")
def update_user(user_id):

    updated_user = request.get_json()
    username = updated_user["username"]
    password = updated_user["password"]

    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        connection.close()
        return jsonify({
            "success": False,
            "message": f"User with ID {user_id} not found"
        }), 404


    cursor.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (username, password, user_id))
    connection.commit()
    connection.close()

    return jsonify({
        "success": True,
        "message": f"User with ID {user_id} updated successfully"
    }), 200

#delete 
@app.delete("/api/users/<int:user_id>")
def delete_user(user_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        connection.close()
        return jsonify ({
            "success":False,
            "message": f"User with ID {user_id} not found"
        }),404

    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    connection.commit()
    connection.close()

    return jsonify({
        "success": True,
        "message": f"User with ID {user_id} deleted successfully"
    }), 200

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

@app.get("/api/expenses")
def get_expenses():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM expenses")
    rows = cursor.fetchall()
    connection.close()

    expenses = [dict(row) for row in rows]
    return jsonify({
        "success": True,
        "message": "Expenses retrieved successfully",
        "data": expenses
    }), 200

@app.get("/api/expenses/<int:expense_id>")
def get_expense_by_id(expense_id):
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    row = cursor.fetchone()
    connection.close()

    if not row:
        return jsonify({
            "success": False,
            "message": f"Expense with ID {expense_id} not found"
        }), 404

    return jsonify({
        "success": True,
        "message": f"Expense with ID {expense_id} retrieved successfully",
        "data": dict(row)
    }), 200

@app.put("/api/expenses/<int:expense_id>")
def update_expense(expense_id):

    updated_expense = request.get_json(silent=True)
    if not updated_expense:
        return jsonify({
            "success": False,
            "message": "Request body must be valid JSON"
        }), 400

    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    row = cursor.fetchone()

    if not row:
        connection.close()
        return jsonify({
            "success": False,
            "message": f"Expense with ID {expense_id} not found"
        }), 404

    existing = dict(row)
    title = updated_expense.get("title", existing["title"])
    description = updated_expense.get("description", existing["description"])
    amount = updated_expense.get("amount", existing["amount"])
    date_expense = updated_expense.get("date", existing["date"])
    category = updated_expense.get("category", existing["category"])

    cursor.execute(
        "UPDATE expenses SET title = ?, description = ?, amount = ?, date = ?, category = ? WHERE id = ?",
        (title, description, amount, date_expense, category, expense_id)
    )
    connection.commit()
    connection.close()

    return jsonify({
        "success": True,
        "message": f"Expense with ID {expense_id} updated successfully"
    }), 200


@app.delete("/api/expenses/<int:expense_id>")
def delete_expense(expense_id):
    connection = sqlite3.connect(DB_NAME)
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM expenses WHERE id = ?", (expense_id,))
    row = cursor.fetchone()

    if not row:
        connection.close()
        return jsonify ({
            "success":False,
            "message": f"Expense with ID {expense_id} not found"
        }),404

    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    connection.commit()
    connection.close()

    return jsonify({
        "success": True,
        "message": f"Expense with ID {expense_id} deleted successfully"
    }), 200

#FRONTEND 
@app.get("/home")
def home():
    my_name = "cole"
    return render_template("home.html", name=my_name)



@app.get("/contact")
def contact():
    return render_template("contact.html")


@app.get("/about")
def about():
    return render_template("about.html")

@app.errorhandler(404) 
def page_not_found(e):
    return render_template("404.html"), 404



init_db()
app.run(debug=True)