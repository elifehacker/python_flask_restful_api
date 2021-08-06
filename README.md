# python_flask_restful_api

Please find screenshot of each page in the directory below for a quick look. 
```
https://github.com/elifehacker/python_flask_restful_api/tree/master/screenshots
```

## task 1
This is a simple python application.

## task 2
The visualization was done with dataframe and matplotlib in a python notebook

## task 3
To install libraries and run the app:
```
(myenv) F:\workspace\saber\task345>pip install -r requirements.txt
(myenv) F:\workspace\saber\task345>python saber_task3.py 
```
There is below logic to facilitate the development. To download the latest data, simply remove the swpc.db file under /task345 and restart the application. If you would ask what would I do to automate this process, I would use airflow to call another api in this app which triggers the download every now and then. New entries could be added to the database.
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
charts could be seen in these pages
```
http://localhost:5000/ticks/msft/5d
http://localhost:5000/spwx/5minavg?end=2021-08-03T00:48:00&start=2021-08-03T00:40:00
```

## original questions
For each task, please put them in a separate folder to keep the files easier for us at Saber to review.

Task 1 - Write a script in Python that prints the numbers from 1 to 75.
But for multiples of four print "Mission" instead of the number and for the multiples of five print "Control".
For numbers which are multiples of both four and seven print "Mission Control".

Task 2 - Data handling and basic visualisation test:
Retrieve the latest json GOES 16 proton data from services.swpc.noaa.gov
https://services.swpc.noaa.gov/json/goes/primary/differential-protons-1-day.json
Put into Pandas Dataframe
Plot a 20 minute moving average against the raw inputs for p1

Task 3 - Create a single RESTful endpoint in Flask for delivering space weather (spwx) data:
Retrieve the latest https://services.swpc.noaa.gov/json/rtsw/rtsw_mag_1m.json to form a SQLite3 table.
Have the endpoint use query strings to allow you to select a time period of up to an hour. Where the data is grouped into periods of 5 minute averages and returned via json.

Task 4 - Extend the Flask app to serve a reactive web page and REST endpoints to do the following things, you can use either basic Flask routing or a library such as Flask-RESTful:Display tick data from Yahoo Finance (or another, such as Google Finance if it requires an account) for a choice of companies for variable time ranges. Have login/logout endpoints (do not need to set up a database for this, just have a default login username/password to use) to show the functionality.

Task 5 - Write a reactive front end for the webserver. You can use your preference of framework (React, Vue.js, Angular, etc).Ability to log in and out
Display reactive plots for time periods for different Financial data
Display reactive plots for spwx data grouped in 5 minute averages
Change between light and dark mode (matched to Saber colours).
Create a CSS file to show your design idea for the front end for this page.

For reference, please take inspiration from the saberastro.com website and our websites such as tarot.saberastro.com for Saber's design language.

