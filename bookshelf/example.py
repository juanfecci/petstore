from bookshelf import get_model
from flask import Blueprint, redirect, render_template, request, url_for
import json


example = Blueprint('example', __name__)

cont = []

@example.route('/')
def index():
    return render_template('index.html')

@example.route('/addItem', methods=['GET', 'POST'])
def addItem():
    return render_template('add_item.html')

@example.route('/added', methods=['GET', 'POST'])
def added():
    if request.method == "POST":
        result = dict()
        details = request.form

        result["itemId"] = str(details['iid'])
        result["name"] = str(details['in'])
        result["price"] = str(details['ip'])
        result["quantity"] = str(details['in'])
        result["description"] = str(details['id'])

        cont.append(result)
        return render_template('added_item.html')
    else:   
        return render_template('index.html')

@example.route('/cancel')
def cancel():
    cont[:] = []
    return render_template('index.html')

@example.route('/succeed', methods=['GET', 'POST'])
def payment():
    #Payment().modify(mysql, cont[-2], datetime(), "Succeed")
    #Orders().modify(mysql,con[-1])
    if request.method == "POST":

        result = dict()
        result["userId"] = 2
        result["userName"] = "Prueba"
        result["status"] = "Prueba"

        result["items"] = []
        for item in cont:
            result["items"].append(item)

        result["paymentDetail"] = "Payment Detail"
        result["address"] = "Address"

        cont[:] = []

        final = get_model().create(result)
        final = json.loads(final)
        return render_template('succed.html', result = final["id"])
    else:
        return render_template('index.html')

@example.route('/viewAll', methods=['GET', 'POST'])
def viewAll():
    result = get_model().listAll()
    result = json.loads(result)
    return render_template("orders.html", result = result)

@example.route('/view', methods=['GET', 'POST'])
def view():
    if request.method == "POST":
        details = request.form
        userId = str(details['uid'])
        result = get_model().listByUser(userId)
        result = json.loads(result)
        return render_template("orders.html", result = result)
    else:
        return render_template('index.html')

@example.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == "POST":
        details = request.form
        orderId = str(details['oid'])
        result = get_model().get(orderId)
        result = json.loads(result)
        for i in range(len(result["items"])):
            result["items"][i]["total"] = int(result["items"][i]['price']) * int(result["items"][i]['quantity'])
        return render_template('order_detail.html', result = result)
    return render_template('index.html')
