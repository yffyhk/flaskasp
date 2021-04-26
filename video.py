from flaskasp.db import get_db
from flaskasp.auth import admin_required

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
)

bp = Blueprint('video', __name__, url_prefix='/video')

@bp.route('/<page>', methods=('GET',))
def index(page):
    db = get_db()

    video_per_page = 3

    count = db.execute('SELECT COUNT(*) AS num FROM video').fetchone()
    count = int(count['num'])

    page = int(page)

    back = False 
    if page > 0 :
        back = True

    next = False 
    if count/video_per_page > page+1:
        next = True

    videos = db.execute('SELECT * FROM video ORDER BY created DESC LIMIT ? OFFSET ?',(video_per_page,page*video_per_page)).fetchall()

    return render_template('video/index.html',videos=videos,back=back,next=next,now=page)

@bp.route('/upload', methods=('GET','POST'))
@admin_required
def upload():

    if request.method == 'POST':
        topic = request.form['topic']
        body = request.form['body']
        link = request.form['link']

        error = None
        if not topic or not body or not link:
            error = "All information are required"

        if not error:
            db = get_db()
            db.execute('INSERT INTO video (topic,body,link) VALUES (?,?,?)',(topic,body,link))
            db.commit()

            return redirect(url_for('video.index',page=0))
        
        flash(error)

    return render_template('video/form.html')

@bp.route('/edit/<id>', methods=('GET','POST'))
@admin_required
def edit(id):

    db = get_db()

    if request.method == 'POST':
        topic = request.form['topic']
        body = request.form['body']
        link = request.form['link']

        error = None
        if not topic or not body or not link:
            error = "All information are required"

        if not error:
            db.execute('UPDATE video SET topic=?, body=?, link=? WHERE id=?',(topic,body,link,id))
            db.commit()

            return redirect(url_for('video.index',page=0))
        
        flash(error)

    data = db.execute('SELECT * FROM video WHERE id=?',(id,)).fetchone()

    return render_template('video/form.html',data=data)

@bp.route('/delete/<id>', methods=('GET',))
@admin_required
def delete(id):

    db = get_db()
    db.execute('DELETE FROM video WHERE id=?',(id,))
    db.commit()

    return redirect(url_for('video.index',page=0))




