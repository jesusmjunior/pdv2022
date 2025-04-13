# ORION PDV - VERSÃO FINAL UNIFICADA
# Módulo consolidado com base em app2.py + melhorias fuzzy estruturadas
# Regras aplicadas: α (variáveis organizadas), β (modularização), γ (correção), δ (boas práticas), ε (redução), θ (performance)

import streamlit as st
from datetime import datetime
import pandas as pd
from weasyprint import HTML
import base64
import io
import re

# --- Função: Gerar recibo HTML com suporte a PDF ---
def gerar_recibo_html(venda):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""
    <!DOCTYPE html>
    <html lang=\"pt-BR\">
    <head>
        <meta charset=\"UTF-8\">
        <title>Recibo de Venda - ORION PDV</title>
        <style>
            body {{ font-family: Arial; padding: 20px; max-width: 800px; margin: auto; }}
            .header {{ text-align: center; margin-bottom: 20px; }}
            .logo {{ font-size: 28px; font-weight: bold; color: #0066cc; }}
            .info, .total, .footer {{ margin-top: 20px; }}
            .items {{ width: 100%; border-collapse: collapse; }}
            .items th, .items td {{ border: 1px solid #ddd; padding: 8px; }}
            .items th {{ background-color: #f0f0f0; }}
            .product-cell {{ display: flex; align-items: center; }}
            .item-img {{ width: 40px; margin-right: 10px; }}
        </style>
    </head>
    <body>
        <div class=\"header\">
            <div class=\"logo\">ORION PDV</div>
            <div>Sistema de Ponto de Venda</div>
        </div>
        <div class=\"info\">
            <p><strong>Data:</strong> {venda['data']}</p>
            <p><strong>Cliente:</strong> {venda['cliente']}</p>
            <p><strong>Forma de Pagamento:</strong> {venda['forma_pgto']}</p>
        </div>
        <table class=\"items\">
            <thead>
                <tr>
                    <th>Produto</th><th>Qtd</th><th>Preço Unit.</th><th>Total</th>
                </tr>
            </thead>
            <tbody>
    """
    for item in venda['itens']:
        img_html = f"<img src='{item.get('foto', '')}' class='item-img'>" if item.get('foto') else ""
        html += f"""
        <tr>
            <td><div class='product-cell'>{img_html}{item['produto']} ({item['codigo_barras']})</div></td>
            <td>{item['quantidade']}</td>
            <td>R$ {item['preco_unit']:.2f}</td>
            <td>R$ {item['total']:.2f}</td>
        </tr>
        """
    html += f"""
            </tbody>
        </table>
        <div class=\"total\"><strong>Total da Venda:</strong> R$ {venda['total']:.2f}</div>
        <div class=\"footer\">Recibo gerado em: {timestamp}<br/>ORION PDV</div>
    </body></html>"""
    return html

# --- Função auxiliar: Exportar PDF ---
def gerar_pdf_do_recibo(venda):
    recibo_html = gerar_recibo_html(venda)
    pdf_bytes = HTML(string=recibo_html).write_pdf()
    return pdf_bytes

# --- Função de finalização com recibo e exportação PDF ---
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
    recibo_pdf = gerar_pdf_do_recibo(venda)
    st.download_button("📄 Baixar Recibo HTML", recibo_html, file_name="recibo.html")
    st.download_button("📄 Baixar Recibo PDF", recibo_pdf, file_name="recibo.pdf")
    st.session_state.carrinho = []
    st.rerun()

# --- Função de Painel Dinâmico com base em Vendas Registradas ---
def render_painel():
    st.title("📈 Painel Financeiro em Tempo Real")
    if 'vendas_db' not in st.session_state or not st.session_state.vendas_db:
        st.warning("Nenhuma venda registrada até o momento.")
        return
    vendas = st.session_state.vendas_db
    df = pd.DataFrame([{
        'DATA': v['data'],
        'CLIENTE': v['cliente'],
        'FORMA_PGTO': v['forma_pgto'],
        'TOTAL': v['total']
    } for v in vendas])
    df['DATA'] = pd.to_datetime(df['DATA'])
    st.subheader("Resumo por Forma de Pagamento")
    resumo_pgto = df.groupby("FORMA_PGTO")["TOTAL"].sum()
    st.bar_chart(resumo_pgto)
    st.subheader("Evolução Diária de Vendas")
    evolucao = df.groupby(df["DATA"].dt.date)["TOTAL"].sum()
    st.line_chart(evolucao)
    st.metric("Total Geral de Vendas", f"R$ {df['TOTAL'].sum():,.2f}")

# --- Função para extrair código de barras ---
def extrair_codigo_barras(texto):
    numeros = re.findall(r'\d+', texto)
    codigo_extraido = ''.join(numeros)
    if len(codigo_extraido) >= 8:
        return codigo_extraido
    return None

# --- Função de scanner básico via input manual ou OCR ---
def leitor_codigo_barras():
    st.subheader("📷 Leitor de Código de Barras")
    metodo = st.radio("Método de entrada:", ["Manual", "Texto OCR"])
    codigo_barras = ""
    if metodo == "Manual":
        codigo_barras = st.text_input("Digite o código de barras:")
    else:
        texto = st.text_area("Cole o texto extraído por OCR:")
        if st.button("Extrair código"):
            codigo_barras = extrair_codigo_barras(texto)
            if codigo_barras:
                st.success(f"Código extraído: {codigo_barras}")
            else:
                st.error("Código inválido.")
    return codigo_barras.strip()

# --- Cadastro de produto com gôndola ---
def cadastrar_produto():
    st.subheader("📦 Cadastro de Produto")
    codigo = leitor_codigo_barras()
    nome = st.text_input("Nome do Produto")
    grupo = st.text_input("Grupo / Categoria")
    marca = st.text_input("Marca")
    preco = st.number_input("Preço", min_value=0.01, step=0.01)
    estoque = st.number_input("Estoque", min_value=0, step=1)
    localizacao = st.text_input("Gôndola / Localização")
    foto = st.text_input("URL da Foto")
    if st.button("Salvar Produto"):
        if 'produtos_db' not in st.session_state:
            st.session_state.produtos_db = {}
        st.session_state.produtos_db[codigo] = {
            'nome': nome,
            'codigo_barras': codigo,
            'grupo': grupo,
            'marca': marca,
            'preco': preco,
            'estoque': estoque,
            'localizacao': localizacao,
            'foto': foto
        }
        st.success(f"Produto {nome} cadastrado com sucesso!")
