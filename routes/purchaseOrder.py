from flask import render_template, request, jsonify, session, redirect, url_for
from routes.db import get_db_connection
import random
import string

def register_purchase_order_routes(app):
    @app.route('/purchase_order')
    def purchase_order():
                # Pass the formatted logs to the template
        # Connect to the database
        mydb = get_db_connection()
        my_cursor = mydb.cursor()
        # Check if 'username' exists in the session
        if 'username' not in session or session['username'] == '':
            # If not logged in, redirect to the login page
            return redirect(url_for('home'))
        # Query the database to get all audit logs
        my_cursor.execute("SELECT * FROM purchase_number ORDER BY created_at DESC")
        logs = my_cursor.fetchall()  # Fetch all rows

        # Format the date and time for each log entry
        formatted_logs = []
        for log in logs:
            # Assuming log[3] is the datetime field (created_at)
            log_date = log[3].strftime('%Y-%m-%d')  # Date in format YYYY-MM-DD
            # log_time = log[3].strftime('%I:%M:%S %p')  # Time in 12-hour format with AM/PM
            
            formatted_logs.append((log[0], log[1], log[2],log_date))

        # Close cursor and database connection
        # Fetch code_id and price from inventory
        my_cursor.execute("SELECT code_id, price,quantity FROM inventory WHERE status !=0 AND quantity != 0 ORDER BY created_at DESC")
        code_data = my_cursor.fetchall()  # Fetch all rows

        # Format the data into a dictionary
        formatted_code_id = {log[0]: {"price": log[1], "quantity": log[2]} for log in code_data}

        # Close cursor and database connection
        my_cursor.close()
        mydb.close()

        # Pass the formatted dictionary to the template
        return render_template('purchaseOrder.html', code_id=formatted_code_id,logs=formatted_logs, show_sidebar=True)
    
    @app.route('/purchaseOrder/create', methods=['GET', 'POST'])
    def createPurchaseOrder():
        mydb = get_db_connection()
        my_cursor = mydb.cursor()
        
        try:
            # Get the JSON data from the request body
            data = request.get_json()
            pricePerUnit = float(data.get('pricePerUnit', 0))  # Convert to float
            description = data.get('description')
            quantity = int(data.get('quantity', 0))  # Convert to int
            code_id = data.get('code_id')
            leftItemQuantity =int(data.get('leftItemQuantity', 0))
            print("ito yung code id",code_id)
            totalPrice = float(data.get('totalPrice', 0))  # Convert to float

            # Ensure data is valid before proceeding with the insert
            if not (pricePerUnit and description and quantity and code_id):
                return jsonify({"error": "Missing required fields!"}), 400

            # Fetch current inventory quantity
            my_cursor.execute("SELECT quantity FROM inventory WHERE code_id = %s", (code_id,))
            logs = my_cursor.fetchone()

            if logs is None:
                return jsonify({"error": "Item not found in inventory!"}), 404
            
            quantinv = logs[0]  # Extract quantity from the tuple

            # Ensure inventory has enough stock
            
            invQuantity = int(quantinv) - quantity
            print("Updated Inventory Quantity:", invQuantity)

            my_cursor.execute(
                "INSERT INTO purchase_order (item_code, Description, price_per_unit, quantity, total_price) VALUES (%s, %s, %s, %s, %s)", 
                (code_id, description, pricePerUnit, quantity, totalPrice)
            )
            
            # Fetch current inventory quantity
            # Insert a new record
            # Fetch the newly inserted ID
            my_cursor.execute("SELECT LAST_INSERT_ID()")
            new_id = my_cursor.fetchone()[0]

            print("This is the ID of the newly created item:", new_id)
            length = 15
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
            print(random_string)
            
            my_cursor.execute(
                "INSERT INTO purchase_number (purchase_order_number,purchase_order) VALUES (%s, %s)", 
                (random_string,new_id)
            )




            # Insert audit log
            my_cursor.execute(
                "INSERT INTO auditLogs (username, did) VALUES (%s, %s)", 
                (session['username'], f"Purchase Order: {description} With Item Code: {code_id}")
            )

            # Update inventory quantity
            my_cursor.execute(
                "UPDATE inventory SET quantity = %s WHERE code_id = %s",
                (invQuantity, code_id)
            )
            my_cursor.execute(
                "SELECT id FROM purchase_order WHERE item_code = %s AND Description = %s AND price_per_unit = %s AND quantity = %s AND total_price = %s",
                (code_id, description, pricePerUnit, quantity, totalPrice)
            )
            logs = my_cursor.fetchone()
            idni=logs[0]

            my_cursor.execute(
                "UPDATE purchase_order SET itemQuantity = %s WHERE id = %s",
                (invQuantity, idni)
            )
            my_cursor.execute(
                "UPDATE purchase_order SET itemQuantity = %s WHERE item_code = %s",
                (invQuantity, code_id)
            )

            mydb.commit()
            return jsonify({"message": "Purchase Order created successfully!"}), 200

        except ValueError as ve:
            print(f"ValueError: {ve}")
            return jsonify({"error": "Invalid data type!"}), 400

        except Exception as e:
            print(f"Error: {e}")
            return jsonify({"error": str(e)}), 500

        finally:
            my_cursor.close()
            mydb.close()

    @app.route('/purchaseOrder/edit', methods=['GET', 'POST'])
    def purchaseOrderEdit():
        # Connect to the database
        mydb = get_db_connection()
        my_cursor = mydb.cursor()

        try:
            data = request.get_json()
            # Extract values from the request data
            id = data.get('id')
            accountTypeButton = data.get('accountTypeButton')
            
            # Convert numeric values safely
            editItemQuantity = int(float(data.get('editItemQuantity', 0)))
            editPricePerUnit = float(data.get('editPricePerUnit', 0))
            editDescription = data.get('editDescription')
            editQuantity = int(float(data.get('editQuantity', 0)))
            EditTotalPrice = float(data.get('EditTotalPrice', 0))

            my_cursor.execute("SELECT item_code FROM purchase_order WHERE id = %s", (id,))
            logs = my_cursor.fetchone()

            if logs is None:
                return jsonify({"error": "Item not found in inventory!"}), 404
            
            purchaseOrderId = logs[0]  # Fixed typo in variable name
            
            print("this is the purchase order",purchaseOrderId)
            print("this is the accountTypeButton",accountTypeButton)
            
            if purchaseOrderId == accountTypeButton:
                # Get current values from purchase_order
                my_cursor.execute("SELECT total_price, quantity FROM purchase_order WHERE id = %s", (id,))
                logs = my_cursor.fetchone()
                
                # Convert database values to appropriate types
                total_price = float(logs[0]) if logs and logs[0] is not None else 0.0
                quantity = int(logs[1]) if logs and logs[1] is not None else 0
                
                updatedQuan = editQuantity + quantity
                updatedTotal_price = total_price + EditTotalPrice
                
                # Update purchase_order
                my_cursor.execute("""
                    UPDATE purchase_order
                    SET item_code = %s, Description = %s, itemQuantity = %s, 
                        price_per_unit = %s, quantity = %s, total_price = %s 
                    WHERE id = %s
                """, (accountTypeButton, editDescription, editItemQuantity, 
                    editPricePerUnit, editQuantity, updatedTotal_price, id))
                
                # Update inventory
                my_cursor.execute("SELECT quantity FROM inventory WHERE code_id = %s", (accountTypeButton,))
                logs = my_cursor.fetchone()
                
                if logs and logs[0] is not None:
                    invQuantity = int(float(logs[0]))
                    updateQuantityInventory = invQuantity - editQuantity
                    
                    my_cursor.execute(
                        "UPDATE inventory SET quantity = %s WHERE code_id = %s",
                        (updateQuantityInventory, accountTypeButton)
                    )

                my_cursor.execute("""
                    UPDATE purchase_order
                    SET itemQuantity = %s WHERE item_code = %s""", 
                    (updateQuantityInventory, accountTypeButton))
                
                # Log the update to the audit log
                my_cursor.execute("INSERT INTO auditLogs (username, did) VALUES (%s, %s)", 
                                (session['username'], f"Edited a Purchase Order with Item Id: {accountTypeButton}, Description: {editDescription}"))

                mydb.commit()
                return jsonify({"message": "Inventory updated successfully!"}), 200
            else:
                # Initialize these variables for the else case
                updatedTotal_price = EditTotalPrice

                my_cursor.execute("SELECT item_code,itemQuantity FROM purchase_order WHERE id = %s", (id,))
                purchase_order_logs = my_cursor.fetchone()
                item_code_logs=purchase_order_logs[0]
                itemQuantity_logs=purchase_order_logs[1]
                
                my_cursor.execute("SELECT quantity FROM inventory WHERE code_id = %s", (item_code_logs,))
                logs = my_cursor.fetchone()
                
                if logs and logs[0] is not None:
                    invQuantity = int(float(logs[0]))
                    updateQuantityInventory = invQuantity + itemQuantity_logs
                    print("this is invQuantity",invQuantity)
                    print("this is itemQuantity_logs",itemQuantity_logs)
                    print("this is the total test 2",updateQuantityInventory)
                    my_cursor.execute(
                        "UPDATE inventory SET quantity = %s WHERE code_id = %s",
                        (updateQuantityInventory, item_code_logs)
                    )
                    mydb.commit()
                    
                # Update purchase_order
                my_cursor.execute("""
                    UPDATE purchase_order
                    SET item_code = %s, Description = %s, itemQuantity = %s, 
                        price_per_unit = %s, quantity = %s, total_price = %s 
                    WHERE id = %s
                """, (accountTypeButton, editDescription, editItemQuantity, 
                    editPricePerUnit, editQuantity, updatedTotal_price, id))
                
                # Update inventory
                my_cursor.execute("SELECT quantity FROM inventory WHERE code_id = %s", (accountTypeButton,))
                logs = my_cursor.fetchone()
                
                if logs and logs[0] is not None:
                    invQuantity = int(float(logs[0]))
                    updateQuantityInventory = invQuantity - editQuantity
                    
                    my_cursor.execute(
                        "UPDATE inventory SET quantity = %s WHERE code_id = %s",
                        (updateQuantityInventory, accountTypeButton)
                    )
                    mydb.commit()
                return jsonify({"message": "Inventory updated successfully!"}), 200
        except Exception as e:
            mydb.rollback()
            print(f"Error occurred: {e}")
            return jsonify({"error": f"An error occurred while updating the inventory: {str(e)}"}), 500
        finally:
            my_cursor.close()
            mydb.close()
