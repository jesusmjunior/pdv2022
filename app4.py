# ORION PDV - VERSÃO FINAL UNIFICADA
# Módulo consolidado com base em app2.py + melhorias fuzzy estruturadas
# Regras aplicadas: α (variáveis organizadas), β (modularização), γ (correção), δ (boas práticas), ε (redução), θ (performance)

import streamlit as st
from datetime import datetime
import pandas as pd
import base64
import io
import re

# --- Geração manual de PDF sem usar weasyprint (substituto básico) ---
def gerar_recibo_html(venda):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""
    <!DOCTYPE html>
    <html lang='pt-BR'>
    <head>
        <meta charset='UTF-8'>
        <title>Recibo de Venda</title>
        <style>
            body {{ font-family: Arial; padding: 20px; }}
            .logo {{ font-size: 24px; font-weight: bold; color: #0056b3; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; }}
            th {{ background: #f0f0f0; }}
            .total {{ font-weight: bold; text-align: right; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class='logo'>ORION PDV - Recibo</div>
        <p><strong>Data:</strong> {venda['data']}</p>
        <p><strong>Cliente:</strong> {venda['cliente']}</p>
        <p><strong>Pagamento:</strong> {venda['forma_pgto']}</p>
        <table>
            <tr><th>Produto</th><th>Qtd</th><th>Unitário</th><th>Total</th></tr>
    """
    for item in venda['itens']:
        html += f"<tr><td>{item['produto']}</td><td>{item['quantidade']}</td><td>R$ {item['preco_unit']:.2f}</td><td>R$ {item['total']:.2f}</td></tr>"
    html += f"""
        </table>
        <p class='total'>Total: R$ {venda['total']:.2f}</p>
        <p style='font-size:12px;'>Gerado em: {timestamp}</p>
    </body></html>
    """
    return html

def download_html_as_file(html_content, filename):
    b64 = base64.b64encode(html_content.encode()).decode()
    href = f'<a href="data:text/html;base64,{b64}" download="{filename}">📄 Baixar Recibo HTML</a>'
    st.markdown(href, unsafe_allow_html=True)

# --- Substituta da finalização com PDF (versão compatível com Streamlit Cloud) ---
def finalizar_venda(cliente, forma_pgto, carrinho):
    total = sum(item['total'] for item in carrinho)
    venda = {
        "cliente": cliente,
        "forma_pgto": forma_pgto,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": total,
        "itens": carrinho
    }
    if 'vendas_db' not in st.session_state:
        st.session_state.vendas_db = []
    st.session_state.vendas_db.append(venda)
    st.success("Venda registrada com sucesso!")
    st.json(venda)
    recibo_html = gerar_recibo_html(venda)
    download_html_as_file(recibo_html, "recibo.html")
    st.session_state.carrinho = []
    st.rerun()

# --- Função de registro de venda com carrinho integrado ---
def registrar_venda():
    st.subheader("🧾 Registro de Venda")

    if 'produtos_db' not in st.session_state:
        st.session_state.produtos_db = {}

    if 'carrinho' not in st.session_state:
        st.session_state.carrinho = []

    codigo = leitor_codigo_barras()
    qtd = st.number_input("Quantidade", min_value=1, value=1, step=1)

    if st.button("Adicionar ao Carrinho") and codigo in st.session_state.produtos_db:
        produto = st.session_state.produtos_db[codigo]
        item = {
            'codigo_barras': codigo,
            'produto': produto['nome'],
            'quantidade': qtd,
            'preco_unit': produto['preco'],
            'total': qtd * produto['preco'],
            'foto': produto.get('foto')
        }
        st.session_state.carrinho.append(item)
        st.success(f"{produto['nome']} adicionado ao carrinho")

    if st.session_state.carrinho:
        st.subheader("Carrinho")
        total = 0
        for i, item in enumerate(st.session_state.carrinho):
            cols = st.columns([1, 3, 1, 1])
            with cols[0]:
                if item['foto']:
                    st.image(item['foto'], width=60)
            with cols[1]:
                st.write(f"**{item['produto']}**\nCódigo: {item['codigo_barras']}")
            with cols[2]:
                st.write(f"Qtd: {item['quantidade']}")
            with cols[3]:
                st.write(f"R$ {item['total']:.2f}")
            total += item['total']
        st.write(f"## Total: R$ {total:.2f}")

        st.markdown("---")
        cliente = st.text_input("Nome do Cliente")
        forma_pgto = st.selectbox("Forma de Pagamento", ["Dinheiro", "Cartão", "PIX"])

        if st.button("Finalizar Venda"):
            finalizar_venda(cliente, forma_pgto, st.session_state.carrinho)

# --- Função principal atualizada ---
def main():
    st.title("ORION PDV - Sistema de Ponto de Venda")
    menu = st.sidebar.selectbox("Menu", ["Registrar Venda", "Painel", "Cadastro Produto"])
    if menu == "Registrar Venda":
        registrar_venda()
    elif menu == "Painel":
        render_painel()
    elif menu == "Cadastro Produto":
        cadastrar_produto()

if __name__ == "__main__":
    main()
