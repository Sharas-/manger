import pytest
from repos.menus import *
import subprocess

DB_URL = 'localhost:9393' 

def setup_module():
    subprocess.run(['docker-compose', '-f', 'tests/startdb-docker-compose.yml', 'up', '--detach'], check=True)

def teardown_function():
    with Menus(DB_URL) as mrepo:
        mrepo.delete_all()

def test_added_menu_found():
    item = MenuItem(_id = 'delano', restaurant_name = "delano", date = '2019-05-11', menu = 'kokletai, kompotas')
    with Menus(DB_URL) as mrepo:
        mrepo.upsert(item)
        query_result = mrepo.query(item)
    expected_result = [item]
    assert query_result == expected_result

def test_menu_added_with_same_id_owerrides_exisiting_one():
    item1 = MenuItem(_id = 'delano', restaurant_name = "best restaurant", date = '2019-05-11', menu = 'kokletai, kompotas')
    item2 = MenuItem(_id = item1._id, date = '2019-11-11', restaurant_name = "other restaurant", menu = 'other menu')
    with Menus(DB_URL) as mrepo:
        mrepo.upsert(item1)
        mrepo.upsert(item2)
        query_result = mrepo.query(dict(_id = item1._id))
    expected_result = [item2]
    assert query_result == expected_result

def test_only_menus_for_date_found():
    date1 = '2019-05-11'
    date1_menus = [MenuItem(_id = 'restaurant1', restaurant_name = "best restaurant 1", date = date1, menu = 'kokletai, kompotas'),
                   MenuItem(_id = 'restaurant2', restaurant_name = "best restaurant 2", date = date1, menu = 'kokletai, kompotas'),
                   MenuItem(_id = 'restaurant3', restaurant_name = "best restaurant 3", date = date1, menu = 'kokletai, kompotas'),
                   MenuItem(_id = 'restaurant4', restaurant_name = "best restaurant 4", date = date1, menu = 'kokletai, kompotas')]
    date2 = '2012-02-12'
    date2_menus = [MenuItem(_id = 'restaurant5', restaurant_name = "best restaurant 5", date = date2, menu = 'kokletai, kompotas'),
                   MenuItem(_id = 'restaurant6', restaurant_name = "best restaurant 6", date = date2, menu = 'kokletai, kompotas'),
                   MenuItem(_id = 'restaurant7', restaurant_name = "best restaurant 7", date = date2, menu = 'kokletai, kompotas'),
                   MenuItem(_id = 'restaurant8', restaurant_name = "best restaurant 8", date = date2, menu = 'kokletai, kompotas')]

    with Menus(DB_URL) as mrepo:
        for item in date1_menus + date2_menus:
            mrepo.upsert(item)
        query_result = mrepo.query(dict(date = date1))

    def get_menuid(menuitem):
        return menuitem['_id']

    assert sorted(query_result, key=get_menuid) == sorted(date1_menus, key=get_menuid)

def test_single_menu_found_by_restaurant_name():
    name = 'restaurant at the end of the universe'
    target_item = MenuItem(restaurant_name = name, date = '9999-01-01', _id = 'restaurant0',  menu = 'barschiai, balandeliai')
    menus = [MenuItem(_id = 'restaurant1', restaurant_name = "best restaurant 1", date = '2011-03-18', menu = 'kokletai, kompotas'),
             target_item,
             MenuItem(_id = 'restaurant2', restaurant_name = "best restaurant 3", date = '2001-09-10', menu = 'silke'),
             MenuItem(_id = 'restaurant3', restaurant_name = "best restaurant 4", date = '2019-11-18', menu = 'antrikotas, pica')]
    with Menus(DB_URL) as mrepo:
        for item in menus:
            mrepo.upsert(item)
        query_result = mrepo.query(dict(restaurant_name=name))
    assert query_result == [target_item]


def teardown_module():
    subprocess.run(['docker-compose', '-f', 'tests/startdb-docker-compose.yml', 'down'])

