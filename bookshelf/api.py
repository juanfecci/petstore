
from bookshelf import get_model
from flask import Blueprint, redirect, render_template, request, url_for

api = Blueprint('api', __name__)

@api.route('/<id>', methods=['GET',])
def get(id):
    return get_model().get(id)

@api.route('/create', methods=['POST',])
def create():
    if request.method == "POST":
        content = request.get_json()
        return get_model().create(content)

@api.route('/list/all', methods=['GET',])
def listAll():
    if request.method == "GET":
        return get_model().listAll()

@api.route('/list/user/<id>', methods=['GET',])
def listByUser(id):
    return get_model().listByUser(id)

@api.route('/items/<id>', methods=['GET',])
def listItems(id):
    return get_model().listItems(id)
