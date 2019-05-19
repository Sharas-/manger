import falcon
from repos.menus import *

def _read_flyer(req, restaurant_id) -> MenuItem:
    if not req.content_length:
        raise falcon.HTTPBadRequest(description="Flyer JSON expected in POST request body")
    try:
        flyer = MenuItem(_id = restaurant_id, **req.media)
    except TypeError:
        raise falcon.HTTPBadRequest(description="Invalid flyer, got: {}".format(req.media))
    except ValueError as e:
        raise falcon.HTTPBadRequest(description=str(e))
    return flyer   

class Resource:
    """
    Creates responder to 'flyers' resource

    Args:
        db_conn: connection string to db sever
    """
    def __init__(self, db_conn: str):
        self.db_conn = db_conn

    def on_get(self, req, resp):
        with Menus(self.db_conn) as mrepo:
            resp.media = mrepo.query(req.params)

    def on_put(self, req, resp, restaurant_id):
        flyer = _read_flyer(req, restaurant_id)
        with Menus(self.db_conn) as mrepo:
            try:
                mrepo.upsert(flyer)
            except ValueError as e:
                raise falcon.HTTPBadRequest(description=str(e))

