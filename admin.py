from functools import wraps
from flaskasp.db import get_db
from flaskasp.auth import admin_required
from flaskasp.log import create_log

import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
)

bp = Blueprint('admin', __name__, url_prefix='/admin', static_folder='static')

@bp.route('/editpage', methods=('GET','POST'))
@admin_required
def edit_page():

    db = get_db()

    if request.method == 'POST':
        domain = request.form['domain']

        error = None
        if not domain:
            error = 'Domain is required.'
        elif db.execute('SELECT * FROM book WHERE title = ?',(domain,)).fetchone() is not None:
            error = 'Domain {} is already registered.'.format(domain)

        if not error:
            db.execute('INSERT INTO book (title,author_id) VALUES (?,?)',(domain,g.user['id']))
            db.execute("INSERT INTO article (title,topic,body,turn) VALUES (?,'New Article','Some Text',0)",(domain,))
            db.commit()

            id = db.execute('Select id FROM article WHERE title=? AND turn=0',(domain,)).fetchone()

            create_log("new page")
            create_log("new article")
            return redirect(url_for('admin.edit_article',title=domain,id=id['id']))
        
        flash(error)

    books = db.execute(
        'SELECT b.title AS title, a.topic AS topic, created, username, a.body AS body, a.id AS id'
        ' FROM book b'
        ' LEFT JOIN user u ON b.author_id = u.id'
        ' LEFT JOIN article a ON (b.title = a.title) AND (a.turn = 0)'
        ' ORDER BY created DESC'
    ).fetchall()

    return render_template('admin/editpage.html',books=books)

@bp.route('/deletepage/<title>', methods=('GET',))
@admin_required
def delete_page(title):

    if title != 'home':
        db = get_db()

        db.execute("DELETE FROM article WHERE title=?",(title,))
        db.execute("DELETE FROM book WHERE title=?",(title,))

        db.commit()

        create_log("delete page")
        return redirect(url_for('admin.edit_page'))

    return "You cannot delete home page"

@bp.route('/newarticle/<title>', methods=('GET',))
@admin_required
def new_article(title):
    db = get_db()

    count = len(db.execute('SELECT id FROM article WHERE title = ?',(title,)).fetchall())

    db.execute("INSERT INTO article (title,topic,body,turn) VALUES (?,'New Article','Some Text',?)",(title,count))
    db.commit()

    id = db.execute('Select id FROM article WHERE title=? AND turn=?',(title,count)).fetchone()
    
    create_log("new article")
    return redirect(url_for('admin.edit_article',title=title,id=id['id']))

@bp.route('/deletearticle/<title>/<id>', methods=('GET',))
@admin_required
def delete_article(title,id):
    db = get_db()
    
    count = len(db.execute('SELECT id FROM article WHERE title=?',(title,)).fetchall())

    if count > 1:
        turn = int(db.execute('SELECT turn FROM article WHERE id=?',(id,)).fetchone()['turn'])

        db.execute('DELETE FROM article WHERE title = ? AND id = ?',(title,id))

        db.execute('UPDATE article SET turn = turn-1 WHERE title = ? AND turn > ?',(title,turn))

        db.commit()

        id = db.execute('Select id FROM article WHERE title=? AND turn=0',(title,)).fetchone()

        create_log("delete article")
        return redirect(url_for('admin.edit_article',title=title,id=id['id']))

    return "At least one article"

@bp.route('/editarticle/<title>/<id>', methods=('GET','POST'))
@admin_required
def edit_article(title,id):

    db = get_db()

    topics = db.execute(
        'SELECT topic,id,turn'
        ' FROM article'
        ' WHERE title = ?'
        ' ORDER BY turn ASC',(title,)
    ).fetchall()

    if request.method == 'POST':
        error = None

        f_topic = request.form['header']
        f_sequence = int(request.form['sequence'])
        f_body = request.form['body']
        f_button = request.form['button']
        f_link = request.form['link']
        f_image = request.form['image']

        if not f_topic:
            error = 'Topic is required.'
        elif not f_sequence and f_sequence != 0:
            error = 'Sequence is required.'
        elif not f_body:
            error = 'Body is required.'
        elif bool(f_button) != bool(f_link):
            error = 'Button Name and Link both required.'

        if error is None:
            biggest_turn = len(topics) - 1
            f_sequence = max(f_sequence,0)
            f_sequence = min(f_sequence,biggest_turn)

            oturn = db.execute('SELECT turn FROM article WHERE id=?',(id,)).fetchone()['turn']
            if oturn > f_sequence:
                db.execute('UPDATE article SET turn = turn+1 WHERE title=? AND turn>=? AND turn<?',(title,f_sequence,oturn))
            elif oturn < f_sequence:
                db.execute('UPDATE article SET turn = turn-1 WHERE title=? AND turn>? AND turn<=?',(title,oturn,f_sequence))


            db.execute('UPDATE article'
                    ' SET topic = ?,'
                    ' body = ?,'
                    ' button = ?,'
                    ' link = ?,'
                    ' turn = ?,'
                    ' image = ?'
                    ' WHERE id = ?',(f_topic, f_body, f_button, f_link, f_sequence, f_image, id)
            )
            db.commit()
            
            create_log("edit article")
            return redirect(url_for('admin.edit_article',title=title,id=id))

        flash(error)
        

    images = os.listdir(os.path.join(bp.static_folder, 'icon'))

    article = db.execute('SELECT * FROM article WHERE id=?',(id,)).fetchone()

    domains = db.execute(
        'SELECT title'
        ' FROM book'
        ' ORDER BY created DESC'
    ).fetchall()

    return render_template('admin/editarticle.html',topics=topics,domains=domains,article=article,images=images)




