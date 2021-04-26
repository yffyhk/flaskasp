from flaskasp.db import get_db
from flaskasp.auth import login_required

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
)

bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route('/<id>', methods=('GET',))
@login_required
def index(id):

    db = get_db()

    user = db.execute('SELECT * FROM user WHERE id=?',(id,)).fetchone()

    follow_list = db.execute('SELECT * FROM follow WHERE follower_id=? AND followed_id=?',(g.user['id'],id)).fetchone()
    
    isfollow = False
    if follow_list:
        isfollow = True

    my_posts = db.execute('SELECT * FROM post WHERE user_id=? ORDER BY created DESC LIMIT 5',(id,)).fetchall()
    my_replys = db.execute('SELECT * FROM reply WHERE user_id=? ORDER BY created DESC LIMIT 5',(id,)).fetchall()

    follower_posts = db.execute('SELECT post.id AS id, post.topic AS topic, post.created AS created'
                               ' FROM post, follow'
                               ' WHERE follow.follower_id = ? AND follow.followed_id = post.user_id'
                               ' ORDER BY post.created DESC LIMIT 5',(id,)).fetchall()
    
    follower_replys = db.execute('SELECT reply.post_id AS post_id, reply.body AS body, reply.created AS created'
                               ' FROM reply, follow'
                               ' WHERE follow.follower_id = ? AND follow.followed_id = reply.user_id'
                               ' ORDER BY reply.created DESC LIMIT 5',(id,)).fetchall()



    return render_template('profile/index.html',isfollow=isfollow,user=user,my_posts=my_posts,my_replys=my_replys,follower_posts=follower_posts,follower_replys=follower_replys)

@bp.route('/follow/<id>', methods=('GET',))
@login_required
def follow(id):

    if id != g.user['id']:
        db = get_db()
        db.execute('INSERT INTO follow (follower_id,followed_id) VALUES (?,?)',(g.user['id'],id))
        db.commit()

    return redirect(url_for('profile.index',id=id))

@bp.route('/unfollow/<id>', methods=('GET',))
@login_required
def unfollow(id):
    db = get_db()
    db.execute('DELETE FROM follow WHERE follower_id=? AND followed_id=?',(g.user['id'],id))
    db.commit()

    return redirect(url_for('profile.index',id=id))
