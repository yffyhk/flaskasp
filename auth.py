from functools import wraps
import time

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskasp.db import get_db
from flaskasp.log import create_log

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        repassword = request.form['repassword']

        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif password != repassword:
            error = 'Password do not match'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, generate_password_hash(password))
            )
            db.commit()

            create_log("register")
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = request.form.getlist('remember')

        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']

            create_log("login")
            resp = make_response(redirect(url_for('index')))
            if not remember:
                resp.set_cookie(key='username', value='', expires=0)
                resp.set_cookie(key='password', value='', expires=0)
                return resp
            else:
                resp.set_cookie(key='username', value=username, expires=time.time()+7*60*60*24)
                resp.set_cookie(key='password', value=password, expires=time.time()+7*60*60*24)
                return resp
            
            return redirect(url_for('index'))

        flash(error)

    if request.method == 'GET':
        username = request.cookies.get('username')
        password = request.cookies.get('password')

        if username is not None and password is not None:
            return render_template('auth/login.html',username=username,password=password)

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    create_log("logout")
    session.clear()
    return redirect(url_for('index'))

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('auth.login', next=request.url))
        elif g.user['isadmin'] == 0:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
       
    return decorated_function