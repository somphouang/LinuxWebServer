# Initialized some fake database and tables
from tables import User, Category, Item
from core import DBSession, engine, Base, session

Base.metadata.create_all(engine)

# Cleared everything before proceeding
session.query(Category).delete()
session.query(Item).delete()
session.query(User).delete()

'''
# Create Starter Categories
category_soccer = Category('Soccer')
category_basketball = Category('Basketball')
category_baseball = Category('Baseball')
category_snowboarding = Category('Snowboarding')

# Create Starter Items
item_soccerball = Item('Soccer Ball',
    'An inflated ball used in playing a game of soccer.')
item_snowboard = Item('Snowboard', 'A board resembling a short,
    broad ski, used for sliding downhill on snow')
item_bindings = Item('Bindings',
    'Special boots which help secure both feet of a snowboarder,
    who generally rides in an upright position.')

# Put Items into few category, other categories are left item empty
category_snowboarding.items = [item_snowboard, item_bindings]
category_soccer.items = [item_soccerball]

print "Database has been initialized with some fake data!"
'''
