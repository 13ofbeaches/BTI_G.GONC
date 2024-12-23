import streamlit as st
import pandas as pd
import spacy
from PyPDF2 import PdfReader
import matplotlib.pyplot as plt
from io import BytesIO

# Memuat model spaCy untuk bahasa Jerman
nlp = spacy.load("de_core_news_sm")

# Styling menggunakan CSS
st.markdown(
    """
    <style>
    /* Warna latar belakang utama */
    body {
        background-color: #2f4f4f;
        color: #ede8e7;
    }
    /* Styling untuk sidebar */
    .css-1y4p8pa {
        background-color: #612525;
        color: #ede8e7;
    }
    /* Gaya umum untuk teks */
    .stTextInput, .stButton, .stFileUploader {
        color: #ede8e7;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Fungsi untuk membaca konten file PDF
def read_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Fungsi untuk membaca file TXT
def read_txt(file):
    return file.read().decode("utf-8")

# Fungsi deteksi negasi dengan hasil tabel
def detect_negation_with_right_word_table(text):
    doc = nlp(text)
    negation_words = ['nicht', 'kein', 'niemand', 'nirgendwo', 'nirgends', 'noch nicht', 'noch nie', 'nie', 'niemals', 'nicht mehr', 'nie mehr']
    results = []
    for sent in doc.sents:
        for i, token in enumerate(sent):
            if token.text.lower() in negation_words:
                results.append({
                    "Kalimat": sent.text.strip(),
                    "Negasi": token.text,
                    "Kata Setelah Negasi": sent[i + 1].text if i + 1 < len(sent) else "-"
                })
                break
    return pd.DataFrame(results)

# Fungsi deteksi komparatif dan superlatif
def detect_comparative_superlative_table(text):
    doc = nlp(text)
    results = []
    for i, token in enumerate(doc):
        if token.pos_ == 'ADJ':
            if 'er' in token.text and len(token.text) > 2:
                results.append({"Jenis": "Komparatif", "Kata": token.text})
            if token.text.startswith("am") and "sten" in token.text:
                results.append({"Jenis": "Superlatif", "Kata": token.text})
    return pd.DataFrame(results)

# Fungsi deteksi Indefinitpronomen
def detect_indefinitpronomen_table(text):
    doc = nlp(text)
    indefinitpronomen = ['man', 'jemand', 'einer', 'irgendwer', 'irgendwo', 'irgendwann', 'eins', 'irgendetwas']
    results = []
    for sent in doc.sents:
        for token in sent:
            if token.text.lower() in indefinitpronomen:
                results.append({"Kalimat": sent.text.strip(), "Indefinitpronomen": token.text})
    return pd.DataFrame(results)

# Fungsi deteksi konektor ganda
def detect_zweiteilige_konnektoren_table(text):
    doc = nlp(text)
    konnektoren_dict = {
        'Entweder - oder': ['entweder', 'oder'],
        'Einerseits - andererseits': ['einerseits', 'andererseits'],
        'Weder - noch': ['weder', 'noch'],
        'Zwar - aber': ['zwar', 'aber'],
        'Nicht nur - sondern': ['nicht nur', 'sondern'],
        'Sowohl - als auch': ['sowohl', 'als auch'],
        'Je ... desto': ['je', 'desto']
    }
    results = []
    for sent in doc.sents:
        for key, values in konnektoren_dict.items():
            if all(value in sent.text.lower() for value in values):
                results.append({"Kalimat": sent.text.strip(), "Konektor": key})
    return pd.DataFrame(results)

# Fungsi unduh dataframe sebagai CSV
def download_dataframe_as_csv(df, filename):
    csv = df.to_csv(index=False)
    st.download_button(
        label="Unduh Hasil sebagai CSV",
        data=csv,
        file_name=filename,
        mime="text/csv"
    )

# Fungsi untuk membuat diagram lingkaran
def create_pie_chart(data, title):
    fig, ax = plt.subplots()
    ax.pie(data.values(), labels=data.keys(), autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title(title)
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    return buffer

# Fungsi utama untuk FAQ
def faq_system():
    faq_data = {
        "Apa itu G.Gonc?": "G.Gonc adalah alat bantu untuk mendeteksi penggunaan gramatik bahasa Jerman.",
        "Bagaimana cara menggunakan G.Gonc?": "Masukkan teks dan pilih jenis gramatik yang ingin dianalisis.",
        "Apakah G.Gonc gratis?": "Ya, saat ini G.Gonc gratis digunakan."
    }
    st.header("FAQ")
    for question, answer in faq_data.items():
        with st.expander(question):
            st.write(answer)

# Streamlit App
st.title("G.GONC: Analisis Grammatik Bahasa Jerman")
st.write("Web ini mendeteksi berbagai fitur gramatik bahasa Jerman dari file atau teks langsung.")
st.sidebar.title("Navigasi")
menu = st.sidebar.radio("Menu:", ["Analisis Teks", "FAQ"])

# Input teks atau unggahan file
input_text = ""
uploaded_file = st.file_uploader("Unggah file (PDF atau TXT):", type=["pdf", "txt"])

if uploaded_file is not None:
    if uploaded_file.type == "application/pdf":
        input_text = read_pdf(uploaded_file)
    elif uploaded_file.type == "text/plain":
        input_text = read_txt(uploaded_file)
    st.write("### Isi File:")
    st.write(input_text)
else:
    input_text = st.text_area("Atau masukkan teks bahasa Jerman:", height=200)

# Pilihan Analisis
analysis_option = st.selectbox("Pilih jenis analisis:", [
    "Negasi",
    "Komparatif dan Superlatif",
    "Indefinitpronomen",
    "Zweiteilige Konnektoren"
])

# Tombol Analisis
if st.button("Analisis Gramatik"):
    if input_text.strip():
        analysis_counts = {}

        if analysis_option == "Negasi":
            st.markdown("### Analisis Negasi")
            df_negation = detect_negation_with_right_word_table(input_text)
            if not df_negation.empty:
                st.dataframe(df_negation)
                download_dataframe_as_csv(df_negation, "analisis_negasi.csv")
                analysis_counts["Negasi"] = len(df_negation)
            else:
                st.write("Tidak ada negasi ditemukan.")

        elif analysis_option == "Komparatif dan Superlatif":
            st.markdown("### Analisis Komparatif dan Superlatif")
            df_comp_super = detect_comparative_superlative_table(input_text)
            if not df_comp_super.empty:
                st.dataframe(df_comp_super)
                download_dataframe_as_csv(df_comp_super, "analisis_komparatif_superlatif.csv")
                analysis_counts["Komparatif dan Superlatif"] = len(df_comp_super)
            else:
                st.write("Tidak ada komparatif atau superlatif ditemukan.")

        elif analysis_option == "Indefinitpronomen":
            st.markdown("### Analisis Indefinitpronomen")
            df_indef = detect_indefinitpronomen_table(input_text)
            if not df_indef.empty:
                st.dataframe(df_indef)
                download_dataframe_as_csv(df_indef, "analisis_indefinitpronomen.csv")
                analysis_counts["Indefinitpronomen"] = len(df_indef)
            else:
                st.write("Tidak ada Indefinitpronomen ditemukan.")

        elif analysis_option == "Zweiteilige Konnektoren":
            st.markdown("### Analisis Zweiteilige Konnektoren")
            df_konnektoren = detect_zweiteilige_konnektoren_table(input_text)
            if not df_konnektoren.empty:
                st.dataframe(df_konnektoren)
                download_dataframe_as_csv(df_konnektoren, "analisis_zweiteilige_konnektoren.csv")
                analysis_counts["Zweiteilige Konnektoren"] = len(df_konnektoren)
            else:
                st.write("Tidak ada Zweiteilige Konnektoren ditemukan.")

        # Menampilkan diagram lingkaran jika ada hasil analisis
        if analysis_counts:
            st.markdown("### Diagram Lingkaran Frekuensi Fitur Gramatik")
            pie_chart = create_pie_chart(analysis_counts, "Frekuensi Fitur Gramatik")
            st.image(pie_chart, caption="Diagram Lingkaran", use_column_width=True)
    else:
        st.warning("Harap masukkan teks untuk dianalisis.")
elif menu == "FAQ":
    faq_system()
