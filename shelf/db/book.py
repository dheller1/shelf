from . import db

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(200))
    edition = db.Column(db.String(100))

    def __repr__(self):
        return f'Book({self.title})'
