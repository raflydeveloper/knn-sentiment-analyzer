# preprocessing_utils.py (Versi Final dengan Blacklist)

import re
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from functools import lru_cache

# Inisialisasi komponen Sastrawi
stopword_factory = StopWordRemoverFactory()
stemmer_factory = StemmerFactory()
stemmer = stemmer_factory.create_stemmer()

# Daftar stopwords tambahan
additional_stopwords = ['yg', 'yaa', 'dgn', 'klo', 'tuh', 'nya', 'sih', 'aja', 'ke', 'deh']
base_stopwords = stopword_factory.get_stop_words()
STOPWORDS_SET = set(base_stopwords + additional_stopwords)


# ==============================================================================
# ===== DEFINISIKAN BLACKLIST DI SINI, TEMPAT YANG BENAR =====
# ==============================================================================
BLACKLISTED_WORDS = {
    'ajg', 'anggerweh', 'choda', 'cing', 'heeeeeee', 'kopet', 'mbagongkan',
    'mp', 'ngozi', 'njlapett', 'ojoss', 'pabeuliyyt', 'pangrekun', 'wahwahhh', 'ko', 'kok', 'enjus', 'seht', 'waduhhhhh', 'loh',
    'ponrekun', 'prex', 'profdesan', 'puki', 'rfk', 'sngerweeh', 'tay', 'preeettt', 'ckg ', 'jajarane', 'tololllllll', 'eaktat',
    'uy', 'uyyyyy', 'woyy', 'lha' , ' na', 'lahhh', 'preeeeetttt', 'hoi', 'lh', ' jalian', 'nah', 'kerasss', 'rfk', 'jr', 'siih', 'an', 'lah'
}


# Kamus slangword
SLANG_WORDS = {
    'abis': 'habis', 'ad': 'ada', 'adlh': 'adalah', 'afaik': 'as far as i know',
    'agan': 'juragan', 'aing': 'saya', 'aj': 'saja', 'ajh': 'saja', 'ak': 'aku', 'ako': 'aku', 'ap': 'apa',
    'ancur': 'hancur', 'anjeng': 'anjing', 'aq': 'aku', 'ato': 'atau', 'atw': 'atau',
    'bgt': 'sangat', 'bkn': 'bukan', 'bnyak': 'banyak', 'bodo': 'bodoh', 'bwt': 'buat', 'bagaimna': 'bagaimana',
    'd': 'di', 'dgn': 'dengan', 'dpt': 'dapat', 'dr': 'dari', 'duit': 'uang', 'elu': 'kamu',
    'emg': 'memang', 'ga': 'tidak', 'gak': 'tidak', 'gmn': 'bagaimana', 'gua': 'saya',
    'gue': 'saya', 'gw': 'saya', 'jgn': 'jangan', 'kalo': 'kalau', 'knp': 'kenapa',
    'kuy': 'ayo', 'lg': 'lagi', 'lgi': 'lagi', 'liat': 'lihat', 'loe': 'kamu',
    'lu': 'kamu', 'mager': 'malas gerak', 'msh': 'masih', 'ngga': 'tidak', 'nggak': 'tidak',
    'ntar': 'nanti', 'sm': 'sama', 'smg': 'semoga', 'smp': 'sampai', 'udah': 'sudah',
    'utk': 'untuk', 'yg': 'yang', 'abis': 'habis', 'ad': 'ada', 'adlh': 'adalah', 'afaik': 'as far as i know',
    'agan': 'juragan', 'aing': 'saya', 'aj': 'saja', 'ajh': 'saja', 'ak': 'aku', 'ako': 'aku',
    'alahkah': 'alangkah', 'alesan': 'alasan', 'alloh': 'allah', 'am': 'sama', 'ama': 'sama',
    'ancur': 'hancur', 'anjeng': 'anjing', 'antek2': 'antek', 'aq': 'aku', 'ato': 'atau', 'atw': 'atau',
    'au': 'tidak tahu', 'babel': 'bab', 'bacot': 'banyak bicara', 'bah': '',
    'bahayaa': 'bahaya', 'bais': 'habis', 'banget': 'sangat', 'banh': 'bang', 'bapa': 'bapak', 'berbasis': 'basis', 'bp': 'bapak',
    'barti': 'berarti', 'baso': 'bakso', 'bbrp': 'beberapa', 'bc': 'baca', 'boosss': 'bos',
    'bct': 'banyak bicara', 'bdg': 'bandung', 'bedaaaa': 'beda', 'bely gate': 'bill gates',
    'bener': 'benar', 'beneran': 'benaran', 'benerin': 'benarkan', 'bg': 'bill gates', 'biilgetes': 'bill gates', 'boosss': 'bos',
    'bgmn': 'bagaimana', 'bgt': 'sangat', 'bgtu': 'begitu', 'bhw': 'bahwa',
    'bhya': 'bahaya', 'biar': 'supaya', 'bijimane': 'bagaimana', 'bikin': 'buat', 'bboosss': 'bos',
    'bile gate': 'bill gates', 'bilget': 'bill gates', 'bintal': 'bimbingan mental',
    'bkn': 'bukan', 'bks': 'bekasi', 'bl': 'beli', 'bleh': 'boleh', 'blg': 'bilang', 'blm': 'belum',
    'blooon': 'bodoh', 'bls': 'balas', 'bngt': 'sangat', 'bnyak': 'banyak',
    'bodo': 'bodoh', 'boong': 'bohong', 'booss': 'bos', 'boss': 'bos', 'bnr': 'benar',
    'bpk': 'bapak', 'br': 'baru', 'brg': 'bareng', 'brp': 'berapa', 'bs': 'bisa', 'bosssss': 'bos',
    'bsk': 'besok', 'btul': 'betul', 'btw': 'by the way', 'bu': 'ibu', 'bwt': 'buat',
    'byk': 'banyak', 'cabs': 'cabut', 'cepet': 'cepat', 'capcus': 'pergi',
    'ce': 'cewek', 'cewe': 'cewek', 'cmiiw': 'correct me if i am wrong', 'cmn': 'cuma',
    'cnk': 'cantik', 'cong': 'selamat', 'convid': 'covid', 'coy': 'kawan', 'coz': 'karena',
    'cs': 'teman-teman', 'cuan': 'uang', 'd': 'di', 'dah': 'sudah', 'dapet': 'dapat', 'dechh': 'deh',
    'denger': 'dengar', 'dewe': 'sendiri', 'dg': 'dengan', 'dgn': 'dengan',
    'dijanjiin': 'dijanjikan', 'dijadiin': 'dijadikan', 'dijln': 'di jalan',
    'divacsin': 'divaksinasi', 'dket': 'dekat', 'dkt': 'dekat', 'dl': 'dulu',
    'dll': 'dan lain lain', 'dlu': 'dulu', 'dlm': 'dalam', 'doang': '', 'donk': 'dong',
    'dpr': 'dewan perwakilan rakyat', 'dpt': 'dapat', 'dr': 'dari', 'dri': 'dari', 'fulusss': 'uang',
    'drmn': 'darimana', 'drpd': 'daripada', 'dsb': 'dan sebagainya', 'dst': 'dan seterusnya',
    'dtg': 'datang', 'duit': 'uang', 'dums': 'dong', 'dunk': 'dong', 'dunno': 'tidak tahu',
    'dy': 'dia', 'efect': 'efek', 'efekx': 'efek', 'elu': 'kamu', 'emang': 'memang',
    'emg': 'memang', 'engga': 'tidak', 'ente': 'anda', 'epek': 'efek', 'eveknya': 'efeknya',
    'faksin': 'vaksin', 'faxin': 'vaksin', 'firus': 'virus', 'fulus': 'uang',
    'fuvksin': 'vaksin', 'g': 'tidak', 'ga': 'tidak', 'gaa': 'tidak', 'gaada': 'tidak ada', 'gah': 'tidak',
    'gaje': 'tidak jelas', 'gak': 'tidak', 'game': 'permainan', 'gan': 'juragan', 'gans': 'juragan', 'gas': 'ayo', 'gass': 'ayo', 'gaskeennn': 'ayo',
    'gawe': 'kerja', 'gbs': 'tidak bisa', 'geje': 'tidak jelas', 'gils': 'gila', 'god': 'tuhan', 
    'gimana': 'bagaimana', 'gini': 'begini', 'gitchu': 'begitu', 'gitu': 'begitu',
    'gj': 'tidak jelas', 'gk': 'tidak', 'globalis': 'globalis', 'gmn': 'bagaimana', 'blum': 'belum',
    'goblk': 'goblok', 'gp': 'tidak apa-apa', 'gpp': 'tidak apa-apa', 'gua': 'saya',
    'gue': 'saya', 'guldar': 'gula darah', 'gw': 'saya', 'halah': 'alah', 'hdp': 'hidup', 'he': 'kamu',
    'henti2nya': 'hentinya', 'hilih': 'alah', 'hilng': 'hilang', 'hri': 'hari',
    'hrp': 'harap', 'hrs': 'harus', 'idu': 'hidup', 'ilang': 'hilang', 'ilfil': 'tidak suka', 'terjdi': 'terjadi', 'is': 'itu',
    'imba': 'hebat', 'imo': 'in my opinion', 'ind': 'indonesia', 'indo': 'indonesia',
    'item': 'hitam', 'iti': 'itu', 'j': 'juga', 'ja': 'saja', 'jagan': 'jangan',
    'jajaran': 'jajaran', 'japri': 'jalur pribadi', 'jd': 'jadi', 'jdi': 'jadi', 'jg': 'juga',
    'jgn': 'jangan', 'jkt': 'jakarta', 'jln': 'jalan', 'jngn': 'jangan', 'jomblo': 'sendiri', 'jalian': 'kalian', 'k': 'ke', 'jls': 'jelas',
    'ka': 'kakak', 'kabor': 'kabur', 'kaga': 'tidak', 'kagak': 'tidak', 'kalo': 'kalau',
    'kangker': 'kanker', 'karna': 'karena', 'kayak': 'seperti', 'kayanya': 'sepertinya', 'sbnernya': 'sebenarnya',
    'kbr': 'kabar', 'kdg': 'kadang', 'kek': 'seperti', 'keknya': 'sepertinya',
    'kemenkes': 'kementerian kesehatan', 'kenak': 'kena', 'kepo': 'penasaran',
    'kere': 'tidak punya uang', 'kesel': 'kesal', 'ketr': 'keterangan', 'kga': 'tidak',
    'khendak': 'kehendak', 'kirain': 'dikira', 'kl': 'kalau', 'klarga': 'keluarga',
    'klrganya': 'keluarganya', 'klinci': 'kelinci', 'kelenci': 'kelinci', 'klo': 'kalau', 'klou': 'kalau', 'knaopa': 'kenapa',
    'klu': 'kalau', 'kluarga': 'keluarga', 'km': 'kamu', 'kmps': 'kampus', 'kmrn': 'kemarin', 'kefalam': 'ke dalam',
    'kn': 'kan', 'knapa': 'kenapa', 'knp': 'kenapa', 'koe': 'kamu', 'konspirasi': 'konspirasi',
    'kongkow': 'kumpul-kumpul', 'kpd': 'kepada', 'kpn': 'kapan', 'krenz': 'keren',
    'krg': 'kurang', 'krn': 'karena', 'krusuhan': 'kerusuhan', 'ksehatan': 'kesehatan', 'kovid': 'covid',
    'kt': 'kita', 'kumang': 'kuman', 'kuy': 'ayo', 'ky': 'seperti', 'kyk': 'seperti',
     'lgsg': 'langsung', 'lho': '', 'lht': 'lihat', 'liat': 'lihat', 'lo': 'kamu',
    'loe': 'kamu', 'lol': 'tertawa', 'lu': 'kamu', 'luchu': 'lucu', 'lum': 'belum', 'libih': 'lebih',
    'luwar': 'luar', 'lw': 'kamu', 'm': 'di', 'maaciw': 'terima kasih',
    'mager': 'malas gerak', 'makasih': 'terima kasih', 'males': 'malas', 'maneh': 'kamu', 'menkesnya': 'mentri sehat',
    'mantep': 'mantap', 'mantul': 'mantap betul', 'mao': 'mau', 'marai': 'membuat',
    'masalh': 'masalah', 'masi': 'masih', 'massa': 'masa', 'masukin': 'memasukkan', 'mulusss ': 'mulus',
    'melu': 'ikut', 'meninggl': 'meninggal', 'menkes': 'menteri kesehatan', 'mentri': 'menteri',
    'mepet': 'dekat sekali', 'mengatasin': 'mengatasi', 'mks': 'terima kasih',
    'mksd': 'maksud', 'mksih': 'terima kasih', 'mksi': 'terima kasih', 'mending': 'lebih baik',
    'mlm': 'malam', 'mls': 'malas', 'mnikmati': 'menikmati', 'mnt': 'minta',
    'mnusia': 'manusia', 'moga': 'semoga', 'moga2': 'semoga', 'mpr': 'majelis permusyawaratan rakyat',
    'mrk': 'mereka', 'msg': 'masing', 'msk': 'masuk', 'mslh': 'masalah', 'msh': 'masih',
    'msyarakat': 'masyarakat', 'mtr': 'motor', 'mulu': 'melulu', 'myb': 'mungkin', 'monggo': 'silakan',
    'n': 'dan', 'nakut': 'menakuti', 'napa': 'kenapa', 'nasgor': 'nasi goreng', 'nda': 'tidak', 'ngawwwuuuurrrrrrr': 'ngawur', 'nantimya': 'nanti',
    'ndak': 'tidak', 'ndonesia': 'indonesia', 'negri': 'negeri', 'nek': 'kalau',
    'nenemoyang': 'nenek moyang', 'ng': 'yang', 'ngakak': 'tertawa', 'ngapain': 'mengapa', 'ngawwwuuuurrrrrrr': 'ngawur',
    'ngapa': 'mengapa', 'ngapusi': 'berbohong', 'ngaret': 'terlambat', 'ngasih': 'memberi', 'ngawwwuuuurrrrrrr': 'ngawur',
    'ngatasin': 'mengatasi', 'ngga': 'tidak', 'nggak': 'tidak', 'ngk': 'tidak',
    'ngomong': 'berbicara', 'nih': '', 'nipu': 'tipu', 'nohh': 'itu', 'nnti': 'nanti',
    'ntaps': 'mantap', 'ntar': 'nanti', 'ntn': 'nonton', 'nyari': 'mencari',
    'nyampe': 'sampai', 'nyoba': 'mencoba', 'obatny': 'obatnya', 'ogah': 'tidak mau',
    'ok': 'ok', 'oke': 'ok', 'okeh': 'oleh', 'omg': 'oh my god', 'omon': 'omong',
    'ongkir': 'ongkos kirim', 'oot': 'out of topic', 'org': 'orang', 'otw': 'sedang di jalan',
    'p': 'pergi', 'pa': 'apa', 'pala': 'kepala', 'pake': 'pakai', 'paksin': 'vaksin',
    'pc': 'personal chat', 'pd': 'pada', 'pdhl': 'padahal', 'pede': 'percaya diri',
    'pegel': 'lelah', 'pejabat2': 'pejabat', 'pejabatnyaa': 'pejabatnya',
    'pemerentah': 'pemerintah', 'pen': 'ingin', 'pengen': 'ingin', 'pikirin': 'pikirkan', 'playing': 'bermain',
    'pinter': 'pintar', 'pk': 'pak', 'pke': 'pakai', 'plg': 'paling', 'pls': 'tolong',
    'pmerintah': 'pemerintah', 'pncitraan': 'pencitraan', 'pngn': 'ingin', 'pny': 'punya', 'puteh': 'putih',
    'positip': 'positif', 'prg': 'pergi', 'pret': 'omong kosong', 'pst': 'pasti',
    'ptg': 'penting', 'q': 'aku', 'qt': 'kita', 'rakyatpun': 'rakyat pun', 'rmh': 'rumah', 'rajyat': 'rakyat',
    'saia': 'saya', 'salken': 'salam kenal', ' safety': 'aman', 'sampean': 'anda', 'sampe': 'sampai',
    'sbb': 'maaf baru balas', 'sbg': 'sebagai', 'sbh': 'sebuah', 'sblm': 'sebelum',
    'sbnrnya': 'sebenarnya', 'safety': 'aman', 'sdg': 'sedang', 'sdgkn': 'sedangkan', 'sdh': 'sudah',
    'sdk': 'sedikit', 'sdra': 'saudara', 'se7': 'setuju', 'sehat2': 'sehat-sehat',
    'sejahtrakan': 'sejahterakan', 'semngat': 'semangat', 'sensara': 'sengsara',
    'sgt': 'sangat', 'shg': 'sehingga', 'si': 'ini', 'silahkan': 'silakan', 'scr': 'secara', ' seht ': 'sehat',
    'skali': 'sekali', 'skrang': 'sekarang', 'skrg': 'sekarang', 'skrng': 'sekarang',
    'slh': 'salah', 'sm': 'sama', 'smg': 'semoga', 'smoga': 'semoga', 'smp': 'sampai',
    'sms': 'pesan singkat', 'smw': 'semua', 'sndr': 'sendiri', 'sni': 'sini',
    'sodara': 'saudara', 'sok': 'berpura-pura', 'sok soan': 'sok tahu', 'sono': 'sana', 'seneng': 'senang',
    'sory': 'maaf', 'sotoy': 'sok tahu', 'softwere': ' perangkat lunak', 'spa': 'siapa', 'spt': 'seperti', 'srg': 'sering',
    'ssdh': 'sesudah', 'suntikin': 'suntikkan', 'sy': 'saya', 'sygnya': 'sayangnya', 'tbc': 'tuberkulosis',    't': 'di', 'tak': 'tidak', 'tau': 'tahu', 'tau2': 'tahu-tahu', 'tauu': 'tahu',
    'td': 'tadi', 'tdk': 'tidak', 'telat': 'terlambat', 'tengil': 'menyebalkan', 'tb' : 'tuberkulosis',
    'tgl': 'tanggal', 'thanks': 'terima kasih', 'thx': 'terima kasih', 'tks': 'terima kasih', 'tuhhhh': 'itu',
    'tlp': 'telepon', 'tmn': 'teman', 'tmbh': 'tambah', 'tnggu': 'tunggu', 'tny': 'tanya', 'trima': 'terima',
    'toh': '', 'tok': 'saja', 'tp': 'tapi', 'tq': 'terima kasih', 'trimakasih': 'terima kasih',
    'trims': 'terima kasih', 'trs': 'terus', 'trus': 'terus', 'tsb': 'tersebut', 
    'tst': 'tes', 'ttg': 'tentang', 'ttp': 'tetap', 'tu': 'itu', 'tuh': 'itu', 'tw': 'tahu', ' teryata': 'ternyata',
    'u': 'kamu', 'ud': 'sudah', 'udah': 'sudah', 'ujicoba': 'uji coba', 'ujg': 'ujung', 'udh': 'sudah',
    'ujung2nya': 'ujungnya', 'ul': 'ulangan', ' ujicobakan':'uji coba', 'untk': 'untuk', 'unyu': 'lucu',
    'utk': 'untuk', 'vansin': 'vaksin', 'vaks': 'vaksin', 'vaxcin': 'vaksin','ujicobakan': 'uji coba', 'vksin ': 'vaksin',
    'vaxin': 'vaksin', 'vc': 'video call', 'w': 'dengan', 'w/': 'dengan',
    'waki': 'wakil', 'waspadaa': 'waspada', 'wkt': 'waktu', 'wkwk': 'tertawa', 'waduhhhhh ': 'waduh', 'wowo': 'prabowo', 'wiwi': 'jokowi',
    'x': 'kali', 'y': 'ya', 'ya': 'iya', 'yaa': 'iya', 'yah': 'iya', 'yanti': 'nanti',
    'yg': 'yang', 'yanglikingkungana': 'lingkungan', 'yh': 'ya', 'yo': 'iya', 'yowes': 'ya sudah', 'yup': 'iya', 'yuk': 'ayo',
    'ywdh': 'ya sudah', 'yth': 'yang terhormat'
}

# Pola Regex tidak berubah
REGEX_PATTERNS = {
    'links': re.compile(r'http[s]?://\S+'),
    'mentions_hashtags': re.compile(r'[@#]\w+'),
    'non_alpha_numeric': re.compile(r'[^a-z\s]'),
    'repeated_chars': re.compile(r'(.)\1{2,}'),
    'extra_spaces': re.compile(r'\s{2,}')
}

@lru_cache(maxsize=None)
def cached_stem(word):
    return stemmer.stem(word)


# ===================================================================
# FUNGSI BARU UNTUK MEMPERBAIKI ENCODING
# ===================================================================
def fix_mojibake(text):
    """Mencoba memperbaiki teks yang rusak karena kesalahan encoding."""
    try:
        # Pola umum: Teks UTF-8 yang salah dibaca sebagai latin-1 atau windows-1252
        return text.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Jika gagal diperbaiki (karena memang bukan pola tsb), kembalikan teks asli
        return text

# ===================================================================
# FUNGSI UTAMA DIPERBARUI
# ===================================================================
def full_preprocess_text(text):
    """
    Fungsi terpusat untuk memproses satu buah teks dari awal hingga akhir.
    """
    # --- LANGKAH 0: PERBAIKAN ENCODING (MOJIBAKE) ---
    # Langkah ini ditambahkan di paling awal untuk memperbaiki teks "rusak"
    text = fix_mojibake(text)
    # ---------------------------------------------
    
    # 1. Case Folding
    text_lower = text.lower()
    
    # 2. Hapus Link, Mention, Hashtag
    text_no_links = REGEX_PATTERNS['links'].sub('', text_lower)
    text_no_mentions = REGEX_PATTERNS['mentions_hashtags'].sub('', text_no_links)
    
    # 3. Hapus Karakter Non-Alfabetik
    text_alpha = REGEX_PATTERNS['non_alpha_numeric'].sub(' ', text_no_mentions)
    
    # --- Tokenizing terjadi di sini secara implisit ---
    words = text_alpha.split()
    
    # 4. Hapus Kata dari Blacklist
    words = [word for word in words if word not in BLACKLISTED_WORDS]
    
    # 5. Normalisasi Kata Slang
    normalized_words = [SLANG_WORDS.get(word, word) for word in words]
    
    # 6. Hapus Spasi Berlebih
    text_cleaned = REGEX_PATTERNS['extra_spaces'].sub(' ', " ".join(normalized_words)).strip()
    
    # 7. Stopword Removal
    tokens = text_cleaned.split()
    text_stopwords_removed = " ".join([word for word in tokens if word not in STOPWORDS_SET])
    
    # 8. Stemming
    if text_stopwords_removed:
        stemmed_words = [cached_stem(word) for word in text_stopwords_removed.split()]
        text_stemmed = " ".join(stemmed_words)
    else:
        text_stemmed = ""

    return {
        "original": text, # Akan berisi teks yang sudah diperbaiki encodingnya
        "cleaned": text_cleaned,
        "stopwords_removed": text_stopwords_removed,
        "stemmed": text_stemmed
    }