from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
from flask_admin import Admin
from flask_admin.contrib.pymongo import ModelView
from flask_admin import BaseView, expose
import bcrypt

app = Flask(__name__)

admin = Admin(app, name='IronBound', template_mode='bootstrap3')

app.config['MONGO_DBNAME'] = 'lifter_db'
app.config['MONGO_URI'] = 'mongodb://admin:admin1234@ds155461.mlab.com:55461/lifter_db'

#DB Hosted on https://mlab.com/

mongo = PyMongo(app)


@app.route('/')
def index():
    users = mongo.db.users
    if 'username' in session:
        user = users.find_one({'name': str(session['username'])})
        return 'You are logged in as ' + session['username'] + '\n' + user['squat']

    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    users = mongo.db.users
    login_user = users.find_one({'name' : request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form['pass'].encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            users.insert({'name' : request.form['username'], 'password' : hashpass, 'squat' : request.form['squat'], 'bench' : request.form['bench'], 'deadlift' : request.form['deadlift']})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        
        return 'That username already exists!'

    return render_template('register.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username', None)
        return redirect(url_for('index'))

class TestView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/test.html')

admin.add_view(TestView(name='Test12'))

if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(debug=True,host='0.0.0.0')