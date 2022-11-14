import json
import requests
from sqlalchemy import func

from .. import db
from shelf.core.isbn import ISBN


class ISBNCache(db.Model):
    isbn = db.Column(db.String(13), primary_key=True)  # only the digits, which should be either 10 or 13 digits
    reply = db.Column(db.String(2000), default='')  # the full json info string
    updated = db.Column(db.DateTime, default=func.now(), onupdate=func.now())

    @staticmethod
    def get(isbn):
        """ isbn should be an ISBN instance, or a string containing only the 10 or 13 ISBN digits.
         Returns a JSON object containing info about the given book, or None if it cannot be found. """
        if isinstance(isbn, ISBN):
            isbn = isbn.digits()

        existing = ISBNCache.query.get(isbn)
        if existing:
            print(f'Found {isbn} in ISBN cache.')
            return json.loads(existing.reply)
        else:
            print(f'Did not find {isbn} in ISBN cache! Querying now...')
            info_str = ISBNCache._query_info(isbn)
            if info_str:
                cache_item = ISBNCache(isbn=isbn, reply=info_str)
                db.session.add(cache_item)
                db.session.commit()
                return json.loads(info_str)
            return None

    @staticmethod
    def _query_info(isbn_digits):
        """ Returns the openlibrary JSON info for the book given by `isbn_digits`. The returned value is a string, but
        can be converted/parsed to a JSON object. """
        url = f'https://openlibrary.org/isbn/{isbn_digits}.json'
        r = requests.get(url)
        if r.status_code == 200:
            return r.text
        return ''
