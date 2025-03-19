from flask import render_template, request, jsonify, session, redirect, url_for
from db import get_db_connection


def register_inventory_routes(app):
    @app.route('/inventory/create', methods=['GET', 'POST'])
    def inventoryCreate():
        # Connect to the database
        mydb = get_db_connection()
        my_cursor = mydb.cursor()
            # Process form data
        data = request.get_json()
            
        codeId = data.get('codeId')
        description = data.get('description')
        location = data.get('location')
        quantity = data.get('quantity')
        price = data.get('price')
        my_cursor.execute("INSERT INTO inventory (code_id, desription, location, quantity,price) VALUES (%s, %s, %s, %s,%s)", 
                            (codeId, description, location, quantity,price))
        my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", 
                            (session['username'], f"Added in Inventory with code ID: {codeId}, Description: {description}"))
        mydb.commit()
        return jsonify({"message": "inventory created successfully!"}), 200
    # Inventory route
    @app.route('/inventory', methods=['GET', 'POST'])
    def inventory():
        # Connect to the database
        mydb = get_db_connection()
        my_cursor = mydb.cursor()
        
        # Check if 'username' exists in the session
        if 'username' not in session or session['username'] == '':
            # If not logged in, redirect to the login page
            return redirect(url_for('home'))
        
        # Handle POST request (form submission)
        
        # Fetch inventory data for both GET and POST requests
        my_cursor.execute("SELECT * FROM inventory ORDER BY created_at DESC")
        logs = my_cursor.fetchall()  # Fetch all rows

        # Format the date and time for each log entry
        formatted_logs = []
        for log in logs:
            # Assuming log[5] is the datetime field (created_at)
            log_date = log[5].strftime('%Y-%m-%d')  # Date in format YYYY-MM-DD
            log_time = log[5].strftime('%I:%M:%S %p')  # Time in 12-hour format with AM/PM
            
            formatted_logs.append((log[0], log[1], log[2], log[3],log[4], log_date, log_time,log[6],log[7]))

        # Close cursor and database connection
        my_cursor.close()
        mydb.close()

        # Pass the formatted logs to the template
        return render_template('inventory.html', logs=formatted_logs, show_sidebar=True)

    @app.route('/inventory/edit', methods=['GET', 'POST'])
    def inventoryEdit():
        # Connect to the database
        mydb = get_db_connection()
        my_cursor = mydb.cursor()

        try:
            # Process form data
            data = request.get_json()

            # Extract values from the request data
            codeId = data.get('codeId')
            description = data.get('description')
            location = data.get('location')
            quantity = data.get('quantity')
            price = data.get('price')
            item_id = data['id']

            # Perform the update operation
            my_cursor.execute("""
                UPDATE inventory
                SET desription = %s, location = %s, quantity = %s, price = %s, code_id = %s
                WHERE id = %s
            """, (description, location, quantity, price, codeId, item_id))

            # Log the update to the audit log
            my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", 
                            (session['username'], f"Edited an item in Inventory with code ID: {codeId}, Description: {description}"))

            # Commit changes to the database
            mydb.commit()

            # Return a success response
            return jsonify({"message": "Inventory updated successfully!"}), 200

        except Exception as e:
            # Capture the exact error for logging and return it in the response
            mydb.rollback()
            print(f"Error occurred: {e}")  # This will print to your console
            return jsonify({"error": f"An error occurred while updating the inventory: {str(e)}"}), 500

        finally:
            # Close the database connection
            my_cursor.close()
            mydb.close()

    @app.route('/inventory/deactivation', methods=['GET', 'POST'])
    def inventoryDeactivation():
        # Connect to the database
        mydb = get_db_connection()
        my_cursor = mydb.cursor()

        try:
            # Process form data
            data = request.get_json()
            item_id = data['id']
            codeId=data['codeId']
            deactivation = 0

            # Perform the update operation
            my_cursor.execute("""
                UPDATE inventory
                SET status = %s WHERE id = %s
            """, (deactivation, item_id))

            # Log the update to the audit log
            my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", 
                            (session['username'], f"Deactivate an item in Inventory with code ID: {codeId}"))

            # Commit changes to the database
            mydb.commit()

            # Return a success response
            return jsonify({"message": "Inventory Deactivate successfully!"}), 200

        except Exception as e:
            # Capture the exact error for logging and return it in the response
            mydb.rollback()
            print(f"Error occurred: {e}")  # This will print to your console
            return jsonify({"error": f"An error occurred while updating the inventory: {str(e)}"}), 500

        finally:
            # Close the database connection
            my_cursor.close()
            mydb.close()

    @app.route('/inventory/edit/quantity', methods=['GET', 'POST'])
    def inventoryEditQuantity():
        # Connect to the database
        mydb = get_db_connection()
        my_cursor = mydb.cursor()

        try:
            # Process form data
            data = request.get_json()

            # Extract values from the request data
            description = data.get('description')
            quantity = data.get('quantity')
            item_id = data['id']

            # Perform the update operation
            my_cursor.execute("""
                UPDATE inventory
                SET desription = %s, quantity = %s WHERE id = %s
            """, (description, quantity, item_id))

            # Log the update to the audit log
            my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", 
                            (session['username'], f"Edited quantity an item in Inventory with Quantity: {quantity}, Description: {description}"))

            # Commit changes to the database
            mydb.commit()

            # Return a success response
            return jsonify({"message": "Inventory updated successfully!"}), 200

        except Exception as e:
            # Capture the exact error for logging and return it in the response
            mydb.rollback()
            print(f"Error occurred: {e}")  # This will print to your console
            return jsonify({"error": f"An error occurred while updating the inventory: {str(e)}"}), 500

        finally:
            # Close the database connection
            my_cursor.close()
            mydb.close()