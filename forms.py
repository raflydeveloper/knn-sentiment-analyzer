# forms.py
from flask_wtf import FlaskForm
from wtforms import (FileField, StringField, SelectField, SubmitField, 
                     IntegerField, BooleanField, TextAreaField)
from flask_wtf.file import FileAllowed, FileRequired
from wtforms.validators import Optional, DataRequired, InputRequired, NumberRange

class UploadCSVForm(FlaskForm):
    file = FileField('Pilih file CSV atau Excel:', validators=[
        FileRequired(message='File belum dipilih.'),
        FileAllowed(['csv', 'xls', 'xlsx'], 'Hanya file CSV atau Excel yang diizinkan!')
    ])
    submit_upload = SubmitField('Unggah File')

class FilterDataForm(FlaskForm):
    search = StringField('Cari text...', validators=[Optional()])
    per_page = SelectField('Tampilkan',
                           choices=[(10, '10'), (20, '20'), (50, '50'), (100, '100')],
                           default=10,
                           coerce=int)

class DeleteAllDataForm(FlaskForm):
    submit_delete = SubmitField('Hapus Semua Data dari Semua Tabel')

class DeletePreprocessingDataForm(FlaskForm):
    submit_delete_preprocessing = SubmitField('Hapus Semua Data Preprocessing')

class LabelingForm(FlaskForm):
    label = SelectField('Label Sentimen',
                        choices=[
                            ('', 'Pilih Label'),
                            ('positif', 'Positif'),
                            ('negatif', 'Negatif'),
                            ('netral', 'Netral')
                        ],
                        validators=[Optional()])
    submit = SubmitField('Simpan Perubahan')

class LabelingFromFileForm(FlaskForm):
    label_file = FileField('Pilih File Label Pakar (Excel/CSV):', validators=[
        FileRequired(message='File label belum dipilih.'),
        FileAllowed(['csv', 'xls', 'xlsx'], 'Hanya file CSV atau Excel yang diizinkan!')
    ])
    submit_labeling = SubmitField('Lakukan Pelabelan')

class ClassificationForm(FlaskForm):
    """Form untuk menjalankan klasifikasi KNN."""
    k_value = IntegerField('Nilai K (Tetangga)', 
                           validators=[Optional(), NumberRange(min=1, message="Nilai K harus positif.")])
    
    # Field ini yang menyebabkan error karena tidak ada di file Anda
    test_size = IntegerField('Persentase Data Uji (%)', 
                             default=20, 
                             validators=[DataRequired(), NumberRange(min=10, max=50, message="Persentase harus antara 10 dan 50.")])
    
    submit_classify = SubmitField('Jalankan Klasifikasi Tunggal')
    submit_experiment = SubmitField('Cari K Terbaik (Validasi KNN)')


class PredictForm(FlaskForm):
    text_to_predict = TextAreaField('Masukkan Teks Baru untuk Diklasifikasi', 
                                    validators=[DataRequired(message="Teks tidak boleh kosong.")],
                                    render_kw={"rows": 4, "placeholder": "Contoh: uji coba vaksin ini sepertinya sangat bermanfaat bagi masyarakat..."})
    
    k_for_predict = IntegerField('Gunakan Nilai K',
                                 validators=[Optional(), NumberRange(min=1)])

    submit_predict = SubmitField('Prediksi Sentimen (dengan KNN)')
