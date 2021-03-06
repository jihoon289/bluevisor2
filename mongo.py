import pymongo
from datetime import date, datetime, timedelta

conn = pymongo.MongoClient('mongodb+srv://bang:bang@cluster0-uiqcf.mongodb.net/test?retryWrites=true')
db = conn.get_database('bluevisor')
date = datetime.now().strftime('%Y-%m-%d')


def check_point_save(name, title):
    collection = db.get_collection('check_point')
    post = {
        "name": name,
        "title": title,
        "save_date": date
    }
    collection.update({"name": name},post,upsert=True)


def post_save(name, title, link, sdate, edate):
    collection = db.get_collection('posts')
    post = {
        "name": name,
        "title": title,
        "link": link,
        "start_date": sdate,
        "end_date": edate,
        "save_date": date
    }
    collection.insert_one(post)


def check_point_read(name):
    collection = db.get_collection('check_point')
    if collection.find_one({"name": name}) is None:
        post = {
            "name": name,
            "title": '',
            "save_date": date
        }
        collection.update({"name": name}, post, upsert=True)
    return collection.find_one({"name": name})
    # return collection.find({"date": date})


def is_saved(title):
    collection = db.get_collection('posts')
    return collection.find_one({"title": title})


def count():
    collection = db.get_collection('posts')
    return collection.find({"save_date": date}).count()


def close():
    conn.close()

