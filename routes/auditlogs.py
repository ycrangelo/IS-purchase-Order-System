from flask import render_template, request, jsonify, session, redirect, url_for
from routes.db import get_db_connection

def register_auditLogs_routes(app):
    @app.route('/auditLogs')
    def auditlogs():
        # Check if 'username' exists in the session
        if 'username' not in session or session['username'] == '':
            # If not logged in, redirect to the login page
            return redirect(url_for('home'))

        # Connect to the database
        mydb = get_db_connection()
        my_cursor = mydb.cursor()

        # Query the database to get all audit logs
        my_cursor.execute("SELECT * FROM auditLogs ORDER BY created_at DESC")
        logs = my_cursor.fetchall()  # Fetch all rows

        # Format the date and time for each log entry
        formatted_logs = []
        for log in logs:
            # Assuming log[3] is the datetime field (created_at)
            log_date = log[3].strftime('%Y-%m-%d')  # Date in format YYYY-MM-DD
            log_time = log[3].strftime('%I:%M:%S %p')  # Time in 12-hour format with AM/PM
            
            formatted_logs.append((log[0], log[1], log[2], log_date, log_time))

        # Close cursor and database connection
        my_cursor.close()
        mydb.close()

        # Pass the formatted logs to the template
        return render_template('auditlogs.html', logs=formatted_logs, show_sidebar=True)