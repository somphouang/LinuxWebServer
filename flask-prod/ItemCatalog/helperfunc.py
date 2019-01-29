# Helper Functions used in the application
from flask import redirect, url_for, request
from functools import wraps
from tables import Item, Category
from core import session
from flask import session as login_session
import string


def login_required(u):
    # verify user login status to protect route
    @wraps(u)
    def verify_login(*args, **kwargs):
        # if user is not logged in, redirect to login
        if user_is_authorized():
            return u(*args, **kwargs)
        else:
            return redirect(url_for('login_route'))
    return verify_login


def user_info():
    # User profile information
    user = {'authorized': False}
    if not user_is_authorized():
        return user

    user['authorized'] = True
    user['id'] = login_session['user_id']
    user['name'] = login_session['user_name']
    user['photo'] = login_session['user_photo']
    return user


def get_login_session():
    return login_session


def user_is_authorized():
    return 'credentials' in login_session


def credentials_to_dict(credentials):
    """
    Converting Google credentials into serializable object,
    so we can save it to session
    """
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def get_category_set():
    return session.query(Category).all()


"""
###############################################
CRUD
###############################################
"""


def get_categories():
    # Helper - Retrieve categories list from Database
    categories = session.query(Category).all()
    return categories


def get_category(category_name):
    """
    READ - Retrieve one category from database by name
    """
    result_category = session.query(Category).filter_by(
        name=category_name).one()
    return result_category


def add_category():
    """
    CREATE - Add new category from request form into Database
    """
    name = request.form['name']
    owner = user_info()['id']
    new_category = Category(name, owner)

    session.add(new_category)
    session.commit()


def update_category(category_name):
    """
    UPDATE - updating category from request form into Database
    """
    name = request.form['name']
    category_to_update = session.query(Category).filter_by(
        name=category_name).one()
    category_to_update.name = name

    session.add(category_to_update)
    session.commit()


def delete_category(category_name):
    """
    DELETE - Delete category from database by name
    """
    # Remove all the Items under this category first
    target_category = session.query(Category).filter_by(
        name=category_name).one()
    items_in_category_to_delete = session.query(Item).filter_by(
        category_id=target_category.id).all()

    for i in items_in_category_to_delete:
        delete_item(i.name)

    category_to_delete = session.query(Category).filter_by(
        name=category_name).delete()
    session.commit()


def get_item(item_name):
    """
    READ - Retrieve item from database by name
    """
    result_item = session.query(Item).filter_by(name=item_name).one()
    return result_item


def add_item(category_name):
    """
    CREATE - Add new item from request form into Database
    """
    category_idd = get_category(category_name)

    name = request.form['name']
    owner = user_info()['id']
    description = request.form['description']
    new_item = Item(name, description, owner)
    new_item.category_id = category_idd.id

    session.add(new_item)
    session.commit()


def update_item(item_id):
    """
    UPDATE - updating item from request form into Database using
    id because user may change the name and description of the
    item from the form
    """
    name = request.form['name']
    description = request.form['description']

    item_to_update = session.query(Item).filter_by(id=item_id).one()
    item_to_update.name = name
    item_to_update.description = description

    session.add(item_to_update)
    session.commit()


def delete_item(item_name):
    """
    DELETE - Delete item from database by name
    """
    session.query(Item).filter_by(name=item_name).delete()
    session.commit()
