# visualization_utils.py

from wordcloud import WordCloud
import matplotlib
matplotlib.use('Agg')  # Mengatur backend agar tidak memerlukan GUI
import matplotlib.pyplot as plt
import os
from collections import Counter

def generate_bar_chart_image(predictions, mode, base_path):
    """Menghasilkan gambar bar chart dan menyimpannya sebagai file."""
    pred_labels = [item['predicted'] for item in predictions]
    counts = Counter(pred_labels)
    
    labels = ['Positif', 'Negatif', 'Netral']
    data = [counts.get('positif', 0), counts.get('negatif', 0), counts.get('netral', 0)]
    colors = ['#28a745', '#dc3545', '#6c757d']

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, data, color=colors)
    
    ax.set_ylabel('Jumlah Prediksi')
    ax.set_title('Distribusi Hasil Prediksi')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    for i, v in enumerate(data):
        ax.text(i, v + 0.5, str(v), ha='center', fontweight='bold')

    image_dir = os.path.join(base_path, 'static', 'images')
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    
    filename = f"barchart_{mode}.png"
    filepath = os.path.join(image_dir, filename)
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close(fig)
    
    return f'images/{filename}'


def generate_pie_chart_image(predictions, mode, base_path):
    """Menghasilkan gambar pie chart dan menyimpannya sebagai file."""
    pred_labels = [item['predicted'] for item in predictions]
    counts = Counter(pred_labels)
    
    labels = ['Positif', 'Negatif', 'Netral']
    data = [counts.get('positif', 0), counts.get('negatif', 0), counts.get('netral', 0)]
    colors = ['#28a745', '#dc3545', '#6c757d']

    filtered_data = [(d, l, c) for d, l, c in zip(data, labels, colors) if d > 0]
    
    fig, ax = plt.subplots(figsize=(6, 6))
    if not filtered_data:
        ax.text(0.5, 0.5, 'Tidak ada data', ha='center', va='center', fontsize=16, color='gray')
        ax.axis('off')
    else:
        data, labels, colors = zip(*filtered_data)
        ax.pie(data, labels=labels, colors=colors, autopct='%1.1f%%',
               startangle=90, wedgeprops={'edgecolor': 'white'})
        ax.axis('equal')
    
    # ===================================================================
    # PERBAIKAN DI SINI: Menambahkan padding pada judul
    # ===================================================================
    ax.set_title('Persentase Hasil Prediksi', pad=20)
    # ===================================================================

    image_dir = os.path.join(base_path, 'static', 'images')
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    filename = f"piechart_{mode}.png"
    filepath = os.path.join(image_dir, filename)
    plt.savefig(filepath, dpi=100, bbox_inches='tight')
    plt.close(fig)
    
    return f'images/{filename}'

# ==============================================================================
# REVISI UTAMA ADA DI FUNGSI INI
# ==============================================================================
def generate_wordclouds(predictions, mode, base_path):
    """Membuat dan menyimpan file gambar word cloud untuk setiap sentimen."""
    texts_by_sentiment = {'positif': [], 'negatif': [], 'netral': []}
    for item in predictions:
        sentiment = item['predicted']
        if sentiment in texts_by_sentiment:
            texts_by_sentiment[sentiment].append(item['text'])

    image_dir = os.path.join(base_path, 'static', 'images')
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    image_paths = {}
    for sentiment, texts in texts_by_sentiment.items():
        full_text = ' '.join(texts).strip()
        filename = f"wordcloud_{sentiment}_{mode}.png"
        filepath = os.path.join(image_dir, filename)

        # --- PERUBAHAN LOGIKA DIMULAI DI SINI ---
        if not full_text:
            # Jika tidak ada teks, buat gambar placeholder
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.text(0.5, 0.5, f"Tidak ada data prediksi\nuntuk sentimen '{sentiment}'",
                    ha='center', va='center', fontsize=16, color='gray')
            ax.axis('off')
            plt.savefig(filepath, dpi=100, bbox_inches='tight')
            plt.close(fig)
        else:
            # Jika ada teks, buat word cloud seperti biasa
            wordcloud = WordCloud(
                width=800, 
                height=400, 
                background_color='white',
                colormap='viridis',
                max_words=100,
                collocations=False # Menghindari kata ganda yang tidak perlu
            ).generate(full_text)
            
            wordcloud.to_file(filepath)
        # --- AKHIR PERUBAHAN LOGIKA ---
        
        image_paths[sentiment] = f'images/{filename}'
        
    return image_paths