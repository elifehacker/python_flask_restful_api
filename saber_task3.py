#!flask/bin/python
from flask import Flask, jsonify, abort, request, make_response, url_for
from flask_httpauth import HTTPBasicAuth
import urllib.request, json 
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__, static_url_path="")
auth = HTTPBasicAuth()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///swpc.db'
db = SQLAlchemy(app)


@auth.get_password
def get_password(username):
    if username == 'saber':
        return 'saber'
    return None


@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

'''
[{
    "time_tag":"2021-08-02T06:40:00",
    "active":false,
    "source":"ACE",
    "range":null,
    "scale":4,
    "sensitivity":0.002,
    "manual_mode":false,
    "sample_size":60,
    "bt":2.97,
    "bx_gse":2.11,
    "by_gse":-1.77,
    "bz_gse":1.12,
    "theta_gse":22.17,
    "phi_gse":320.01,
    "bx_gsm":2.10,
    "by_gsm":-1.28,
    "bz_gsm":1.67,
    "theta_gsm":34.18,
    "phi_gsm":328.65,
    "max_telemetry_flag":0,
    "max_data_flag":0,
    "overall_quality":0}
'''

class Data(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    time_tag = db.Column(db.DateTime, nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    source = db.Column(db.String(10), nullable=False)
    range = db.Column(db.Integer)
    scale = db.Column(db.Integer)
    sensitivity = db.Column(db.Float)
    manual_mode = db.Column(db.Boolean, nullable=False)
    sample_size = db.Column(db.Integer, nullable=False)
    bt = db.Column(db.Float, nullable=False)
    bx_gse = db.Column(db.Float, nullable=False)
    by_gse = db.Column(db.Float, nullable=False)
    bz_gse = db.Column(db.Float, nullable=False)
    theta_gsm = db.Column(db.Float, nullable=False)
    phi_gsm = db.Column(db.Float, nullable=False)
    max_telemetry_flag = db.Column(db.Integer, nullable=False)
    max_data_flag = db.Column(db.Integer, nullable=False)
    overall_quality = db.Column(db.Integer, nullable=False)

db.create_all()

has_data = Data.query.get(1)
if not has_data:
    print("downloading data")
    data = ''
    with urllib.request.urlopen("https://services.swpc.noaa.gov/json/rtsw/rtsw_mag_1m.json") as url:
        data = json.loads(url.read().decode())
    for d in data:
        #print(d)
        new_data = Data(
            time_tag = datetime.datetime.fromisoformat(d['time_tag']), 
            active = d['active'], 
            source = d['source'],
            range = d['range'],
            scale = d['scale'],
            sensitivity = d['sensitivity'],
            manual_mode = d['manual_mode'],
            sample_size = d['sample_size'],
            bt = d['bt'],
            bx_gse = d['bx_gse'],
            by_gse = d['by_gse'],
            bz_gse = d['bz_gse'],
            theta_gsm = d['theta_gsm'],
            phi_gsm = d['phi_gsm'],
            max_telemetry_flag = d['max_telemetry_flag'],
            max_data_flag = d['max_data_flag'],
            overall_quality = d['overall_quality']
        )
        db.session.add(new_data)
        db.session.commit()
else:
    print("skip downloading data")

# test with 
# curl -u saber:saber -i "http://localhost:5000/spwx/api/v1.0/data"
@app.route('/spwx/api/v1.0/data', methods=['GET'])
@auth.login_required
def get_tasks():
    #return jsonify({'tasks': [make_public_task(task) for task in tasks]})
    print("get request")
    #print('data',data_dict)
    try:
        start = datetime.datetime.fromisoformat(request.args.get('start'))
        end = datetime.datetime.fromisoformat(request.args.get('end'))
    except Exception as e:
        abort(400)
    print(start, end)
    delta  = end - start
    print('delta in seconds',delta.seconds)
    if delta.seconds > 3600:
        abort(400)
        
    qry = db.session.query(Data).filter(Data.time_tag.between(start, end))
    result = []
    for row in qry:
        row_dict = row.__dict__
        row_dict.pop('_sa_instance_state')
        result.append(row_dict)
        print(row_dict)
    return jsonify({'data': result})

@app.route('/spwx/api/v1.0/data/<int:data_id>', methods=['GET'])
@auth.login_required
def get_task(data_id):
    data = Data.query.get(data_id)
    data_dict = data.__dict__
    data_dict.pop('_sa_instance_state')
    return jsonify({'data': [data_dict]})

if __name__ == '__main__':
    app.run(debug=True)

'''
https://stackoverflow.com/questions/9581692/recommended-date-format-for-rest-get-api
'''