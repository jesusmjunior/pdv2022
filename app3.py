
import streamlit as st
from PIL import Image
import numpy as np
import io

st.title("📷 Cadastro de Produto com Foto Direta")

# Captura da foto pelo usuário
img_file_buffer = st.camera_input("Tire uma foto do produto")

if img_file_buffer is not None:
    # Conversão para imagem PIL
    image = Image.open(img_file_buffer)
    st.image(image, caption="Imagem capturada", use_column_width=True)

    # Conversão opcional para processamento em array NumPy
    img_array = np.array(image)

    # Simulação de cadastro
    st.subheader("📝 Informações do Produto")
    nome = st.text_input("Nome do Produto")
    preco = st.number_input("Preço", min_value=0.0)
    estoque = st.number_input("Estoque", min_value=0)

    if st.button("Salvar Produto"):
        st.success("✅ Produto salvo com sucesso!")
        st.json({
            "nome": nome,
            "preco": preco,
            "estoque": estoque,
            "imagem_capturada": True
        })
else:
    st.warning("Use a câmera acima para capturar a imagem do produto.")
