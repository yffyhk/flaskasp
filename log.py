from datetime import date

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
)

from flaskasp.db import get_db

bp = Blueprint('log', __name__, url_prefix='/log')

@bp.route('/graph/<tag>', methods=('GET','POST'))
def graph(tag):
    
    db = get_db()
    
    tags = db.execute('SELECT DISTINCT tag FROM log ORDER BY tag ASC').fetchall()
 
    sameday = db.execute("SELECT strftime('%d', created) AS day, COUNT(*) AS count"
                         " FROM log"
                         " WHERE tag = ? AND created > (SELECT DATETIME('now', '-7 day'))"
                         " GROUP BY day"
                         " ORDER BY day ASC",(tag,)
    ).fetchall()

    today = int(date.today().strftime('%d'))

    datas = [0, 0, 0, 0, 0, 0, 0]
    for d in sameday:
        dday = int(d['day'])
        theday = 6 - (today - dday)
        datas[theday] += int(d['count'])

    return render_template('log.html',datas=datas,title=tag,tags=tags)

def create_log(tag):
    db = get_db()
    if g.user:
        db.execute('INSERT INTO log(user_id,tag) VALUES (?,?)',(g.user['id'],tag))
    else:
        db.execute('INSERT INTO log(tag) VALUES (?)',(tag,))
    db.commit()
        


