from sqlalchemy import DateTime
from datetime import datetime, timezone
from itsdangerous import SignatureExpired, URLSafeTimedSerializer as Serializer
from flask_login import UserMixin
from biudzetas import app, db
import sqlalchemy.orm as so


class Vartotojas(db.Model, UserMixin):
    __tablename__ = "vartotojas"
    id = db.Column(db.Integer, primary_key=True)
    vardas = db.Column("Vardas", db.String(20), unique=True, nullable=False)
    el_pastas = db.Column(
        "El. pašto adresas", db.String(120), unique=True, nullable=False
    )
    nuotrauka = db.Column(db.String(20), nullable=False, default="default.jpg")
    slaptazodis = db.Column("Slaptažodis", db.String(60), unique=True, nullable=False)
    irasai = db.relationship("Irasas")

    def get_reset_token(self):
        s = Serializer(app.config["SECRET_KEY"])
        return s.dumps({"user_id": self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token, max_age=1800)["user_id"]
        except:
            return None
        return Vartotojas.query.get(user_id)


class Irasas(db.Model, UserMixin):
    __tablename__ = "irasas"
    id = db.Column(db.Integer, primary_key=True)
    data_laikas: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc)
    )
    message = db.Column(db.Text, nullable=False)
    vartotojas_id = db.Column(db.Integer, db.ForeignKey("vartotojas.id"))
    vartotojas = db.relationship(
        "Vartotojas", cascade="all, delete", passive_deletes=True
    )
