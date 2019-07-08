# Copyright 2015 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from flask import current_app, Flask, redirect, url_for, render_template, session, request
from flask_bootstrap import Bootstrap
import json, requests


def create_app(config, debug=False, testing=False, config_overrides=None):
    app = Flask(__name__)
    app.secret_key = 'petstoreFecci'
    Bootstrap(app)
    app.config.from_object(config)

    app.debug = debug
    app.testing = testing

    if config_overrides:
        app.config.update(config_overrides)

    # Configure logging
    if not app.testing:
        logging.basicConfig(level=logging.INFO)

    # Setup the data model.
    with app.app_context():
        model = get_model()
        model.init_app(app)

    # Register the Bookshelf CRUD blueprint.

    from .api import api
    app.register_blueprint(api, url_prefix='/api')

    from .example import example
    app.register_blueprint(example, url_prefix='/example')

    # Add a default root route.)

    @app.route("/")
    def index(error='none'):
        if 'username' in session:
            return render_template("index2.html", session=session['username'], error=error)
        return render_template("index2.html", session='', error=error)

    @app.route("/catalog/<name>")
    def catalog(name):
        path = "http://practiceiv-on-gcloud.appspot.com/products/get/specie/" + name
        headers = {'Content-Type' : 'application/json'}
        resp = json.loads(requests.get(path, headers=headers).text)

        if 'username' in session:
            return render_template("catalog.html", catalog1 = resp[name][0], catalog2 = resp[name][1:3], animals = resp[name], name=name, session=session['username'])
        return render_template("catalog.html", catalog1 = resp[name][0], catalog2 = resp[name][1:3], animals = resp[name], name=name, session='')

    @app.route("/pet/<name>/<id>")
    def pet(name, id, error='none'):
        path = "http://practiceiv-on-gcloud.appspot.com/products/get/id/" + id
        headers = {'Content-Type' : 'application/json'}
        resp = json.loads(requests.get(path, headers=headers).text)

        if 'username' in session:
            return render_template("item.html", session=session['username'], pet=resp, error=error)
        return render_template("item.html", session='', pet=resp, error=error)

    @app.route("/addPet/<id>", methods=['GET', 'POST'])
    def addPet(id):
        if request.method == 'POST':
            data = request.form.to_dict()

            path = "http://practiceiv-on-gcloud.appspot.com/products/get/id/" + id
            headers = {'Content-Type' : 'application/json'}
            resp = json.loads(requests.get(path, headers=headers).text)

            if data["amount"] != "" and data["amount"] != None:

                if int(resp['stock']) < int(data['amount']):
                    print("AAAAAAAAAAAAAAAB")
                    return pet(name=resp['specie'], id=id, error="The quantity is greater than the stock")

                path = "http://petstorecustomer.appspot.com/list/byname/" + session['username']
                headers = {'Content-Type' : 'application/json'}
                resp2 = json.loads(requests.get(path, headers=headers).text)

                path = 'http://petstorecart.appspot.com/add2cart'
                data = {'species': resp['specie'], 'breed': resp['breed'], 'amount': data["amount"],
                'phone': resp2[0]['phone'], 'name': resp2[0]['name']}
                headers = {'content-type' : 'application/json'}

                r = requests.post(path, data=json.dumps(data), headers=headers)

                return shoppingCart()

            return pet(name=resp['specie'], id=id, error="You have to add an amount")
        return shoppingCart(error="Not a POST")

    @app.route("/shoppingCart")
    def shoppingCart():
        if 'username' in session:
            path = "http://petstorecustomer.appspot.com/list/byname/" + session['username']
            headers = {'Content-Type' : 'application/json'}
            resp = json.loads(requests.get(path, headers=headers).text)

            if len(resp) == 0:
                return index()

            path = "http://petstorecart.appspot.com/list/pets/in/" + str(resp[0]["phone"])
            headers = {'Content-Type' : 'application/json'}
            resp = json.loads(requests.get(path, headers=headers).text)

            total = 0

            for i in range(len(resp)):
                path = "http://practiceiv-on-gcloud.appspot.com/products/get/breed/" + str(resp[i]["pet_breed"])
                headers = {'Content-Type' : 'application/json'}
                resp2 = json.loads(requests.get(path, headers=headers).text)

                resp[i]['price'] = resp2['price']

                total += int(resp[i]['price']) * int(resp[i]['pet_amount'])

            return render_template("shopping_cart.html", session=session['username'], cart=resp, total=total)
        return index()

    @app.route("/listOrder")
    def listOrder():
        if 'username' in session:
            path = "http://petstorecustomer.appspot.com/list/byname/" + session['username']
            headers = {'Content-Type' : 'application/json'}
            resp = json.loads(requests.get(path, headers=headers).text)

            if len(resp) == 0:
                return index()

            path = "http://order-by-fecci.appspot.com/api/list/user/" + str(resp[0]["phone"])
            headers = {'Content-Type' : 'application/json'}
            resp2 = json.loads(requests.get(path, headers=headers).text)

            total = 0

            return render_template("listOrder.html", session=session['username'], user2=resp[0], orders=resp2)
        return index()

    @app.route("/order")
    def order(error='none'):
        if 'username' in session:
            path = "http://petstorecustomer.appspot.com/list/byname/" + session['username']
            headers = {'Content-Type' : 'application/json'}
            resp = json.loads(requests.get(path, headers=headers).text)

            if len(resp) == 0:
                return index()

            path = "http://petstorecart.appspot.com/list/pets/in/" + str(resp[0]["phone"])
            headers = {'Content-Type' : 'application/json'}
            resp = json.loads(requests.get(path, headers=headers).text)

            total = 0

            for i in range(len(resp)):
                path = "http://practiceiv-on-gcloud.appspot.com/products/get/breed/" + str(resp[i]["pet_breed"])
                headers = {'Content-Type' : 'application/json'}
                resp2 = json.loads(requests.get(path, headers=headers).text)

                resp[i]['price'] = resp2['price']

                total += int(resp[i]['price']) * int(resp[i]['pet_amount'])

            return render_template("order.html", session=session['username'], cart=resp, total=total, error=error)
        return index()

    @app.route("/makeOrder", methods=['GET', 'POST'])
    def makeOrder(error='none'):
        if request.method == 'POST':

            print("AAAAAAAAAAAAAAAAA")

            data = request.form.to_dict()

            if len(data) < 1: return index()

            path = "http://petstorecustomer.appspot.com/list/byname/" + session['username']
            headers = {'Content-Type' : 'application/json'}
            resp = json.loads(requests.get(path, headers=headers).text)

            path = "http://petstorecart.appspot.com/list/pets/in/" + str(resp[0]["phone"])
            headers = {'Content-Type' : 'application/json'}
            resp2 = json.loads(requests.get(path, headers=headers).text)

            items = []

            print("AAAAAAAAAAAAAAAAA")
            for i in resp2:
                print("AAAAAAAAAAAAAAAAAb")
                path = "http://practiceiv-on-gcloud.appspot.com/products/get/breed/" + str(i["pet_breed"])
                headers = {'Content-Type' : 'application/json'}
                resp3 = json.loads(requests.get(path, headers=headers).text)

                aux = {}
                aux['itemId'] = int(float(resp3["id"]))
                aux['name'] = i["pet_breed"]
                aux['price'] = int(float(resp3["price"]))
                aux['quantity'] = int(float(i["pet_amount"]))
                aux['description'] = resp3["specie"]

                items.append(aux)

            print("AAAAAAAAAAAAAAAAA")
            print(items)
            path = 'http://order-by-fecci.appspot.com/api/create'
            data = {'userId': int(resp[0]['phone']), 'userName': resp[0]['name'], 'status': "Completed",
            'paymentDetail': data['payment'], 'address': resp[0]['address'], 'items' : items}
            headers = {'content-type' : 'application/json'}

            r = requests.post(path, data=json.dumps(data), headers=headers)
            print(r)

            path = "http://petstorecart.appspot.com/delete/cart/" + str(resp[0]["phone"])
            headers = {'Content-Type' : 'application/json'}
            resp = requests.get(path, headers=headers)

            print("AAAAAAAAAAAAAAAAA")
            for i in resp2:
                print("AAAAAAAAAAAAAAAAAb")
                path = "http://practiceiv-on-gcloud.appspot.com/products/get/breed/" + str(i["pet_breed"])
                headers = {'Content-Type' : 'application/json'}
                resp3 = json.loads(requests.get(path, headers=headers).text)

                path = "http://practiceiv-on-gcloud.appspot.com/products/update"
                data = {'breed': i["pet_breed"], 'id': int(resp3["id"]), 'price': int(resp3["price"]),
                'specie': resp3["specie"], 'stock': int(resp3["stock"]) - int(i["pet_amount"])}
                headers = {'content-type' : 'application/json'}

                print(data)

                r = requests.post(path, data=json.dumps(data), headers=headers)

            print("AAAAAAAAAAAAAAAAA")
            return render_template("complete.html", session=session['username'])

        return order("Error")

    @app.route("/removeShop/<breed>")
    def removeShop(breed):
        path = "http://petstorecustomer.appspot.com/list/byname/" + session['username']
        headers = {'Content-Type' : 'application/json'}
        resp = json.loads(requests.get(path, headers=headers).text)

        path = "http://petstorecart.appspot.com/delete/pets/bybreed/"+breed+"/in/" + str(resp[0]["phone"])
        headers = {'Content-Type' : 'application/json'}
        resp = requests.get(path, headers=headers)

        return shoppingCart()

    @app.route("/clearShop/")
    def clearShop():
        path = "http://petstorecustomer.appspot.com/list/byname/" + session['username']
        headers = {'Content-Type' : 'application/json'}
        resp = json.loads(requests.get(path, headers=headers).text)

        path = "http://petstorecart.appspot.com/delete/cart/" + str(resp[0]["phone"])
        headers = {'Content-Type' : 'application/json'}
        resp = requests.get(path, headers=headers)

        return shoppingCart()

    @app.route("/login")
    def login():
        if request.args.get("name") != None and request.args.get("phone") != None:
            path = "http://petstorecustomer.appspot.com/list/byname/" + request.args.get("name")
            headers = {'Content-Type' : 'application/json'}
            resp = json.loads(requests.get(path, headers=headers).text)

            if len(resp) == 0:
                return render_template("login.html", error="No existe ese usuario")

            if str(resp[0]["phone"]) != str(request.args.get("phone")):
                return render_template("login.html", error="Numero incorrecto")

            session['username'] = request.args.get("name")

            path = 'http://petstorecart.appspot.com/add2cart'
            data = {'phone': resp[0]["phone"], 'name': resp[0]["name"]}
            headers = {'Content-Type' : 'application/json'}

            r = requests.post(path, data=json.dumps(data), headers=headers)

            return index()

        return render_template("login.html", error="none")

    @app.route("/register")
    def register():
        if request.args.get("name") != None and request.args.get("phone") != None and request.args.get("address") != None:
            path = "http://petstorecustomer.appspot.com/create" 
            data = {'name': request.args.get("name"), 'phone': request.args.get("phone"), 'address': request.args.get("address")}
            headers = {'Content-Type' : 'application/json'}
            r = requests.post(path, data=json.dumps(data), headers=headers)

            return index(error="Account created")

        return render_template("register.html", error="none")

    @app.route("/logout")
    def logout():
        session.pop('username', None)
        return redirect(url_for('index'))

    @app.errorhandler(500)
    def server_error(e):
        return """
        An internal error occurred: <pre>{}</pre>
        See logs for full stacktrace.
        """.format(e), 500

    return app


def get_model():
    model_backend = current_app.config['DATA_BACKEND']
    if model_backend == 'cloudsql':
        from . import model_cloudsql
        model = model_cloudsql
    elif model_backend == 'datastore':
        from . import model_datastore
        model = model_datastore
    elif model_backend == 'mongodb':
        from . import model_mongodb
        model = model_mongodb
    else:
        raise ValueError(
            "No appropriate databackend configured. "
            "Please specify datastore, cloudsql, or mongodb")

    return model
