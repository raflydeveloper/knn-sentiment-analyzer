# config.py

import os

# Opsional: Menentukan direktori dasar proyek untuk path yang lebih konsisten.
# basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """
    Konfigurasi dasar aplikasi.
    """
    # Kunci rahasia default. Sebaiknya diatur melalui environment variable bahkan untuk base config,
    # atau pastikan ini adalah nilai yang sangat umum dan akan selalu ditimpa.
    SECRET_KEY = os.getenv('BASE_SECRET_KEY', 'default_base_secret_key_please_change')
    
    # Konfigurasi URI untuk koneksi database
    # Contoh: 'mysql+mysqlconnector://user:password@host/dbname'
    # config.py
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'mysql+mysqlconnector://root@localhost/analisissentimen?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Folder untuk menyimpan file yang diunggah
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx'}

    # Pengaturan tambahan (opsional)
    TESTING = False
    DEBUG = False


class DevelopmentConfig(Config):
    """
    Konfigurasi untuk lingkungan pengembangan.
    """
    DEBUG = True
    # Untuk pengembangan, Anda bisa menggunakan SECRET_KEY yang lebih sederhana jika diwarisi dari Config
    # atau definisikan secara eksplisit di sini.
    # SECRET_KEY = 'kunci_rahasia_untuk_development_mode'
    
    # Contoh: Menggunakan database SQLite untuk pengembangan yang lebih mudah
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'development_app.db')


class ProductionConfig(Config):
    """
    Konfigurasi untuk lingkungan produksi.
    DEBUG mode harus selalu mati.
    SECRET_KEY HARUS diatur melalui environment variable dengan nilai yang aman dan unik.
    """
    DEBUG = False
    TESTING = False

    # Mengambil SECRET_KEY dari environment variable.
    # Jika tidak ditemukan, sebuah nilai fallback (TIDAK AMAN UNTUK PRODUKSI) akan digunakan
    # untuk mencegah aplikasi crash saat pengujian lokal jika FLASK_CONFIG=production
    # tetapi SECRET_KEY belum diatur di environment.
    _prod_secret_key_env = os.getenv('SECRET_KEY') # Variabel sementara untuk menampung hasil getenv
    if not _prod_secret_key_env:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("PERINGATAN: FLASK_CONFIG diatur ke 'production' TAPI SECRET_KEY environment")
        print("               variable TIDAK DITEMUKAN.")
        print("               Menggunakan kunci default SEMENTARA yang TIDAK AMAN untuk menjalankan aplikasi.")
        print("               Ini berisiko keamanan jika ini adalah lingkungan produksi aktual.")
        print("               PASTIKAN ANDA MENGATUR SECRET_KEY YANG KUAT DAN UNIK")
        print("               DI ENVIRONMENT VARIABLE UNTUK LINGKUNGAN PRODUKSI AKTUAL!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # Menggunakan SECRET_KEY dari Config dasar sebagai fallback jika _prod_secret_key_env tidak ada
        # atau definisikan fallback spesifik di sini.
        # Jika SECRET_KEY di Config dasar juga tidak aman, ini tetap berisiko.
        SECRET_KEY = Config.SECRET_KEY # Mewarisi dari Config dasar jika tidak ada di ENV
        if SECRET_KEY == 'default_base_secret_key_please_change': # Cek jika fallback juga default tidak aman
            SECRET_KEY = 'fallback_production_secret_key_VERY_UNSAFE_CONFIGURE_ENV_PROPERLY'

    else:
        SECRET_KEY = _prod_secret_key_env


class TestingConfig(Config):
    """
    Konfigurasi untuk lingkungan pengujian (testing).
    """
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///:memory:') # In-memory SQLite untuk tes cepat
    SECRET_KEY = 'kunci_rahasia_sederhana_untuk_testing'
    # WTF_CSRF_ENABLED = False # Jika menggunakan Flask-WTF dan ingin menonaktifkan CSRF untuk tes


# ==============================================================================
# PASTIKAN BAGIAN INI ADA DAN BERNAMA 'config' (HURUF KECIL SEMUA)
# INI ADALAH DICTIONARY YANG AKAN DIIMPOR OLEH web.py
# ==============================================================================
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig # Konfigurasi default jika FLASK_CONFIG tidak diatur
}
# ==============================================================================
# AKHIR DARI DEFINISI DICTIONARY 'config'
# ==============================================================================