from typing import Optional

from prisma import Prisma, register, get_client
from prisma.models import Url
from hashids import Hashids
from flask import Flask, render_template, request, flash, redirect, url_for, g


def get_db() -> Prisma:
    try:
        return g.db
    except AttributeError:
        g.db = db = Prisma()
        db.connect()
        return db


def close_db(exc: Optional[Exception] = None) -> None:  # noqa: ARG001
    client = get_client()
    if client.is_connected():
        client.disconnect()


register(get_db)
app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config['SECRET_KEY'] = 'this should be a secret random string'

hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])


@app.route('/', methods=('GET',))
def index():
    return render_template('index.html')


@app.route('/', methods=('POST',))
def create_shortened():
    original: str = request.form['url']

    if not original:
        flash('The URL is required!')
        return redirect(url_for('index'))

    url = Url.prisma().create(
        {
            'original': original,
        }
    )
    hashid = hashids.encode(url.id)
    short_url = request.host_url + hashid
    return render_template('index.html', short_url=short_url)


@app.route('/<id>')
def url_redirect(id: str):
    decoded = hashids.decode(id)
    if decoded:
        original_id = decoded[0]
        url = Url.prisma().update(
            where={
                'id': original_id,
            },
            data={
                'clicks': {
                    'increment': 1,
                },
            },
        )
        if url is None:
            flash('URL not found')
            return redirect(url_for('index'))

        return redirect(url.original)
    else:
        flash('Invalid URL')
        return redirect(url_for('index'))


@app.route('/stats')
def stats():
    urls = Url.prisma().find_many(
        order={
            'clicks': 'desc',
        }
    )
    short_urls = {url.id: request.host_url + hashids.encode(url.id) for url in urls}
    return render_template('stats.html', urls=urls, short_urls=short_urls)
