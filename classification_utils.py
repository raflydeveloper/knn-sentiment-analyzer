# classification_utils.py

import math
from collections import Counter
import random
import statistics

class TFIDFVectorizer:
    def __init__(self):
        self.vocabulary_, self.idf_, self.doc_count_ = {}, {}, 0
    def _calculate_tf(self, c, t):
        return c / t if t > 0 else 0
    def fit(self, docs):
        self.doc_count_, term_doc_counts, vocab_idx = len(docs), Counter(), 0
        for doc in docs:
            seen = set()
            for term in doc.split():
                if term not in self.vocabulary_: self.vocabulary_[term], vocab_idx = vocab_idx, vocab_idx + 1
                if term not in seen:
                    term_doc_counts[term] += 1
                    seen.add(term)
        for term, count in term_doc_counts.items():
            self.idf_[term] = math.log((self.doc_count_ + 1) / (count + 1)) + 1
        return self
    def transform(self, docs):
        vectors = []
        for doc in docs:
            vec, terms, term_counts = [0.0] * len(self.vocabulary_), doc.split(), Counter(doc.split())
            for term, count in term_counts.items():
                if term in self.vocabulary_:
                    tf = self._calculate_tf(count, len(terms))
                    vec[self.vocabulary_[term]] = tf * self.idf_.get(term, 0)
            vectors.append(vec)
        return vectors

class KNeighborsClassifier:
    def __init__(self, k=3):
        self.k, self.X_train_, self.y_train_, self.X_train_norms_ = k, None, None, None
    def fit(self, X_train, y_train):
        self.X_train_, self.y_train_ = X_train, y_train
        self.X_train_norms_ = [math.sqrt(sum(v**2 for v in vec)) for vec in self.X_train_]
        return self
    def _cosine_distance(self, n1, v1, n2, v2):
        if n1 == 0 or n2 == 0: return 1.0
        return 1.0 - (sum(a * b for a, b in zip(v1, v2)) / (n1 * n2))
    def _predict_single(self, x_test):
        norm_x = math.sqrt(sum(v**2 for v in x_test))
        dists = [(self._cosine_distance(norm_x, x_test, self.X_train_norms_[i], xt), self.y_train_[i]) for i, xt in enumerate(self.X_train_)]
        dists.sort(key=lambda item: item[0])
        neighbors = dists[:self.k]
        if not neighbors: return None
        weights = {}
        for dist, label in neighbors:
            weights[label] = weights.get(label, 0) + (1 / (dist + 1e-6))
        return max(weights, key=weights.get)
    def predict(self, X_test):
        return [self._predict_single(x) for x in X_test]

def train_test_split(X, y, test_size=0.2, random_state=None):
    combined = list(zip(X, y))
    if random_state is not None: random.seed(random_state)
    random.shuffle(combined)
    idx = int(len(combined) * (1 - test_size))
    train, test = combined[:idx], combined[idx:]
    return [d[0] for d in train], [d[0] for d in test], [d[1] for d in train], [d[1] for d in test]

def calculate_metrics(y_true, y_pred, labels=['positif', 'negatif', 'netral']):
    valid = [(t, p) for t, p in zip(y_true, y_pred) if p is not None]
    if not valid:
        z_mat = {l: {pl: 0 for pl in labels} for l in labels}
        z_rep = {l: {'precision': 0, 'recall': 0, 'f1_score': 0, 'support': 0} for l in labels}
        return {'confusion_matrix': z_mat, 'accuracy': 0, 'report': z_rep, 'labels': labels}
    y_t, y_p = zip(*valid)
    matrix = {l: {pl: 0 for pl in labels} for l in labels}
    for t, p in zip(y_t, y_p):
        if p in matrix[t]: matrix[t][p] += 1
    acc = sum(1 for t, p in zip(y_t, y_p) if t == p) / len(y_t) if y_t else 0
    rep = {}
    for l in labels:
        tp = matrix[l].get(l, 0)
        fp = sum(matrix[ol].get(l, 0) for ol in labels if ol != l)
        fn = sum(matrix[l].get(ol, 0) for ol in labels if ol != l)
        prec = tp / (tp + fp) if (tp + fp) > 0 else 0
        rec = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0
        rep[l] = {'precision': prec, 'recall': rec, 'f1_score': f1, 'support': tp + fn}
    return {'confusion_matrix': matrix, 'accuracy': acc, 'report': rep, 'labels': labels}

# ==============================================================================
# REVISI FINAL FUNGSI K-FOLD UNTUK HASIL YANG 100% KONSISTEN
# ==============================================================================
def run_kfold_cross_validation(X, y, k_options, n_folds=5, random_state=None):
    """Menjalankan Stratified K-Fold CV yang bisa direproduksi secara konsisten."""
    data_by_label = {label: [] for label in set(y)}
    for i, label in enumerate(y):
        data_by_label[label].append((X[i], y[i]))

    # --- PERBAIKAN PENTING ADA DI SINI ---
    # Kocok data terlebih dahulu dengan satu seed yang terkontrol
    if random_state is not None:
        random.seed(random_state)
    
    # Gabungkan semua data kembali setelah dikelompokkan
    all_data_combined = []
    for label in sorted(data_by_label.keys()): # Urutkan keys agar urutan kelas konsisten
        items = data_by_label[label]
        random.shuffle(items) # Acak di dalam setiap kelas
        all_data_combined.extend(items)
    
    # Kocok sekali lagi data gabungan untuk memastikan distribusi antar fold lebih acak
    random.shuffle(all_data_combined)
    # ------------------------------------

    folds = [[] for _ in range(n_folds)]
    for i, item in enumerate(all_data_combined):
        folds[i % n_folds].append(item)

    k_accuracies = {k: [] for k in k_options}
    
    for i in range(n_folds):
        train_data = [item for idx, fold in enumerate(folds) if idx != i for item in fold]
        test_data = folds[i]

        X_train_fold, y_train_fold = [d[0] for d in train_data], [d[1] for d in train_data]
        X_test_fold, y_test_fold = [d[0] for d in test_data], [d[1] for d in test_data]

        if not X_train_fold or not X_test_fold: continue
        
        vectorizer = TFIDFVectorizer().fit(X_train_fold)
        X_train_tfidf, X_test_tfidf = vectorizer.transform(X_train_fold), vectorizer.transform(X_test_fold)
        
        for k in k_options:
            knn = KNeighborsClassifier(k=k).fit(X_train_tfidf, y_train_fold)
            y_pred = knn.predict(X_test_tfidf)
            
            accuracy = sum(1 for t, p in zip(y_test_fold, y_pred) if t == p) / len(y_test_fold) if y_test_fold else 0
            k_accuracies[k].append(accuracy)
            
    summary_results = []
    for k, accs in k_accuracies.items():
        if accs:
            avg_acc = statistics.mean(accs)
            std_dev = statistics.stdev(accs) if len(accs) > 1 else 0.0
            summary_results.append({'k': k, 'avg_accuracy': avg_acc, 'std_dev': std_dev})
            
    return summary_results