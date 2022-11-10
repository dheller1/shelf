from . import db
from .written_by import written_by

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(200), default='')
    edition = db.Column(db.String(100), default='')
    authors = db.relationship('Author', secondary=written_by, lazy='subquery', backref=db.backref('books', lazy=True))

    def __repr__(self):
        return f'Book({self.title})'
