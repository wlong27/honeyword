# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session, flash, g
from functools import wraps
import bcrypt
import sqlite3
import honeyaux

# create the application object
app = Flask(__name__)

index = -1
connection = sqlite3.connect(":memory:", check_same_thread=False)
cur = connection.cursor()
cur.execute('CREATE TABLE Users(userName TEXT, passwdHash TEXT, idx INTEGER, TEXT word)')
cur.execute('CREATE TABLE UsersIndex(userName TEXT, idx INTEGER)')

#init admin account
password = "123"
while (index == -1):
    print('init admin')
    index = honeyaux.insert_new('admin','123', cur, index)

honeyaux.honey_checker('admin','123',cur)

# config
app.secret_key = 'this is my secret key'

# login required decorator
def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap

#Display list of user credentials. Admin can see all
@app.route('/')
@login_required
def home():
    users = {}
    username = session['username']
    if (username == 'admin'):
        cur.execute('select * from Users')
    else:
        cur.execute('select * from Users where userName = "' + username + '"')
    
    users = [dict(username=row[0], hash=row[1], idx=row[2], word=row[3]) for row in cur.fetchall()]
    return render_template('index.html',users=users)

#To check for actual password index
@app.route('/tracker')
@login_required
def tracker():
    users = {}
    username = session['username']
    if (username == 'admin'):
        cur.execute('select * from UsersIndex')
    else:
        cur.execute('select * from UsersIndex where userName = "' + username + '"')
    users = [dict(username=row[0], idx=row[1]) for row in cur.fetchall()]
    return render_template('tracker.html',users=users)
 
# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        #Check if username and password hash exists in DB
        username = request.form['username']
        password = request.form['password']
        status = honeyaux.honey_checker(username, password, cur)

        if (status == 0):
            error = 'User not found or Invalid Credentials. Please try again!'
            flash('Note: Username is case-sensitive.')
        elif (status == -1):
            error = 'Honey word detected! Suspicious login attempts.'
        else :                
            session['logged_in'] = True
            session['username'] = request.form['username']
            flash('You were logged in.')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('login'))

#Register new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        #Insert into DB the user name and password
        username = request.form['username']
        cur.execute('select * from Users where userName = "' + username + '"')       
        if (len(cur.fetchall()) > 0):      
            error = "Username already exists! Please try again."
            return render_template('register.html', error=error)
        else:
            try:       
                global index
                index = honeyaux.insert_new(request.form['username'],request.form['password'], cur, index)
                if (index == -1):
                    error = "Error inserting into DB"
                else:
                    session['logged_in'] = True
                    session['username'] = request.form['username']
                    return redirect(url_for('home'))  
            except Exception as e:
                error=e
    return render_template('register.html', error=error)


# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)