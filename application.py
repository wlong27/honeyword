# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request, session, flash, g
from functools import wraps
import bcrypt
import sqlite3

# create the application object
app = Flask(__name__)

index = 0
connection = sqlite3.connect(":memory:", check_same_thread=False)
cur = connection.cursor()
cur.execute('CREATE TABLE Users(userName TEXT, passwdHash TEXT, idx INTEGER)')
cur.execute('CREATE TABLE RealIndex(userName TEXT, idx INTEGER)')


#init admin account
password = "123"
hashed1 = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
hashed2 = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
hashed3 = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
index += 1
cur.execute('INSERT INTO Users VALUES("admin","{0}","{1}")'.format(hashed1.decode('utf-8'), index))
index += 1
cur.execute('INSERT INTO Users VALUES("admin","{0}","{1}")'.format(hashed2.decode('utf-8'), index))
index += 1
cur.execute('INSERT INTO Users VALUES("admin","{0}","{1}")'.format(hashed3.decode('utf-8'), index))


# config
app.secret_key = 'this is my secret key'
#app.database = "sample.db"


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
    users = {}
    username = session['username']
    if (username == 'admin'):
        cur.execute('select * from Users')
    else:
        cur.execute('select * from Users where userName = "' + username + '"')
    
    users = [dict(username=row[0], hash=row[1], idx=row[2]) for row in cur.fetchall()]
    return render_template('index.html',users=users)

# route for handling the login page logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        #Check if username and password hash exists in DB
        #g.db = connect_db()   
        username = request.form['username']
        password = request.form['password']
        cur.execute('select * from Users where userName="{0}"'.format(username))
        hashes = []
        for row in cur.fetchall():
            hashes.append(row[1])
        if (len(hashes) == 0):
            error = 'User not found or Invalid Credentials. Please try again!'
            flash('Note: Username is case-sensitive.')
        else :
            valid = bcrypt.checkpw(password.encode('utf-8'), hashes[0].encode('utf-8'))
            print(valid)
            
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
        username = request.form['username']
        cur.execute('select * from Users where userName = "' + username + '"')       
        if (len(cur.fetchall()) > 0):      
            error = "Username already exists! Please try again."
            return render_template('register.html', error=error)
        else:
            try:       
                global index
                index += 1
                cur.execute('INSERT INTO Users VALUES("{0}","{1}","{2}")'.format(request.form['username'], request.form['password'], index))
                session['logged_in'] = True
                session['username'] = request.form['username']
                return redirect(url_for('home'))  
            except Exception as e:
                error=e
    return render_template('register.html', error=error)

def connect_db():
    return sqlite3.connect(":memory:")


# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)