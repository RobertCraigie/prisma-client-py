from typing import Optional

from prisma import Client
from hashids import Hashids
from flask import Flask, render_template, request, flash, redirect, url_for, g


def get_db() -> Client:
    try:
        return g.db
    except AttributeError:
        g.db = db = Client()
        db.connect()
        return db


def close_db(exc: Optional[Exception] = None) -> None:
    print('close db called')
    db = g.pop('db', None)
    if isinstance(db, Client) and db.is_connected():
        db.disconnect()


app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config['SECRET_KEY'] = 'this should be a secret random string'

hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])


@app.route('/', methods=('GET',))
def index():
    return render_template('index.html')


@app.route('/', methods=('POST',))
def create_shortened():
    client = get_db()
    original: str = request.form['url']

    if not original:
        flash('The URL is required!')
        return redirect(url_for('index'))

    url = client.url.create(
        {
            'original': original,
        }
    )
    hashid = hashids.encode(url.id)
    short_url = request.host_url + hashid
    return render_template('index.html', short_url=short_url)


@app.route('/<id>')
def url_redirect(id: str):
    client = get_db()
    decoded = hashids.decode(id)
    if decoded:
        original_id = decoded[0]
        url = client.url.update(
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
    client = get_db()
    urls = client.url.find_many(
        order={
            'clicks': 'desc',
        }
    )
    short_urls = {url.id: request.host_url + hashids.encode(url.id) for url in urls}
    return render_template('stats.html', urls=urls, short_urls=short_urls)
