import falcon
import os
from webapi import flyers, todays_menus

ENV_DB_CONNECTION = 'DB_CONNECTION'
db_conn = os.environ.get(ENV_DB_CONNECTION, None)
if not db_conn:
    raise ValueError("{} env variable must be set".format(ENV_DB_CONNECTION))

flyers_controller = flyers.Resource(db_conn)
todays_controller = todays_menus.Resource(db_conn)

api = application = falcon.API()
api.add_route('/flyers/{restaurant_id}', flyers_controller)
api.add_route('/flyers', flyers_controller)
api.add_route('/todays_menus', todays_controller)
