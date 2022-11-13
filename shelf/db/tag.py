from . import db
from sqlalchemy import func


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'Tag({self.name})'

    @staticmethod
    def get_or_create(name):
        existing = Tag.query.filter(func.lower(Tag.name) == func.lower(name)).first()
        if existing:
            return existing
        t = Tag(name=name)
        db.session.add(t)
        db.session.commit()
        return t
