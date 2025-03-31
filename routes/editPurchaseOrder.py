from flask import render_template, request, jsonify, session, redirect, url_for
from routes.db import get_db_connection


def register_editPurchaseOrder_routes(app):
    @app.route('/editPurchaseOrder')
    def editPurchaseOrder():


        # Pass the formatted logs to the template
        return render_template('editPurchaseOrder.html', show_sidebar=True)