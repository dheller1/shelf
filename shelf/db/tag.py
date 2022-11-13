from . import db


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f'Tag({self.name})'

    @staticmethod
    def get_or_create(name):
        existing = Tag.query.filter_by(name=name).first()
        if existing:
            return existing
        t = Tag(name=name)
        db.session.add(t)
        db.session.commit()
        return t
