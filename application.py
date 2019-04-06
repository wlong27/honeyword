# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session, flash, g
from functools import wraps
import sqlite3

# create the application object
app = Flask(__name__)

# config
app.secret_key = 'this is my secret key'
app.database = "sample.db"


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

# use decorators to link the function to a url
@app.route('/')
@login_required
def home():
    g.db = connect_db()
    users = {}
    username = session['username']
    if (username == 'admin'):
        cur = g.db.execute('select * from Users')
    else:
        cur = g.db.execute('select * from Users where userName = "' + username + '"')
    
    users = [dict(username=row[0], hash=row[1]) for row in cur.fetchall()]
    g.db.close()
    return render_template('index.html',users=users)

# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        #Check if username and password hash exists in DB
        g.db = connect_db()
        username = request.form['username']
        hash = request.form['password']
        cur = g.db.execute('select * from Users where userName="{0}" and passwdHash="{1}"'.format(username, hash))       
        if (len(cur.fetchall()) == 0):
            error = 'User not found or Invalid Credentials. Please try again!'
            flash('Note: Username is case-sensitive.')
        else:
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':         
        #Insert into DB the user name and password
        g.db = connect_db()
        username = request.form['username']
        cur = g.db.execute('select * from Users where userName = "' + username + '"')       
        if (len(cur.fetchall()) > 0):
            error = "Username already exists! Please try again."
            g.db.close()
            return render_template('register.html', error=error)
        else:
            cur2 = g.db.execute('INSERT INTO Users VALUES("{0}","{1}")'.format(request.form['username'], request.form['password']))
            session['logged_in'] = True
            session['username'] = request.form['username']
            flash('Succesfully registered and logged in.')
            g.db.commit()
            g.db.close()  
            return redirect(url_for('home'))
    else:
        return render_template('register.html', error=error)

def connect_db():
    return sqlite3.connect(app.database, timeout=10)

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)