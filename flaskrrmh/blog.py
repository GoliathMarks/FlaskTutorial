from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskrrmh.auth import login_required
from flaskrrmh.db import get_db

from typing import List

bp = Blueprint('blog', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    user_data: List = db.execute('SELECT * FROM like WHERE user_id = ?', (g.user['id'],)).fetchall()
    user_data = [it[1] for it in user_data]
    print(f"user_data = {user_data}")
    return render_template('blog/index.html', posts=posts, user_data=user_data)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, author_id)'
                ' VALUES (?, ?, ?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')


def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))


@bp.route('/<int:id>/detail', methods=('GET',))
def detail(id):
    post = get_post(id)

    return render_template('blog/detail.html', post=post)


@bp.route('/<int:id>/like', methods=('GET',))
@login_required
def like(id):
    get_post(id)
    db = get_db()
    res = db.execute("SELECT * FROM like WHERE user_id = ? AND post_id = ?", (g.user['id'], id)).fetchone()
    if not res:
        db.execute('INSERT INTO like (user_id, post_id) VALUES (?, ?)', (g.user['id'], id))
        db.commit()
    else:
        db.execute('DELETE FROM like WHERE user_id = ? AND post_id = ?', (g.user['id'], id))
        db.commit()

    return redirect(url_for('blog.index'))


