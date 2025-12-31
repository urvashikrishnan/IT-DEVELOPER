from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secretkey"

def get_db():
    return sqlite3.connect("database.db")

# Create tables
with get_db() as conn:
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, user TEXT, task TEXT, status TEXT)")
    conn.commit()

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        if cursor.fetchone():
            session["user"] = user
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users VALUES (NULL, ?, ?)", (user, pwd))
        conn.commit()
        return redirect("/")
    return render_template("register.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        task = request.form["task"]
        cursor.execute("INSERT INTO tasks VALUES (NULL, ?, ?, 'pending')", (session["user"], task))
        conn.commit()

    cursor.execute("SELECT * FROM tasks WHERE user=?", (session["user"],))
    tasks = cursor.fetchall()
    return render_template("dashboard.html", tasks=tasks)

@app.route("/complete/<int:id>")
def complete(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status='completed' WHERE id=?", (id,))
    conn.commit()
    return redirect("/dashboard")

@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
