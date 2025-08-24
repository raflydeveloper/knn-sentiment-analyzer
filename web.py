# web.py

from flask import Flask, render_template, request, flash, redirect, url_for, session
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import pandas as pd
import sqlalchemy
from sqlalchemy import or_, func, text
import statistics

from config import config
from models import db, Dataset, Preprocessing
from forms import (
    UploadCSVForm, 
    FilterDataForm, 
    DeleteAllDataForm, 
    DeletePreprocessingDataForm,
    LabelingForm,
    LabelingFromFileForm,
    ClassificationForm,
    PredictForm
)
from preprocessing_utils import full_preprocess_text
from preprocessing import run_preprocessing_in_batches
from classification_utils import (
    TFIDFVectorizer,
    KNeighborsClassifier,
    train_test_split,
    calculate_metrics,
    run_kfold_cross_validation,
    
)
from visualization_utils import generate_bar_chart_image, generate_pie_chart_image, generate_wordclouds


app = Flask(__name__)

# Konfigurasi Aplikasi
CONFIG_NAME = os.getenv('FLASK_CONFIG', 'default')
app.config.from_object(config[CONFIG_NAME])
if not app.config['SECRET_KEY']:
    raise ValueError("SECRET_KEY tidak diatur! Diperlukan untuk menggunakan session.")
db.init_app(app)

def clear_results_session():
    """Menghapus semua hasil dari session agar selalu fresh."""
    session.pop('detailed_results', None)
    session.pop('experiment_results', None)
    session.pop('single_prediction_result', None)
    session.pop('last_k_value', None)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def clean_text(text_data):
    if pd.isna(text_data): return ""
    return str(text_data).strip() 

@app.route('/')
def index():
    try:
        total_dataset_mentah = db.session.query(func.count(Dataset.id)).scalar()
        total_setelah_preprocessing = db.session.query(func.count(Preprocessing.id)).scalar()
        total_berlabel = db.session.query(func.count(Preprocessing.id)).filter(Preprocessing.label.isnot(None)).scalar()
        label_counts = db.session.query(Preprocessing.label, func.count(Preprocessing.label)).filter(Preprocessing.label.isnot(None)).group_by(Preprocessing.label).all()
        counts = { 'positif': 0, 'negatif': 0, 'netral': 0 }
        for label, count in label_counts:
            if label in counts: counts[label] = count
    except Exception as e:
        app.logger.error(f"Error fetching dashboard stats: {e}")
        total_dataset_mentah, total_setelah_preprocessing, total_berlabel = 0, 0, 0
        counts = {'positif': 0, 'negatif': 0, 'netral': 0}
    stats = {
        'total_dataset': total_dataset_mentah, 'total_preprocessing': total_setelah_preprocessing,
        'total_berlabel': total_berlabel, 'label_positif': counts['positif'],
        'label_negatif': counts['negatif'], 'label_netral': counts['netral']
    }
    return render_template('index.html', title="Dashboard", stats=stats)

@app.route('/input-data', methods=['GET', 'POST'])
def input_data():
    upload_form = UploadCSVForm()
    filter_form = FilterDataForm(request.args, meta={'csrf': False})
    delete_all_form = DeleteAllDataForm()
    if upload_form.validate_on_submit():
        clear_results_session()
        file = upload_form.file.data
        filename = secure_filename(file.filename)
        upload_folder = app.config.get('UPLOAD_FOLDER')
        if not upload_folder:
            flash('Kesalahan konfigurasi: Folder unggah tidak diatur.', 'error')
            return redirect(url_for('input_data'))
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        try:
            file_extension = filename.rsplit('.', 1)[1].lower()
            df = pd.read_excel(filepath).fillna('') if file_extension in ['xls', 'xlsx'] else pd.read_csv(filepath, encoding='utf-8').fillna('')
            Dataset.query.delete()
            Preprocessing.query.delete()
            db.session.commit() # Commit delete before resetting auto-increment
            if db.engine.name == 'mysql':
                db.session.execute(text("ALTER TABLE dataset AUTO_INCREMENT = 1"))
                db.session.execute(text("ALTER TABLE preprocessing AUTO_INCREMENT = 1"))
            db.session.commit()
            required_columns = {'username', 'text', 'created_at'}
            df.columns = [col.lower() for col in df.columns]
            if not required_columns.issubset(df.columns):
                missing_cols = required_columns - set(df.columns)
                flash(f'Kolom pada file Excel/CSV hilang: {", ".join(missing_cols)}.', 'error')
                return redirect(url_for('input_data'))
            new_dataset_entries = [Dataset(username=str(row['username']), text=clean_text(row['text']), created_at=pd.to_datetime(row['created_at'], errors='coerce').to_pydatetime()) for _, row in df.iterrows()]
            if new_dataset_entries:
                db.session.add_all(new_dataset_entries)
                db.session.commit()
            flash(f'{len(new_dataset_entries)} data mentah berhasil diunggah.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan saat memproses file: {str(e)}', 'error')
            app.logger.error(f"Error processing file {filename}: {e}", exc_info=True)
        return redirect(url_for('input_data'))
    
    page, per_page, search_query = request.args.get('page', 1, type=int), request.args.get('per_page', 10, type=int), request.args.get('search', '')
    filter_form.per_page.data, filter_form.search.data = per_page, search_query
    query = Dataset.query
    if search_query:
        search_filter = f'%{search_query}%'
        query = query.filter(or_(Dataset.text.ilike(search_filter), Dataset.username.ilike(search_filter)))
    data_paginated = query.order_by(Dataset.id.asc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('input_data.html', title="Input Data", upload_form=upload_form, filter_form=filter_form, delete_all_form=delete_all_form, data=data_paginated, total_data=data_paginated.total, search_query=search_query, current_per_page=per_page)

@app.route('/delete_all_data', methods=['POST'])
def delete_all_data():
    form = DeleteAllDataForm()
    if form.validate_on_submit():
        try:
            clear_results_session()
            Dataset.query.delete()
            Preprocessing.query.delete()
            db.session.commit()
            flash('Semua data berhasil dihapus dari semua tabel.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan saat menghapus semua data: {str(e)}', 'error')
    return redirect(url_for('input_data'))

@app.route('/preprocessing', methods=['GET', 'POST'])
def preprocessing():
    if request.method == 'POST':
        clear_results_session()
        processed_count = run_preprocessing_in_batches(app)
        flash(f'Preprocessing selesai. {processed_count} data berhasil diproses dan disimpan.', 'success')
        return redirect(url_for('preprocessing'))
    
    filter_form, delete_form = FilterDataForm(request.args, meta={'csrf': False}), DeletePreprocessingDataForm()
    page, per_page, search_query = request.args.get('page', 1, type=int), request.args.get('per_page', 10, type=int), request.args.get('search', '')
    filter_form.per_page.data, filter_form.search.data = per_page, search_query
    total_data_mentah = db.session.query(func.count(Dataset.id)).scalar()
    query = Preprocessing.query
    if search_query:
        search_filter = f'%{search_query}%'
        query = query.filter(or_(Preprocessing.username.ilike(search_filter), Preprocessing.text_stem.ilike(search_filter)))
    data_paginated = query.order_by(Preprocessing.id.asc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('preprocessing.html', title="Preprocessing Data", data=data_paginated, total_data_mentah=total_data_mentah, search_query=search_query, current_per_page=per_page, filter_form=filter_form, delete_form=delete_form)

@app.route('/preprocessing/delete', methods=['POST'])
def delete_preprocessing_data():
    form = DeletePreprocessingDataForm()
    if form.validate_on_submit():
        try:
            # Hapus juga hasil klasifikasi yang tersimpan karena sudah tidak relevan
            clear_results_session()
            num_rows_deleted = Preprocessing.query.delete()
            # Commit untuk mereset auto-increment jika perlu
            if db.engine.name == 'mysql':
                db.session.execute(text("ALTER TABLE preprocessing AUTO_INCREMENT = 1"))
            db.session.commit()
            flash(f'Semua {num_rows_deleted} data dari tabel Preprocessing berhasil dihapus.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal menghapus data preprocessing: {str(e)}', 'error')
    else:
        # Ini terjadi jika ada masalah dengan validasi form (misal: CSRF token)
        flash('Gagal menghapus data. Permintaan tidak valid.', 'warning')
    return redirect(url_for('preprocessing'))

@app.route('/pelabelan', methods=['GET'])
def pelabelan():
    filter_form, labeling_form, delete_form, labeling_file_form = FilterDataForm(request.args, meta={'csrf': False}), LabelingForm(), DeleteAllDataForm(), LabelingFromFileForm()
    page, per_page, search_query = request.args.get('page', 1, type=int), request.args.get('per_page', 10, type=int), request.args.get('search', '')
    query = Preprocessing.query
    if search_query:
        search_filter = f'%{search_query}%'
        query = query.filter(or_(Preprocessing.username.ilike(search_filter), Preprocessing.text_stem.ilike(search_filter)))
    data_paginated = query.order_by(Preprocessing.id.asc()).paginate(page=page, per_page=per_page, error_out=False)
    counts = {
        'total': db.session.query(func.count(Preprocessing.id)).scalar(),
        'positif': db.session.query(func.count(Preprocessing.id)).filter_by(label='positif').scalar(),
        'negatif': db.session.query(func.count(Preprocessing.id)).filter_by(label='negatif').scalar(),
        'netral': db.session.query(func.count(Preprocessing.id)).filter_by(label='netral').scalar()
    }
    return render_template('pelabelan.html', title="Pelabelan Manual", data=data_paginated, counts=counts, search_query=search_query, current_per_page=per_page, filter_form=filter_form, labeling_form=labeling_form, delete_form=delete_form, labeling_file_form=labeling_file_form)

@app.route('/pelabelan/edit/<int:id>', methods=['POST'])
def edit_label(id):
    form = LabelingForm()
    if form.validate_on_submit():
        clear_results_session()
        data_to_update = Preprocessing.query.get_or_404(id)
        new_label = form.label.data or None
        data_to_update.label = new_label
        try:
            db.session.commit()
            flash(f'Label untuk data ID {id} berhasil diperbarui.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal memperbarui label: {str(e)}', 'danger')
    return redirect(url_for('pelabelan', page=request.args.get('page', 1, type=int)))

# ==========================================================
# FUNGSI INI HARUS ADA DI FILE WEB.PY ANDA
# ==========================================================
@app.route('/pelabelan/hapus-label/<int:id>', methods=['POST'])
def hapus_label(id):
    # Menggunakan DeleteAllDataForm hanya untuk mendapatkan token CSRF, ini adalah praktik umum
    form = DeleteAllDataForm() 
    if form.validate_on_submit():
        clear_results_session()
        data_to_update = Preprocessing.query.get_or_404(id)
        try:
            data_to_update.label = None
            db.session.commit()
            flash(f'Label untuk data dengan ID {id} berhasil dihapus.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Gagal menghapus label: {str(e)}', 'danger')
    return redirect(url_for('pelabelan', page=request.args.get('page', 1, type=int)))
# ==========================================================

@app.route('/pelabelan/apply-from-file', methods=['POST'])
def apply_labels_from_file():
    form = LabelingFromFileForm()
    if form.validate_on_submit():
        # Setiap aksi pelabelan akan menghapus hasil klasifikasi lama
        clear_results_session()
        
        file = form.label_file.data
        filename = secure_filename(file.filename)
        upload_folder = app.config.get('UPLOAD_FOLDER')
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        try:
            file_extension = filename.rsplit('.', 1)[1].lower()
            df = pd.read_excel(filepath).fillna('') if file_extension in ['xls', 'xlsx'] else pd.read_csv(filepath, encoding='utf-8').fillna('')
            
            df.columns = [col.lower().strip() for col in df.columns]

            if not {'text', 'sentimen'}.issubset(df.columns):
                flash('File label harus memiliki kolom "text" dan "sentimen".', 'error')
                return redirect(url_for('pelabelan'))

            # LOGIKA UTAMA: Melabeli tabel PREPROCESSING
            
            # 1. Buat peta pencarian dari tabel PREPROCESSING
            preprocessing_map = {}
            for p_object in Preprocessing.query.all():
                cleaned_original_text = clean_text(p_object.text)
                if cleaned_original_text not in preprocessing_map:
                    preprocessing_map[cleaned_original_text] = []
                preprocessing_map[cleaned_original_text].append(p_object)
            
            updated_ids = set()
            not_found_count = 0

            # 2. Iterasi melalui file Excel untuk melabeli data
            for _, row in df.iterrows():
                original_text_from_file = clean_text(row['text'])
                label_value = str(row['sentimen']).strip().lower()

                list_of_data_to_update = preprocessing_map.get(original_text_from_file)
                
                if list_of_data_to_update:
                    # 3. Jika ditemukan, labeli SEMUA data yang cocok (termasuk duplikat)
                    for data_to_update in list_of_data_to_update:
                        if label_value in ['positif', 'negatif', 'netral']:
                            data_to_update.label = label_value
                            updated_ids.add(data_to_update.id)
                else:
                    not_found_count += 1
            
            final_updated_count = len(updated_ids)
            db.session.commit()
            
            flash(f'Pelabelan selesai. {final_updated_count} baris data unik berhasil diperbarui.', 'success')
            if not_found_count > 0:
                flash(f'Info: {not_found_count} baris dari file label tidak ditemukan di data preprocessing dan diabaikan.', 'info')

        except Exception as e:
            db.session.rollback()
            flash(f'Terjadi kesalahan saat memproses file label: {str(e)}', 'error')
            app.logger.error(f"Error processing label file: {e}", exc_info=True)
            
    else:
        for field, errors in form.errors.items():
            flash(f"{getattr(form, field).label.text}: {', '.join(errors)}", 'danger')
                
    return redirect(url_for('pelabelan'))

# ... (sisa route lain seperti klasifikasi dan visualisasi) ...
@app.route('/klasifikasi', methods=['GET', 'POST'])
def klasifikasi():
    form = ClassificationForm()
    predict_form = PredictForm()
    
    labeled_data_count = Preprocessing.query.filter(Preprocessing.label.isnot(None)).count()
    
    detailed_results = session.get('detailed_results', None)
    experiment_results = session.get('experiment_results', None)
    single_prediction_result = session.pop('single_prediction_result', None)

    # --- INI ADALAH KUNCI UTAMA ---
    RANDOM_STATE_SEED = 42
    # -----------------------------

    if request.method == 'GET':
        k_from_url = request.args.get('best_k', type=int)
        k_to_set = k_from_url or session.get('last_k_value')
        if k_to_set:
            form.k_value.data = k_to_set
            predict_form.k_for_predict.data = k_to_set

    if form.is_submitted() and (form.submit_classify.data or form.submit_experiment.data):
        if form.submit_experiment.data:
            clear_results_session()
            labeled_data = Preprocessing.query.filter(Preprocessing.label.isnot(None)).all()
            if len(labeled_data) < 20:
                flash('Tidak cukup data berlabel untuk validasi.', 'warning')
                return redirect(url_for('klasifikasi'))
            X_all, y_all = [data.text_stem for data in labeled_data], [data.label for data in labeled_data]
            k_options, N_FOLDS = [7, 9, 11, 13, 15, 17], 5
            
            # --- PASTIKAN random_state DIKIRIM KE FUNGSI ---
            summary_list = run_kfold_cross_validation(X_all, y_all, k_options, n_folds=N_FOLDS, random_state=RANDOM_STATE_SEED)
            
            if summary_list:
                session['experiment_results'] = summary_list
                best_result = max(summary_list, key=lambda item: item['avg_accuracy'])
                best_k_found = best_result['k']
                session['last_k_value'] = best_k_found
                flash(f'Validasi K-Fold selesai! K terbaik ditemukan: {best_k_found}.', 'success')
                return redirect(url_for('klasifikasi', best_k=best_k_found))

        elif form.submit_classify.data:
            # ... (sisa logika klasifikasi tunggal tidak berubah, karena sudah menggunakan RANDOM_STATE_SEED)
            if form.k_value.data is None: flash('Harap masukkan Nilai K.', 'warning'); return redirect(url_for('klasifikasi'))
            clear_results_session()
            k = form.k_value.data
            session['last_k_value'] = k
            labeled_data = Preprocessing.query.filter(Preprocessing.label.isnot(None)).all()
            if len(labeled_data) < 20: flash('Tidak cukup data berlabel.', 'warning'); return redirect(url_for('klasifikasi'))
            X_all, y_all = [data.text_stem for data in labeled_data], [data.label for data in labeled_data]
            test_size = form.test_size.data
            X_train, X_test, y_train, y_test = train_test_split(X_all, y_all, test_size=test_size/100.0, random_state=RANDOM_STATE_SEED)
            vectorizer = TFIDFVectorizer().fit(X_train)
            X_train_vec, X_test_vec = vectorizer.transform(X_train), vectorizer.transform(X_test)
            model = KNeighborsClassifier(k=k).fit(X_train_vec, y_train)
            y_pred = model.predict(X_test_vec)
            metrics = calculate_metrics(y_test, y_pred)
            session['detailed_results'] = {'model_name': f"KNN (K={k})",'k': k, 'test_size': test_size, 'metrics': metrics,'predictions': [{'text': X_test[i], 'actual': y_test[i], 'predicted': y_pred[i]} for i in range(len(y_test))], 'prediction_counts': {'total': len(y_test), 'positif': y_pred.count('positif'), 'negatif': y_pred.count('negatif'), 'netral': y_pred.count('netral')}}
            flash(f'Klasifikasi tunggal dengan KNN (K={k}) berhasil.', 'info')
            return redirect(url_for('klasifikasi', best_k=k))

    # Menangani form prediksi tunggal
    if predict_form.is_submitted() and predict_form.submit_predict.data:
        if not predict_form.validate():
            for field, errors in predict_form.errors.items():
                for error in errors:
                    flash(f"{getattr(predict_form, field).label.text}: {error}", 'danger')
            return redirect(url_for('klasifikasi'))

        k_predict = session.get('last_k_value')
        if not k_predict:
            flash('Harap jalankan sebuah klasifikasi setidaknya satu kali untuk menetapkan nilai K.', 'warning')
            return redirect(url_for('klasifikasi'))
        
        text_input = predict_form.text_to_predict.data
        preprocessed_text = full_preprocess_text(text_input)['stemmed']
        all_labeled_data = Preprocessing.query.filter(Preprocessing.label.isnot(None)).all()
        if len(all_labeled_data) < 10: flash('Tidak cukup data berlabel untuk prediksi.', 'warning')
        else:
            X_full, y_full = [d.text_stem for d in all_labeled_data], [d.label for d in all_labeled_data]
            vectorizer = TFIDFVectorizer().fit(X_full)
            X_full_vec, X_predict_vec = vectorizer.transform(X_full), vectorizer.transform([preprocessed_text])
            knn_model = KNeighborsClassifier(k=k_predict).fit(X_full_vec, y_full)
            prediction = knn_model.predict(X_predict_vec)[0]
            session['single_prediction_result'] = {'text': text_input, 'processed_text': preprocessed_text, 'prediction': prediction}
            session['last_k_value'] = k_predict
        return redirect(url_for('klasifikasi', best_k=k_predict))

    return render_template('klasifikasi.html', title="Klasifikasi & Validasi KNN", form=form, predict_form=predict_form, total_labeled_data=labeled_data_count, detailed_results=detailed_results, experiment_results=experiment_results, single_prediction_result=single_prediction_result)

@app.route('/klasifikasi/clear')
def clear_classification_results():
    clear_results_session()
    flash('Hasil klasifikasi sebelumnya telah dihapus.', 'info')
    return redirect(url_for('klasifikasi'))

@app.route('/visualisasi')
def visualisasi():
    # --- PERUBAHAN LOGIKA DIMULAI DI SINI ---

    # 1. Cek apakah ada hasil di session dari halaman klasifikasi
    detailed_results = session.get('detailed_results')

    # 2. Jika tidak ada hasil, tampilkan pesan error
    if not detailed_results:
        flash('Harap jalankan sebuah "Klasifikasi Tunggal" terlebih dahulu untuk melihat visualisasinya.', 'warning')
        return render_template('visualisasi.html', title="Visualisasi Hasil", error=True)

    # 3. Jika ada, gunakan hasil tersebut untuk membuat grafik
    try:
        # Ambil daftar prediksi dari session
        predictions_for_viz = detailed_results.get('predictions', [])

        if not predictions_for_viz:
            flash('Tidak ada prediksi valid yang ditemukan di hasil klasifikasi.', 'warning')
            return render_template('visualisasi.html', title="Visualisasi Hasil", error=True)

        # Hasilkan gambar-gambar grafik
        bar_chart_path = generate_bar_chart_image(predictions_for_viz, 'session', app.root_path)
        pie_chart_path = generate_pie_chart_image(predictions_for_viz, 'session', app.root_path)
        wordcloud_paths = generate_wordclouds(predictions_for_viz, 'session', app.root_path)
        
        return render_template(
            'visualisasi.html', 
            title="Visualisasi Hasil", 
            bar_chart_path=bar_chart_path, 
            pie_chart_path=pie_chart_path, 
            wordcloud_paths=wordcloud_paths, 
            error=False
        )
    except Exception as e:
        app.logger.error(f"Error generating visualization: {e}")
        flash('Terjadi kesalahan saat membuat gambar visualisasi.', 'danger')
        return render_template('visualisasi.html', title="Visualisasi Hasil", error=True)


@app.errorhandler(404)
def not_found_error(error): return render_template('404.html', title="Halaman Tidak Ditemukan"), 404

@app.errorhandler(500)
def internal_error(error): db.session.rollback(); return render_template('500.html', title="Kesalahan Server Internal"), 500

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists(app.config.get('UPLOAD_FOLDER')): os.makedirs(app.config.get('UPLOAD_FOLDER'))
        db.create_all()
    debug_mode = app.config.get('DEBUG', False)
    app.run(debug=debug_mode)