# python_flask_restful_api

## task 1
This is a simple python application.

## task2
The visualization was done with dataframe and matplotlib in a python notebook

## task 3
There is below logic to facilitate the development. To download the latest data, simply remove the swpc.db file under /task345 and restart the application.
```
has_data = Data.query.get(1)
if not has_data:
    print("downloading data and putting them into a sqlite database")
    ...
 else:
    print("skip downloading and processing data")
 ```

Please use command below to test the api.
```
curl -u saber:saber -i "http://localhost:5000/spwx/api/v1.0/data/5minavg?end=2021-08-03T00:48:00&start=2021-08-03T00:40:00"
```
The data in the database was between '2021-08-02T01:42:00' and '2021-08-03T01:40:00'
```
>>> from saber_task345 import db, Data
>>> obj = db.session.query(Data).order_by(Data.id.desc()).first()
>>> obj.time_tag.isoformat()
'2021-08-02T01:42:00'
>>> obj = db.session.query(Data).order_by(Data.id).first()
>>> obj.time_tag.isoformat()
'2021-08-03T01:40:00'
```

There are also other endpoints I implemented along the way:
```
curl -u saber:saber -i "http://localhost:5000/spwx/api/v1.0/data?start=2021-08-03T00:40:00&end=2021-08-03T00:48:00"
curl -u saber:saber -i "http://localhost:5000/spwx/api/v1.0/data/1"
```

## task 4
The ticks data could be access by either visiting url such as the following. Please login with saber/saber from the home page first. 
```
# http://localhost:5000/ticks/msft/5d
```
or from an api such as the following
```
curl -u saber:saber -i "http://localhost:5000/ticks/api/v1.0/msft/5d"
```

## task 5
charts could be see in these pages
```
http://localhost:5000/ticks/msft/5d
http://localhost:5000/spwx/5minavg?end=2021-08-03T00:48:00&start=2021-08-03T00:40:00
```

