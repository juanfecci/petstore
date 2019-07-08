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

from flask import current_app
#from google.cloud import datastore
from google.appengine.ext import ndb

import datetime
import json

builtin_list = list

def init_app(app):
    pass

class Item(ndb.Model):
    itemId = ndb.IntegerProperty()
    name = ndb.StringProperty()
    price = ndb.IntegerProperty()
    quantity = ndb.IntegerProperty()
    description = ndb.StringProperty()

class Order(ndb.Model):
    userId = ndb.IntegerProperty()
    userName = ndb.StringProperty()
    orderDate = ndb.DateTimeProperty(auto_now_add=True)
    total = ndb.IntegerProperty()
    status = ndb.StringProperty()
    items = ndb.StructuredProperty(Item, repeated=True)
    paymentDetail = ndb.StringProperty()
    address = ndb.StringProperty()


def update(data, id=None):
    order = Order()
    order.userId = int(data['userId'])
    order.userName = str(data['userName'])
    order.status = str(data['status'])
    order.paymentDetail = str(data['paymentDetail'])
    order.address = str(data['address'])

    aux = []
    total = 0

    for item in data["items"]:
        itemAux = Item()
        itemAux.itemId = int(item['itemId'])
        itemAux.name = str(item['name'])
        itemAux.price = int(item['price'])
        itemAux.quantity = int(item['quantity'])
        itemAux.description = str(item['description'])

        itemAux.put()

        total += int(item["price"]) * int(item["quantity"])
        aux.append(itemAux)

    order.items = aux
    print(total)
    order.total = int(total)

    order.put()

    return returnJson(order)

create = update


def returnJson(order):
    result = dict()

    result['id'] = order.key.id()
    result['userId'] = order.userId
    result['userName'] = order.userName
    result['orderDate'] = order.orderDate.strftime("%m/%d/%Y, %H:%M:%S")
    result['status'] = order.status
    result['paymentDetail'] = order.paymentDetail
    result['address'] = order.address
    result['total'] = order.total

    result['items'] = []

    for item in order.items:
        itemAux = dict()
        itemAux['itemId'] = item.itemId
        itemAux['name'] = item.name
        itemAux['price'] = item.price
        itemAux['quantity'] = item.quantity
        itemAux['description'] = item.description

        result['items'].append(itemAux)

    return json.dumps(result)

def get(id):
    order = Order.get_by_id(int(id))
    return returnJson(order)

def listAll():
    query_iterator = Order.query().fetch()

    result = []
    for item in query_iterator:
        result.append(json.loads(returnJson(item)))

    return json.dumps(result)

def listByUser(userId):
    query_iterator = Order.query(Order.userId == int(userId)).fetch()

    result = []
    for item in query_iterator:
        result.append(json.loads(returnJson(item)))

    return json.dumps(result)

def listItems(orderId):
    order = Order.get_by_id(int(orderId))

    result = []
    for item in order.items:
        aux = {}
        aux["id"] = item.itemId
        aux['name'] = item.name
        aux["price"] = item.price
        aux["quantity"] = item.quantity
        aux["description"] = item.description
        result.append(aux)

    return json.dumps(result)

def delete(id):
    order = Order.get_by_id(int(id))
    order.key.delete()
    return 'Correct'