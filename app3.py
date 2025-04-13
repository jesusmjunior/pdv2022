
import streamlit as st
from PIL import Image
import numpy as np
import base64

def render_cadastro_produto():
    st.title("📦 Cadastro de Produto com Câmera")

    # Captura de imagem com câmera nativa
    img_file_buffer = st.camera_input("📷 Tire uma foto do produto")

    encoded_foto = ""
    if img_file_buffer is not None:
        image = Image.open(img_file_buffer)
        st.image(image, caption="Imagem capturada", use_column_width=True)
        foto_bytes = img_file_buffer.read()
        encoded_foto = base64.b64encode(foto_bytes).decode("utf-8")
    else:
        st.warning("⚠️ Use a câmera acima para capturar a imagem do produto.")

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
            "foto_base64": encoded_foto[:30] + "..." if encoded_foto else "nenhuma"
        })
