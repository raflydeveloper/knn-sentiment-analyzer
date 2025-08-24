# preprocessing.py

import time
from sqlalchemy import text
from models import db, Preprocessing, Dataset
from preprocessing_utils import full_preprocess_text

def run_preprocessing_in_batches(app):
    """
    Workflow utama preprocessing yang membawa serta label dari data mentah.
    """
    start_time = time.time()
    with app.app_context():
        # Hapus data preprocessing lama
        Preprocessing.query.delete()
        if db.engine.name == 'mysql':
            db.session.execute(text("ALTER TABLE preprocessing AUTO_INCREMENT = 1"))
        db.session.commit()

        # Ambil semua data dari tabel Dataset
        dataset_entries = Dataset.query.all()
        if not dataset_entries:
            print("Tidak ada data di tabel Dataset untuk diproses.")
            return 0
        
        new_preprocessing_entries = []
        for entry in dataset_entries:
            processed_text = full_preprocess_text(entry.text)
            
            # Hanya simpan jika hasil stemming tidak kosong
            if processed_text['stemmed']:
                new_entry = Preprocessing(
                    username=entry.username,
                    text=entry.text, # Simpan teks asli
                    text_clean=processed_text['cleaned'],
                    text_stopwords=processed_text['stopwords_removed'],
                    text_stem=processed_text['stemmed'],
                    created_at=entry.created_at
                    # Baris 'label=entry.label' sudah dihapus
                )
                new_preprocessing_entries.append(new_entry)
        
        if new_preprocessing_entries:
            db.session.bulk_save_objects(new_preprocessing_entries)
            db.session.commit()
            
        end_time = time.time()
        print(f"Preprocessing selesai dalam {end_time - start_time:.2f} detik.")
        return len(new_preprocessing_entries)