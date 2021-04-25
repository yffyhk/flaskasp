from functools import wraps
from flaskasp.db import get_db
from flaskasp.log import create_log

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
)

bp = Blueprint('article', __name__, url_prefix='/article', static_folder='static')

@bp.route('/<title>', methods=('GET','POST'))
def page(title):

    db = get_db()
    articles = db.execute('SELECT * FROM article WHERE title=? ORDER BY turn ASC',(title,)).fetchall()
    

    return render_template('article/article.html',articles=articles)