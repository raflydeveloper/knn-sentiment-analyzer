# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Dataset(db.Model):
    __tablename__ = 'dataset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=True)
    # Kolom 'label' dihapus dari model ini

class Preprocessing(db.Model):
    __tablename__ = 'preprocessing'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text, nullable=False) # Teks asli disimpan untuk referensi
    text_clean = db.Column(db.Text, nullable=True)
    text_stopwords = db.Column(db.Text, nullable=True)
    text_stem = db.Column(db.Text, nullable=True) # Teks bersih untuk klasifikasi
    created_at = db.Column(db.DateTime, nullable=False)
    label = db.Column(db.String(25), nullable=True) # Label hanya ada di sini