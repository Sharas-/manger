import pytest
import requests
import subprocess
import urllib


HOST_URL = 'http://localhost:8080/'
FLYERS_URL = HOST_URL + 'flyers'
TODAYS_URL = HOST_URL + 'todays_menus'

def format_url_query(params: dict, url=FLYERS_URL) -> str:
    return url + '?' + urllib.parse.urlencode(params)

def setup_module():
    import time
    subprocess.run(['docker-compose', 'up', '--detach', '--build'], check=True)
    time.sleep(1) # give time for web server in the container to start

def teardown_function():
    subprocess.run(['docker-compose', 'restart', 'db'], check=True)

def test_can_list_flyers_without_authentication():
    r = requests.get(FLYERS_URL)
    assert r.status_code == 200

def test_cant_create_flyer_without_authentication():
    flyer = {'restaurant_name': 'restaurant 1', 'date': '2019-04-11', 'menu': 'kokletai, pyragas'} 
    r = requests.put(FLYERS_URL, json = flyer) 
    assert r.status_code == 401

def test_cant_create_flyer_with_partial_data():
    restaurant_auth = ('restaurant1', 'pass1') 
    partial_flyer = {'restaurant_name': 'restaurant 1', 'menu': 'kokletai, pyragas'} 
    r = requests.put(FLYERS_URL, json = partial_flyer, auth = restaurant_auth) 
    assert r.status_code == 400
    assert 'Invalid flyer' in r.json()['description']

def populate_menus(menus):
    for item in menus:
        auth, menu = item
        r = requests.put(FLYERS_URL, json = menu, auth=auth) 
        assert r.status_code == 200

def test_added_flyer_found():
    flyer = {'restaurant_name': 'best restaurant', 'date': '2019-04-11', 'menu': 'kokletai, pyragas'}
    restaurant_id = 'restaurant1'
    populate_menus([((restaurant_id, 'pass1'), flyer)])
    r = requests.get(FLYERS_URL)
    assert r.status_code == 200
    query_result = r.json()
    assert query_result == [dict(flyer, _id = restaurant_id)]

def test_all_menus_for_date_found():
    date1 = '2019-05-11'
    date2 = '2012-02-12'
    populate_menus([(('restaurant1', 'pass1'), {'restaurant_name': "best restaurant 1", 'date' : date1, 'menu' : 'kokletai, kompotas'}),
                    (('restaurant2', 'pass2'), {'restaurant_name': "best restaurant 2", 'date' : date1, 'menu' : 'kokletai, kompotas'}),
                    (('restaurant3', 'pass3'), {'restaurant_name': "best restaurant 3", 'date' : date2, 'menu' : 'geresni kokletai, kompotas'}),
                    (('restaurant4', 'pass4'), {'restaurant_name': "best restaurant 4", 'date' : date2, 'menu' : 'geresni kokletai, kompotas'}),
                    (('restaurant5', 'pass5'), {'restaurant_name': "best restaurant 5", 'date' : date2, 'menu' : 'geresni kokletai, kompotas'})])
    r = requests.get(format_url_query(dict(date=date2)))
    assert r.status_code == 200
    query_result = r.json()
    assert len(query_result) == 3
    assert all(menu['date'] == date2 for menu in query_result)

def test_todays_menus_finds_all_todays_menus():
    from datetime import date
    date1 = '2019-05-11'
    today = str(date.today())
    populate_menus([(('restaurant1', 'pass1'), {'restaurant_name': "best restaurant 1", 'date' : date1, 'menu' : 'kokletai, kompotas'}),
                    (('restaurant2', 'pass2'), {'restaurant_name': "best restaurant 2", 'date' : date1, 'menu' : 'kokletai, kompotas'}),
                    (('restaurant3', 'pass3'), {'restaurant_name': "best restaurant 3", 'date' : today, 'menu' : 'geresni kokletai, kompotas'}),
                    (('restaurant4', 'pass4'), {'restaurant_name': "best restaurant 4", 'date' : today, 'menu' : 'geresni kokletai, kompotas'}),
                    (('restaurant5', 'pass5'), {'restaurant_name': "best restaurant 5", 'date' : today, 'menu' : 'geresni kokletai, kompotas'})])
    r = requests.get(format_url_query(dict(date=today), url=TODAYS_URL))
    assert r.status_code == 200
    query_result = r.json()
    assert len(query_result) == 3
    assert all(menu['date'] == today for menu in query_result)

def teardown_module():
    subprocess.run(['docker-compose', 'down'])
