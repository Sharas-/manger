import falcon
from repos.menus import *

class Resource:
    """
    Creates responder to 'todays_menus' resource

    Args:
        db_conn: connection string to db sever
    """
    def __init__(self, db_conn: str):
        self.db_conn = db_conn

    def on_get(self, req, resp):
        from datetime import date
        today = str(date.today())
        with Menus(self.db_conn) as mrepo:
            resp.media = mrepo.query(dict(date = today))
