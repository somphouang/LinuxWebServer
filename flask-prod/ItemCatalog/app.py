import os
import sys
import google_auth_oauthlib.flow
import googleapiclient.discovery
import string

from flask import Flask, render_template, redirect, url_for, \
    request, session, flash, jsonify
from helperfunc import user_is_authorized, user_info, get_categories, \
    credentials_to_dict, login_required, get_category, add_category, \
    update_category, delete_category, get_item, add_item, update_item, \
    delete_item, get_category_set

from core import session
from tables import User, Category, Item
from flask import session as login_session

# Provisioned a Flask instance
app = Flask(__name__)

"""
Routes for Authorization with Google OAuth2 API
"""
# Allow Google GConnect
PROJECT_DIR = os.path.dirname(__file__)
CLIENT_SECRETS_FILE = os.path.join(PROJECT_DIR, 'client_secrets.json')
SCOPES = ['https://www.googleapis.com/auth/userinfo.profile']


@app.route('/login', methods=['GET'])
def login_route():
    """
    Redirects user to Google auth link
    """
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    login_session['state'] = state

    return redirect(authorization_url)


@app.route('/logout', methods=['GET'])
def logout_route():
    """
    Cleansup credentials from session and
    as result user logged out
    """
    if 'credentials' in login_session:
        del login_session['credentials']
    flash('You logged out')
    return redirect(url_for('index_route'))


@app.route('/oauth2callback')
def oauth2callback():
    """
    Handles callback call from google, and finished authorization,
    then retrieves user info and saves it into session till next login
    """
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = login_session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = request.url

    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session.
    # ACTION ITEM: In a production app, you likely want to save these
    #              credentials in a persistent database instead.
    credentials = flow.credentials
    login_session['credentials'] = credentials_to_dict(credentials)

    # requesting user info
    service = googleapiclient.discovery.build('people', 'v1',
                                              credentials=credentials)
    result = service.people().get(resourceName='people/me',
                                  personFields='names,photos').execute()

    user_id = result['resourceName']
    user_name = result['names'][0]['displayName']
    user_photo = url_for('static', filename='images/no-profile-photo.svg')
    if len(result['photos']) > 0:
        user_photo = result['photos'][0]['url']

    # saving user info to session so it remains persistent
    # this updates on login process
    login_session['user_id'] = user_id
    login_session['user_name'] = user_name
    login_session['user_photo'] = user_photo

    return redirect(url_for('index_route'))


"""
Routes
"""


@app.route('/', methods=['GET'])
def index_route():
    # Homepage for web interface
    return render_template('index.html', page={
        'title': 'Catalog Application Homepage',
        'has_sidebar': True
    }, user=user_info(), content={'categories': get_categories()})


@app.route('/profile', methods=['GET'])
def profile_route():
    # Shows user information on the page
    user = user_info()

    if not user_is_authorized():
        return redirect(url_for('login_route'))

    return render_template('profile.html', page={
        'title': user['name'] + ' profile'
    }, user=user, content={'categories': get_categories()})


"""
Routes for Categories
"""


@app.route('/categories', methods=['GET'])
def categories_route():
    """
    List of all categories
    """
    return render_template('categories.html', page={
        'title': 'Categories'
    }, user=user_info(), content={
        'categories': get_categories()
    })


@app.route('/category/add', methods=['GET', 'POST'])
@login_required
def category_add_route():
    """
    Add new category to data base
    """
    if request.method == 'POST':
        add_category()
        flash('Category added')
        return redirect(url_for('categories_route'))

    if request.method == 'GET':
        return render_template('category_edit.html', page={
            'title': 'Add category'
        }, user=user_info(), content={
            'is_edit': False
        })


@app.route('/category/<path:category_name>/edit', methods=['GET', 'POST'])
@login_required
def category_edit_route(category_name):
    """
    Updating category info
    """
    target_category = get_category(category_name)

    # checking access rights
    if target_category.owner != user_info()['id']:
        flash('Only owner can edit category')
        return redirect(url_for('categories_route'))

    if target_category is None:
        abort(404)

    if request.method == 'POST':
        update_category(category_name)
        flash('Category updated')
        return redirect(url_for('categories_route'))

    if request.method == 'GET':
        return render_template('category_edit.html', page={
            'title': 'Add category'
        }, user=user_info(), content={
            'is_edit': True,
            'category': target_category
        })


@app.route('/category/<path:category_name>/delete', methods=['GET', 'POST'])
@login_required
def category_delete_route(category_name):
    """
    Deleting category from DB
    """
    target_category = get_category(category_name)

    # checking access rights
    if target_category.owner != user_info()['id']:
        flash('Only owner can delete category')
        return redirect(url_for('categories_route'))

    if target_category is None:
        abort(404)

    if request.method == 'POST':
        delete_category(category_name)
        flash('Category deleted')
        # sending user to list of categories after all he has done
        return redirect(url_for('categories_route'))

    # as polite people we will ask some configmation first,
    # also we need it for CSRF check
    if request.method == 'GET':
        return render_template('confirm.html', page={
            'title': 'Delete category'
        }, user=user_info(), content={
            'message': 'Do you really want delete category '
            + target_category.name + '?'})


@app.route('/category/<path:category_name>', methods=['GET'])
def category_route(category_name):
    """
    Outputing category info
    """
    target_category = get_category(category_name)
    print target_category

    # ooops category not found
    if target_category is None:
        abort(404)

    return render_template('category.html', page={
        'title': 'Category ' + target_category.name,
        'has_sidebar': True
    }, user=user_info(), content={
        'categories': get_categories(),
        'category': target_category
    })


"""
Route for items
"""


@app.route('/item/<path:item_name>/edit', methods=['GET', 'POST'])
@login_required
def item_edit_route(item_name):
    """
    Route to edit item
    """
    target_item = get_item(item_name)
    # It is possible that user change the Item Name so use the previous

    # checking access rights
    if target_item.owner != user_info()['id']:
        flash('Only owner can edit item')
        return redirect(url_for('item_route', item_name=item_name))

    if target_item is None:
        flash('Item with this name does not exist')
        abort(404)

    if request.method == 'POST':
        update_item(target_item.id)
        flash('Item updated')
        # sending user to item page after edit is done
        return redirect(url_for('item_route', item_name=target_item.name))

    if request.method == 'GET':
        return render_template('item_edit.html', page={
            'title': 'Edit item'
        }, user=user_info(), content={
            'is_edit': True,
            'item': target_item
        })


@app.route('/item/<path:item_name>/delete', methods=['GET', 'POST'])
@login_required
def item_delete_route(item_name):
    """
    Route to delete item
    """
    target_item = get_item(item_name)

    # checking access rights
    if target_item.owner != user_info()['id']:
        flash('Only owner can delete item')
        return redirect(url_for('item_route', item_name=item_name))

    if target_item is None:
        abort(404)

    if request.method == 'POST':
        delete_item(item_name)
        flash('Item deleted')
        # sending user to categories page for he has done
        return redirect(url_for('categories_route'))

    if request.method == 'GET':
        return render_template('confirm.html', page={
            'title': 'Delete item'
        }, user=user_info(), content={
            'message': 'Do you really want delete item '
                       + target_item.name + '?'
        })


@app.route('/item/<path:item_name>', methods=['GET'])
def item_route(item_name):
    """
    Route that outputs item info
    """
    target_item = get_item(item_name)

    if target_item is None:
        flash('Item not found')
        # sending user to categories page for he has done
        return redirect(url_for('categories_route'))

    return render_template('item.html', page={
        'title': 'Item ' + target_item.name,
        'has_sidebar': True
    }, user=user_info(), content={
        'categories': get_categories(),
        'item': target_item
    })


@app.route('/category/<path:category_name>/add', methods=['GET', 'POST'])
@login_required
def item_add_route(category_name):
    """
    Route to add new item
    """
    target_category = get_category(category_name)

    if target_category is None:
        abort(404)

    if request.method == 'POST':

        add_item(target_category.name)
        flash('Item added')
        return redirect(url_for('category_route',
                                category_name=category_name))

    if request.method == 'GET':
        return render_template('item_edit.html', page={
            'title': 'Add category'
        }, user=user_info(), content={
            'is_edit': False,
            'category': target_category
        })


'''
JSON and API interface
'''


# Show all categories and items
@app.route('/catalog/JSON')
def allItemsJSON():
    categories = session.query(Category).all()
    category_set = [c.serialize for c in categories]
    for c in range(len(category_set)):
        items = [i.serialize for i in session.query(Item).filter_by(
            category_id=category_set[c]["id"]).all()]
        if items:
            category_set[c]["Item"] = items
    return jsonify(Category=category_set)


# All categories
@app.route('/catalog/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[c.serialize for c in categories])


# All items
@app.route('/catalog/items/JSON')
def itemsJSON():
    items = session.query(Item).all()
    return jsonify(items=[i.serialize for i in items])


# All items in a specific category
@app.route('/catalog/<path:category_name>/items/JSON')
def categoryItemsJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return jsonify(items=[i.serialize for i in items])


# Specific one item
@app.route('/catalog/<path:category_name>/<path:item_name>/JSON')
def specificItemJSON(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(
        name=item_name,
        category_id=category.id
        ).one()
    return jsonify(item=[item.serialize])


if __name__ == '__main__':
    '''
    # Placeholder to use when publish to github
        --> app.secret_key = 'PUT SECRET KEY HERE'
    '''
    app.secret_key = 'IoTXcD7rzRs9GcYcHbcDESPm'
   
    '''
    # for OAuth on http localhost
    #os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    #os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    '''

    app.run()
