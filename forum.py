from flaskasp.db import get_db
from flaskasp.auth import login_required
from flaskasp.log import create_log

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
)

bp = Blueprint('forum', __name__, url_prefix='/forum')

@bp.route('', methods=('GET',))
def index():
    db = get_db()
    posts = db.execute('SELECT post.id, user.username, created, topic, body'
                       ' FROM post' 
                       ' LEFT JOIN user ON post.user_id = user.id'
                       ' ORDER BY created DESC').fetchall()


    return render_template('forum/index.html',posts=posts)

@bp.route('/post/<id>', methods=('GET',))
def post(id):
    
    db = get_db()

    post = db.execute('SELECT post.id, post.user_id, user.username, created, topic, body'
                      ' FROM post' 
                      ' LEFT JOIN user ON post.user_id = user.id'
                      ' WHERE post.id = ?',(id,)).fetchone()

    replys = db.execute('SELECT reply.id, reply.user_id, user.username, created, body'
                      ' FROM reply' 
                      ' LEFT JOIN user ON reply.user_id = user.id'
                      ' WHERE reply.post_id = ?'
                      ' ORDER BY created ASC',(id,)).fetchall()

    return render_template('forum/post.html',post=post,replys=replys)

@bp.route('/newpost', methods=('GET','POST'))
@login_required
def new_post():

    if request.method == 'POST':
        topic = request.form['topic']
        body = request.form['body']

        error = None

        if not topic:
            error = "Topic is required"
        elif not body:
            error = "Body is required"

        if not error:
            db = get_db()
            db.execute('INSERT INTO post (user_id, topic, body) VALUES (?,?,?)',(g.user['id'],topic,body))
            db.commit()

            create_log("post")
            return redirect(url_for('forum.index'))
        
        flash(error)

    return render_template('forum/form.html',isPost=True)

@bp.route('/editpost/<id>', methods=('GET','POST'))
@login_required
def edit_post(id):

    db = get_db()
    
    if request.method == 'POST':
        topic = request.form['topic']
        body = request.form['body']

        error = None

        if not topic:
            error = "Topic is required"
        elif not body:
            error = "Body is required"

        if not error:
            db.execute('UPDATE post SET topic=?, body=? WHERE id=?',(topic,body,id,))
            db.commit()
            return redirect(url_for('forum.post',id=id))

        flash(error)

    data = db.execute('SELECT * FROM post WHERE id=?',(id,)).fetchone()

    return render_template('forum/form.html',isPost=True,data=data)

@bp.route('/newreply/<id>', methods=('GET','POST'))
@login_required
def new_reply(id):

    if request.method == 'POST':
        body = request.form['body']

        error = None
        if not body:
            error = "Body is required"

        if not error:
            db = get_db()
            db.execute('INSERT INTO reply (user_id, post_id, body) VALUES (?,?,?)',(g.user['id'],id,body))
            db.commit()

            create_log("reply")
            return redirect(url_for('forum.post',id=id))
        
        flash(error)

    return render_template('forum/form.html',isPost=False)

@bp.route('/editreply/<id>', methods=('GET','POST'))
@login_required
def edit_reply(id):

    db = get_db()
    
    if request.method == 'POST':

        body = request.form['body']

        error = None
        if not body:
            error = "Body is required"

        if not error:
            db.execute('UPDATE reply SET body=? WHERE id=?',(body,id))
            db.commit()

            post_id = db.execute('SELECT post_id FROM reply WHERE id=?',(id,)).fetchone()['post_id']

            return redirect(url_for('forum.post',id=post_id))

        flash(error)

    data = db.execute('SELECT * FROM reply WHERE id=?',(id,)).fetchone()

    return render_template('forum/form.html',isPost=False,data=data)

