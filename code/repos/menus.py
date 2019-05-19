"""
Repo for menu items
"""
import pymongo

class MenuItem(dict):
    """
    value object representing a valid menu item
    """
    def __init__(self, _id: str, restaurant_name: str, date: str, menu: str):
        vals = (val.strip() for val in [_id, restaurant_name, date, menu])
        if '' in vals:
            raise ValueError("Cannot create menu item with empty value(s)")
        self._id = _id
        self.restaurant_name = restaurant_name
        self.date = date
        self.menu = menu
        super().__init__(vars(self))

class Menus:
    """
    Persistent collection of menu items
    """

    def __init__(self, dbhost: str):
        client = pymongo.MongoClient(dbhost)
        self.menus = client.menudb.menus
        self.client = client

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()

    def upsert(self, menuitem: MenuItem):
        """
        Persists a single menu item

        Args:
            menuitem: MenuItem value object

        """
        return self.menus.replace_one(filter = dict(_id = menuitem._id), replacement = vars(menuitem), upsert=True)

    def query(self, criteria: dict) -> list:
        """
        Queries menu item store for matching items

        Args:
            kvargs: Dictionary of criteria to match

        Returns:
            list of menu items matching query criteria

        """
        return list(self.menus.find(criteria))

    def delete_all(self):
        """
        Deletes all menu entries
        """
        self.menus.delete_many({})

