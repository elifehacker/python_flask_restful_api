#!flask/bin/python
from flask import Flask, jsonify, abort, request, make_response, url_for, render_template,redirect,flash
from flask_login import current_user, login_user, logout_user, LoginManager, UserMixin, login_required
from flask_httpauth import HTTPBasicAuth
import urllib.request, json 
from flask_sqlalchemy import SQLAlchemy
import datetime
import pandas as pd   
import yfinance as yf
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo

app = Flask(__name__, static_url_path="")
auth = HTTPBasicAuth()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///swpc.db'
db = SQLAlchemy(app)
login = LoginManager(app)
app.config['SECRET_KEY'] = 'saber'


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
    bx_gsm = db.Column(db.Float, nullable=False)
    by_gsm = db.Column(db.Float, nullable=False)
    bz_gsm = db.Column(db.Float, nullable=False)
    theta_gsm = db.Column(db.Float, nullable=False)
    theta_gse = db.Column(db.Float, nullable=False)
    phi_gsm = db.Column(db.Float, nullable=False)
    phi_gse = db.Column(db.Float, nullable=False)
    max_telemetry_flag = db.Column(db.Integer, nullable=False)
    max_data_flag = db.Column(db.Integer, nullable=False)
    overall_quality = db.Column(db.Integer, nullable=False)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class User(UserMixin):
    id = 0
    username = 'saber'
    password = 'saber'


user = User()
db.create_all()
has_data = Data.query.get(1)
if not has_data:
    print("downloading data and putting them into a sqlite database")
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
            bx_gsm = d['bx_gsm'],
            by_gsm = d['by_gsm'],
            bz_gsm = d['bz_gsm'],
            theta_gsm = d['theta_gsm'],
            theta_gse = d['theta_gse'],
            phi_gsm = d['phi_gsm'],
            phi_gse = d['phi_gse'],
            max_telemetry_flag = d['max_telemetry_flag'],
            max_data_flag = d['max_data_flag'],
            overall_quality = d['overall_quality']
        )
        db.session.add(new_data)
        db.session.commit()
else:
    print("skip downloading and processing data")


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
    return make_response(jsonify({
        'error': 'Bad request.',
        'message':'Please enter datetime in ISO format. And have datatime range between 5 min and 1 hour',
        'format': [
            'http://localhost:5000/spwx/api/v1.0/data/5minavg?end=2021-08-03T00:48:00&start=2021-08-03T00:40:00',
            'http://localhost:5000/spwx/api/v1.0/data?end=2021-08-03T00:48:00&start=2021-08-03T00:40:00',
            'http://localhost:5000/spwx/api/v1.0/data/1'
            ]
        }), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# test with 
# curl -u saber:saber -i "http://localhost:5000/spwx/api/v1.0/data/5minavg?end=2021-08-03T00:48:00&start=2021-08-03T00:40:00"
@app.route('/spwx/api/v1.0/data/5minavg', methods=['GET'])
@auth.login_required
def get_avgs():
    #print("get request")
    try:
        start = datetime.datetime.fromisoformat(request.args.get('start'))
        end = datetime.datetime.fromisoformat(request.args.get('end'))
    except Exception as e:
        abort(400)
    #print(start, end)
    delta  = end - start
    #print('delta in seconds',delta.seconds)
    if delta.seconds > 3600 or delta.seconds < 300:
        abort(400)

    sources = db.session.execute('select distinct source from data')
    result = []
    for s in sources:
        #print('sources',s[0])

        qry = db.session.query(Data).filter(
            Data.time_tag.between(start, end),
            Data.source == s[0]
            )
        q_dict = qry[0].__dict__
        q_dict.pop('_sa_instance_state')
        ks = list(q_dict.keys())
        #print('ks',ks)
        df = pd.DataFrame(columns=list(ks))
        for row in qry:
            row_dict = row.__dict__
            row_dict.pop('_sa_instance_state')
            SR_row = pd.Series(row_dict.values(), index= ks)

            df = df.append(SR_row, ignore_index=True)
            #print(row_dict)
        '''
        These are averaged
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
        '''
        #print('df head print')
        #print(df.head())
        df['bt_5min_avg'] = df['bt'].rolling(5).mean()
        df['bx_gse_5min_avg'] = df['bx_gse'].rolling(5).mean()
        df['by_gse_5min_avg'] = df['by_gse'].rolling(5).mean()
        df['bz_gse_5min_avg'] = df['bz_gse'].rolling(5).mean()
        df['theta_gse_5min_avg'] = df['theta_gse'].rolling(5).mean()
        df['phi_gse_5min_avg'] = df['phi_gse'].rolling(5).mean()
        df['bx_gsm_5min_avg'] = df['bx_gsm'].rolling(5).mean()
        df['by_gsm_5min_avg'] = df['by_gsm'].rolling(5).mean()
        df['bz_gsm_5min_avg'] = df['bz_gsm'].rolling(5).mean()
        df['theta_gsm_5min_avg'] = df['theta_gsm'].rolling(5).mean()
        df['phi_gsm_5min_avg'] = df['phi_gsm'].rolling(5).mean()
        df = df.iloc[5::5, :]
        result.append(df.to_dict())
    return jsonify({'data': [result]})

# test with
# curl -u saber:saber -i "http://localhost:5000/spwx/api/v1.0/data/5minavg?end=2021-08-03T00:48:00&start=2021-08-03T00:40:00"
@app.route('/spwx/api/v1.0/data', methods=['GET'])
@auth.login_required
def get_data():
    #print("get request")
    try:
        start = datetime.datetime.fromisoformat(request.args.get('start'))
        end = datetime.datetime.fromisoformat(request.args.get('end'))
    except Exception as e:
        abort(400)
    #print(start, end)
    delta  = end - start
    #print('delta in seconds',delta.seconds)
    if delta.seconds > 3600:
        abort(400)

    sources = db.session.execute('select distinct source from data')
    result = []
    for s in sources:
        #print('sources',s[0])

        qry = db.session.query(Data).filter(
            Data.time_tag.between(start, end),
            Data.source == s[0]
            )
        for row in qry:
            row_dict = row.__dict__
            row_dict.pop('_sa_instance_state')
            result.append(row_dict)
            #print(row_dict)
    
    return jsonify({'data': [result]})

@app.route('/spwx/api/v1.0/data/<int:data_id>', methods=['GET'])
@auth.login_required
def get_data_id(data_id):
    data = Data.query.get(data_id)
    data_dict = data.__dict__
    data_dict.pop('_sa_instance_state')
    return jsonify({'data': [data_dict]})


# test with
# http://localhost:5000/msft/5d
@app.route('/<string:tick_req>/<string:period_req>', methods=['GET'])
@login_required
def ticks(tick_req, period_req):
    tick = yf.Ticker(tick_req)
    hist = tick.history(period=period_req)
    return render_template('ticks.html', tick_data = tick.info, tick_hist = hist.to_html(), xvals = '50,60,70,90', yvals='6,7,7,9')


# test with
# curl -u saber:saber -i "http://localhost:5000/ticks/api/v1.0/msft/5d"
@app.route('/ticks/api/v1.0/<string:tick_req>/<string:period_req>', methods=['GET'])
@auth.login_required
def ticks_api(tick_req, period_req):
    tick = yf.Ticker(tick_req)
    hist = tick.history(period=period_req)
    print(hist, type(hist))
    return hist.to_json()

@login.user_loader
def load_user(id = 0):
    return user

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == user.username and form.password.data == user.password:
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

'''
https://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
https://stackoverflow.com/questions/9581692/recommended-date-format-for-rest-get-api
https://towardsdatascience.com/free-stock-data-for-python-using-yahoo-finance-api-9dafd96cad2e
'''