from flask_wtf import FlaskForm

from wtforms import SubmitField, BooleanField, StringField, PasswordField
from wtforms.validators import DataRequired, ValidationError, EqualTo, Email
import app
from flask_wtf.file import FileField, FileAllowed


class RegistracijosForma(FlaskForm):
    vardas = StringField("Vardas", [DataRequired()])
    el_pastas = StringField("El. paštas", [Email()])
    slaptazodis = PasswordField("Slaptažodis", [DataRequired()])
    patvirtintas_slaptazodis = PasswordField(
        "Pakartokite slaptažodį", [EqualTo("slaptazodis", "Slaptažodis turi sutapti.")]
    )
    submit = SubmitField("Prisiregistruoti")

    def tikrinti_varda(self, vardas):
        vartotojas = app.Vartotojas.query.filter_by(vardas=vardas.data).first()
        if vartotojas:
            raise ValidationError("Šis vardas panaudotas. Pasirinkite kitą.")

    def tikrinti_pasta(self, el_pastas):
        vartotojas = app.Vartotojas.query.filter_by(el_pastas=el_pastas.data).first()
        if vartotojas:
            raise ValidationError("Šis el. pašto adresas panaudotas. Pasirinkite kitą.")


class PrisijungimoForma(FlaskForm):
    el_pastas = StringField("El. paštas", [DataRequired()])
    slaptazodis = PasswordField("Slaptažodis", [DataRequired()])
    prisiminti = BooleanField("Prisiminti mane")
    submit = SubmitField("Prisijungti")


class IrasoForma(FlaskForm):
    irasas = StringField("Įveskite žinutę.", [DataRequired()])
    submit = SubmitField("Patvirtinti")


class PaskyrosAtnaujinimoForma(FlaskForm):
    vardas = StringField("Vardas", [DataRequired()])
    el_pastas = StringField("El. paštas", [DataRequired()])
    nuotrauka = FileField(
        "Atnaujinti profilio nuotrauką", validators=[FileAllowed(["jpg", "png"])]
    )
    submit = SubmitField("Atnaujinti")
