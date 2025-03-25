from flask import render_template, request, jsonify, session, redirect, url_for
from routes.db import get_db_connection

def register_purchase_order_routes(app):
    @app.route('/purchase_order')
    def purchase_order():
        # Check if 'username' exists in the session
        if 'username' not in session or session['username'] == '':
            # If not logged in, redirect to the login page
            return redirect(url_for('home'))
        # # Query the database to get all audit logs
        # my_cursor.execute("SELECT * FROM auditLogs ORDER BY created_at DESC")
        # logs = my_cursor.fetchall()  # Fetch all rows

        # # Format the date and time for each log entry
        # formatted_logs = []
        # for log in logs:
        #     # Assuming log[3] is the datetime field (created_at)
        #     log_date = log[3].strftime('%Y-%m-%d')  # Date in format YYYY-MM-DD
        #     log_time = log[3].strftime('%I:%M:%S %p')  # Time in 12-hour format with AM/PM
            
        #     formatted_logs.append((log[0], log[1], log[2], log_date, log_time))

        # # Close cursor and database connection
        # my_cursor.close()
        # mydb.close()

        # Pass the formatted logs to the template
        # Connect to the database
        mydb = get_db_connection()
        my_cursor = mydb.cursor()

        my_cursor.execute("SELECT code_id FROM inventory ORDER BY created_at DESC")
        code_id = my_cursor.fetchall()  # Fetch all rows
                # Format the date and time for each log entry
        formatted_code_id = []
        for log in code_id:
            formatted_code_id.append((log[0]))
        # Close cursor and database connection
        my_cursor.close()
        mydb.close()
        
        return render_template('purchaseOrder.html',code_id=formatted_code_id, show_sidebar=True)