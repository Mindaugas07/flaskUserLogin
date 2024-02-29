import os
from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, logout_user, login_user, login_required
from datetime import datetime
import secrets
from PIL import Image
from flask_mail import Message
from biudzetas import forms, db, app, bcrypt
from biudzetas.models import Vartotojas, Irasas


@app.route("/")
def index():
    return render_template("index.html")
