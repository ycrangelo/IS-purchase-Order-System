from flask import render_template, request, jsonify, session, redirect, url_for
from routes.db import get_db_connection


def register_editPurchaseOrder_routes(app):
    @app.route('/editPurchaseOrder')
    def editPurchaseOrder():

        mydb = get_db_connection()
        my_cursor = mydb.cursor()
        
        order_id = request.args.get('id')  # Retrieve the ID from URL parameters
        source = request.args.get('from_source')  # Retrieve the source from URL parameters

        query = "SELECT * FROM inventory WHERE id = %s ORDER BY created_at DESC"
        my_cursor.execute(query, (order_id,))  # Pass order_id safely as a tuple

        code_data = my_cursor.fetchall()  # Fetch all rows

        formatted_logs = []
        for log in code_data:
            # # Assuming log[3] is the datetime field (created_at)
            # log_date = log[3].strftime('%Y-%m-%d')  # Date in format YYYY-MM-DD
            # # log_time = log[3].strftime('%I:%M:%S %p')  # Time in 12-hour format with AM/PM
            
            formatted_logs.append((log[0], log[1], log[2]))

        # Close cursor and database connection
        my_cursor.close()
        mydb.close()
        # Pass the formatted logs to the template
        return render_template('editPurchaseOrder.html', code_data=code_data, order_id=order_id, show_sidebar=True,source=source)