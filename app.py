from datetime import datetime, timezone
import sqlalchemy.orm as so
import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    current_user,
    logout_user,
    login_user,
    UserMixin,
    login_required,
)
import forms

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SECRET_KEY"] = "4654f5dfadsrfasdr54e6rae"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "biudzetas.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "prisijungti"
login_manager.login_message_category = "info"


class Vartotojas(db.Model, UserMixin):
    __tablename__ = "vartotojas"
    id = db.Column(db.Integer, primary_key=True)
    vardas = db.Column("Vardas", db.String(20), unique=True, nullable=False)
    el_pastas = db.Column(
        "El. pašto adresas", db.String(120), unique=True, nullable=False
    )
    slaptazodis = db.Column("Slaptažodis", db.String(60), unique=True, nullable=False)
    irasai = db.relationship("Irasas")


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


@login_manager.user_loader
def load_user(vartotojo_id):
    return Vartotojas.query.get(int(vartotojo_id))


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    db.create_all()
    form = forms.IrasoForma()
    if form.validate_on_submit():
        naujas_irasas = Irasas(message=form.irasas.data, vartotojas_id=current_user.id)
        db.session.add(naujas_irasas)
        db.session.commit()
        return redirect(url_for("irasai"))
    return render_template("index.html", form=form)


@app.route("/registruotis", methods=["GET", "POST"])
def registruotis():
    db.create_all()
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = forms.RegistracijosForma()
    if form.validate_on_submit():
        koduotas_slaptazodis = bcrypt.generate_password_hash(
            form.slaptazodis.data
        ).decode("utf-8")
        vartotojas = Vartotojas(
            vardas=form.vardas.data,
            el_pastas=form.el_pastas.data,
            slaptazodis=koduotas_slaptazodis,
        )
        db.session.add(vartotojas)
        db.session.commit()
        flash("Sėkmingai prisiregistravote! Galite prisijungti", "success")
        return redirect(url_for("index"))
    return render_template("registruotis.html", title="Register", form=form)


@app.route("/prisijungti", methods=["GET", "POST"])
def prisijungti():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = forms.PrisijungimoForma()
    if form.validate_on_submit():
        user = Vartotojas.query.filter_by(el_pastas=form.el_pastas.data).first()
        if user and bcrypt.check_password_hash(user.slaptazodis, form.slaptazodis.data):
            login_user(user, remember=form.prisiminti.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("index"))
        else:
            flash(
                "Prisijungti nepavyko. Patikrinkite el. paštą ir slaptažodį", "danger"
            )
    return render_template("prisijungti.html", title="Prisijungti", form=form)


@app.route("/atsijungti")
def atsijungti():
    logout_user()
    return redirect(url_for("index"))


@app.route("/paskyra")
@login_required
def account():
    return render_template("paskyra.html", title="Paskyra")


@app.route("/irasai")
@login_required
def irasai():
    all_rows = Irasas.query.filter_by(vartotojas_id=current_user.id)
    return render_template("irasai.html", title="Įrašai", visi_irasai=all_rows)


@app.route("/delete/<int:id>")
def delete(id):
    uzklausa = Irasas.query.get(id)
    db.session.delete(uzklausa)
    db.session.commit()
    return redirect(url_for("irasai"))


@app.route("/irasas_update/<int:id>", methods=["GET", "POST"])
def irasas_update(id):
    all_rows = Irasas.query.filter_by(vartotojas_id=current_user.id)
    form = forms.IrasoForma()
    irasas = Irasas.query.get(id)
    print(irasas, id)
    if form.validate_on_submit():
        irasas.message = form.irasas.data
        irasas.data_laikas = datetime.now(timezone.utc)
        db.session.commit()
        return redirect(url_for("irasai"))
    return render_template("irasas_update.html", form=form, irasas=irasas)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
    db.create_all()
