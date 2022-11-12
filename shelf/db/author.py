from . import db


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'Author({self.name})'

    @staticmethod
    def get_or_create(name):
        existing = Author.query.filter_by(name=name).first()
        if existing:
            return existing
        a = Author(name=name)
        db.session.add(a)
        db.session.commit()
        return a