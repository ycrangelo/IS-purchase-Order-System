from flask import Flask, render_template, session, request, jsonify, redirect, url_for
from db import get_db_connection
from users import register_user_routes
from inventory import register_inventory_routes
from dashboard import register_dashboard_routes
from auditlogs import register_auditLogs_routes  # Import the audit logs routes

app = Flask(__name__, template_folder='pages')
app.secret_key = 'your_strong_random_secret_key_here'

# Register routes from separate files
register_user_routes(app)
register_inventory_routes(app)
register_dashboard_routes(app)
register_auditLogs_routes(app)  # Register audit logs routes

# Home route
@app.route('/')
def home():
    return render_template('login.html', show_sidebar=False)

# Login route
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('name')
    password = request.form.get('password')

    mydb = get_db_connection()
    my_cursor = mydb.cursor()
    my_cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = my_cursor.fetchone()

    if user:
        session['username'] = user[3]
        session['password'] = password
        my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", (session['username'], "log in"))
        mydb.commit()
        return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', error="Invalid username or password.")

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)