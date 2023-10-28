import streamlit as st
import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import pairwise_distances, cosine_similarity
import faiss

tokenizer = AutoTokenizer.from_pretrained("cointegrated/rubert-tiny2")
model = AutoModel.from_pretrained("cointegrated/rubert-tiny2")

df = pd.read_csv('data_final.csv')

MAX_LEN = 300

def embed_bert_cls(text, model, tokenizer):
    t = tokenizer(text, padding=True, truncation=True, return_tensors='pt', max_length=MAX_LEN)
    with torch.no_grad():
        model_output = model(**{k: v.to(model.device) for k, v in t.items()})
    embeddings = model_output.last_hidden_state[:, 0, :]
    embeddings = torch.nn.functional.normalize(embeddings)
    return embeddings[0].cpu().numpy()

books_vector = np.loadtxt('vectors.txt')

index = faiss.IndexFlatIP(books_vector.shape[1])
index.add(books_vector)

st.title('Приложение для рекомендации книг')

text = st.text_input('Введите запрос:')
num_results = st.number_input('Введите количество рекомендаций:', min_value=1, max_value=50, value=1)

recommend_button = st.button('Найти')

if text and recommend_button:
    user_text_pred = embed_bert_cls(text, model, tokenizer)
    D, I = index.search(user_text_pred.reshape(1, -1), num_results)

    st.subheader('Топ рекомендуемых книг:')

    for i, j in zip(I[0], D[0]):
        col_1, col_2 = st.columns([1, 3])

        with col_1:
            st.image(df['image_url'][i], use_column_width=True)
            st.write(round(j* 100, 2))
        with col_2:
            st.write(f'Название книги: {df["title"][i]}')
            st.write(f'Название книги: {df["author"][i]}')
            st.write(f'Ссылка: {df["page_url"][i]}')
            st.write(f'Название книги: {df["annotation"][i]}')
            