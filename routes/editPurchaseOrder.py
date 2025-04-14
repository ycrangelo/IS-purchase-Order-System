from flask import render_template, request, jsonify, session, redirect, url_for
from routes.db import get_db_connection

def register_editPurchaseOrder_routes(app):
    @app.route('/editPurchaseOrder/<string:source>/<int:id>/<string:pon>/<string:date>')
    def editPurchaseOrder(source, id, pon, date):
        # Now you can use source, id, pon, and date in your function
        print(f"Source: {source}, ID: {id}, PO Number: {pon}, Date: {date}")

        # Fetch additional data from the database if needed
        mydb = get_db_connection()
        cursor = mydb.cursor(dictionary=True)
        
        # Example: Fetch purchase order details
        cursor.execute("""
            SELECT * FROM purchase_order 
            WHERE id = %s
        """, (id,))
        order = cursor.fetchall()
        print("ito oh")
        print(order)


        # Pass the data to the template
        return render_template(
            'editPurchaseOrder.html',
            source=source,  # Pass source to template
            id=id,
            po_number=pon,
            date=date,
            show_sidebar=True,
            order=order
        )