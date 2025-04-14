import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import hashlib
import uuid
import re
from PIL import Image

# ----------------------------- CONFIGURACAO BASICA ----------------------------- #
st.set_page_config(page_title="ORION PDV - Importador", layout="wide")

API_KEY = "AIzaSyAKibc0A3TerDdfQeZBLePxU01PbK_53Lw"
URLS = {
    "grupo": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=528868130&single=true&output=csv",
    "marcas": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=832596780&single=true&output=csv",
    "cliente": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1645177762&single=true&output=csv",
    "produto": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1506891785&single=true&output=csv",
    "pgto": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1061064660&single=true&output=csv",
    "venda": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1817416820&single=true&output=csv"
}
SPREADSHEET_ID = URLS["produto"].split("/d/e/")[1].split("/")[0]

# ----------------------------- ESTADO INICIAL ----------------------------- #
if 'produtos_db' not in st.session_state:
    st.session_state.produtos_db = {}

if 'vendas_db' not in st.session_state:
    st.session_state.vendas_db = []

if 'carrinho' not in st.session_state:
    st.session_state.carrinho = []

if 'clientes_db' not in st.session_state:
    st.session_state.clientes_db = []

if 'ultimo_codigo' not in st.session_state:
    st.session_state.ultimo_codigo = None

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = True

# ----------------------------- FUNCAO DE IMPORTACAO ----------------------------- #
def importar_produtos_csv():
    st.title("📥 Importar Produtos via Planilha")

    st.markdown("""
    1. Baixe o [modelo CSV](https://raw.githubusercontent.com/jesusmjunior/pdv2022/main/modelo_importacao.csv)
    2. Preencha com até 100 produtos
    3. Envie abaixo e confirme a importação

    **Colunas obrigatórias:**
    - nome
    - codigo_barras
    - grupo
    - marca
    - preco
    - estoque
    - foto (opcional)
    """)

    arquivo = st.file_uploader("📎 Enviar Arquivo CSV", type=["csv", "txt"])

    if arquivo:
        try:
            df = pd.read_csv(arquivo, sep=None, engine='python')
            df = df.fillna("")
            obrigatorias = ["nome", "codigo_barras", "grupo", "marca", "preco", "estoque"]
            if not all(col in df.columns for col in obrigatorias):
                st.error("⚠️ O arquivo está faltando colunas obrigatórias.")
                return

            st.success("Pré-visualização dos dados:")
            st.dataframe(df.head())

            if st.button("🚀 Importar para o Sistema"):
                novos_produtos = {}
                for _, row in df.iterrows():
                    codigo = str(row["codigo_barras"]).strip()
                    novos_produtos[codigo] = {
                        "nome": str(row["nome"]),
                        "codigo_barras": codigo,
                        "grupo": str(row["grupo"]),
                        "marca": str(row["marca"]),
                        "preco": float(row["preco"]),
                        "estoque": int(row["estoque"]),
                        "foto": str(row["foto"]) if row["foto"] else "https://via.placeholder.com/150"
                    }

                st.session_state.produtos_db.update(novos_produtos)
                st.success(f"{len(novos_produtos)} produtos importados com sucesso!")

                # Atualizar Google Sheets
                url = f"https://sheets.googleapis.com/v4/spreadsheets/{SPREADSHEET_ID}/values/Produtos!A1:append?valueInputOption=USER_ENTERED&key={API_KEY}"
                headers = {"Content-Type": "application/json"}

                valores = [["nome", "codigo_barras", "grupo", "marca", "preco", "estoque", "foto"]]
                for p in novos_produtos.values():
                    valores.append([p["nome"], p["codigo_barras"], p["grupo"], p["marca"], p["preco"], p["estoque"], p["foto"]])

                payload = {"values": valores}
                response = requests.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    st.success("Google Sheets atualizado com sucesso!")
                else:
                    st.warning(f"Erro ao enviar dados para Google Sheets: {response.status_code}")

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")

# ----------------------------- EXECUCAO ----------------------------- #
if __name__ == "__main__":
    importar_produtos_csv()
# Lousa 3 – Sessão, Autenticação e Utilitários de OCR e Códigos de Barras
import streamlit as st
import hashlib
import re
from datetime import datetime

# ----------------------------- USUÁRIOS ----------------------------- #
USUARIOS = {
    "admjesus": {
        "nome": "ADM Jesus",
        "senha_hash": hashlib.sha256("senha123".encode()).hexdigest()
    }
}

# ----------------------------- FUNÇÃO DE AUTENTICAÇÃO ----------------------------- #
def autenticar_usuario():
    st.title("🔐 Login - ORION ADM. JESUS MARTINS O. JR. PDV")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://github.com/jesusmjunior/pdv2022/blob/69ff7f9ecaa6209d10cec3ea589f803b56180c32/logo.webp", width=200)

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar", type="primary"):
        if usuario in USUARIOS:
            hash_inserida = hashlib.sha256(senha.encode()).hexdigest()
            if hash_inserida == USUARIOS[usuario]["senha_hash"]:
                st.session_state["autenticado"] = True
                st.session_state["usuario"] = usuario
                st.success("Login realizado com sucesso!")
                st.rerun()
            else:
                st.error("Senha incorreta.")
        else:
            st.error("Usuário não encontrado.")

# ----------------------------- EXTRAÇÃO DE CÓDIGO DE BARRAS ----------------------------- #
def extrair_codigo_barras(texto):
    numeros = re.findall(r'\d+', texto)
    codigo_extraido = ''.join(numeros)
    if len(codigo_extraido) >= 8:
        return codigo_extraido
    return None

# ----------------------------- RECONHECIMENTO DE TEXTO (OCR) ----------------------------- #
def reconhecer_texto_imagem():
    st.markdown("""
    <div style="padding: 10px; border: 1px solid #f63366; border-radius: 5px; margin-bottom: 10px; background-color: #fff5f5;">
        <h4 style="color: #f63366;">Como usar o reconhecimento de texto:</h4>
        <ol>
            <li>Tire uma foto clara do código de barras com seu celular</li>
            <li>Use um aplicativo de OCR como Google Lens para extrair os números</li>
            <li>Cole os números obtidos no campo abaixo</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    ocr_texto = st.text_area("Cole aqui o texto obtido pelo OCR ou os números do código de barras",
                             placeholder="Cole aqui o texto que contém os números do código de barras...",
                             height=100)

    codigo_barras = None

    if st.button("Extrair Código de Barras", type="primary") and ocr_texto:
        codigo_barras = extrair_codigo_barras(ocr_texto)

        if codigo_barras:
            st.success(f"Código de barras extraído: {codigo_barras}")
            st.session_state.ultimo_codigo = codigo_barras
        else:
            st.error("Não foi possível extrair um código de barras válido do texto fornecido.")

    return st.session_state.ultimo_codigo
# Lousa 4 – Leitor Assistido de Código de Barras e Exibição de Produto
import streamlit as st
from PIL import Image

# ----------------------------- LEITOR DE CÓDIGO DE BARRAS ----------------------------- #
def leitor_codigo_barras():
    st.subheader("📷 Scanner de Código de Barras")

    st.markdown("""
    <div style="padding: 20px; border: 1px solid #ccc; border-radius: 5px; margin-bottom: 20px;">
        <h4 style="color: #0066cc;">Scanner de Código de Barras Assistido</h4>
        <p>Para escanear um código de barras, você tem duas opções:</p>
        <ol>
            <li><strong>Via celular:</strong> Use Google Lens ou aplicativo de scanner, depois digite o código detectado</li>
            <li><strong>Via caixa de texto:</strong> Utilize a seção abaixo para colar texto com números e extrair o código automaticamente</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Digitar Código", "Extrair de Texto"])

    with tab1:
        col1, col2 = st.columns([3, 1])

        with col1:
            codigo_barras = st.text_input("Digite o código de barras:", 
                value=st.session_state.ultimo_codigo if st.session_state.ultimo_codigo else "",
                placeholder="Ex: 7891000315507")

        with col2:
            st.image("https://www.qr-code-generator.com/wp-content/themes/qr/images/barcode-generator-free.jpg", 
                     width=150, caption="Exemplo")

        if st.button("Usar Código", type="primary") and codigo_barras:
            st.session_state.ultimo_codigo = codigo_barras
            st.success(f"Código registrado: {codigo_barras}")

    with tab2:
        codigo_texto = reconhecer_texto_imagem()

    # Verificar e exibir produto relacionado
    codigo_selecionado = st.session_state.ultimo_codigo
    if codigo_selecionado and codigo_selecionado in st.session_state.produtos_db:
        produto = st.session_state.produtos_db[codigo_selecionado]
        st.success(f"Produto encontrado: {produto['nome']}")

        col1, col2 = st.columns([1, 2])
        with col1:
            if produto['foto']:
                st.image(produto['foto'], width=150)
        with col2:
            st.subheader(produto['nome'])
            st.write(f"**Preço:** R$ {produto['preco']:.2f}")
            st.write(f"**Estoque:** {produto['estoque']} unidades")

    elif codigo_selecionado:
        st.warning(f"Código {codigo_selecionado} não encontrado no cadastro.")

    return codigo_selecionado
# Lousa 6 – Cadastro de Produto com Leitor de Código Integrado
import streamlit as st
import pandas as pd

# ----------------------------- CADASTRO DE PRODUTO ----------------------------- #
def cadastro_produto():
    st.header("📦 Cadastro de Produto")

    # Tenta carregar dados das planilhas externas (grupos e marcas)
    try:
        grupo_df = pd.read_csv(URLS["grupo"])
        marcas_df = pd.read_csv(URLS["marcas"])
        grupos_lista = list(grupo_df["DESCRICAO"].dropna())
        marcas_lista = list(marcas_df["DESCRICAO"].dropna())
    except:
        grupos_lista = ["Alimentos", "Bebidas", "Limpeza", "Higiene", "Diversos"]
        marcas_lista = ["Nestlé", "Unilever", "P&G", "Ambev", "Outras"]

    usar_scanner = st.checkbox("Usar scanner de código de barras")

    if usar_scanner:
        st.info("Use o scanner para obter o código automaticamente")
        codigo_barras = leitor_codigo_barras()
        if codigo_barras:
            st.success(f"Código de barras capturado: {codigo_barras}")
    else:
        codigo_barras = st.text_input("Código de Barras")

    with st.form("form_produto"):
        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input("Nome do Produto")
            grupo = st.selectbox("Grupo/Categoria", grupos_lista)

        with col2:
            marca = st.selectbox("Marca", marcas_lista)
            preco = st.number_input("Preço", min_value=0.01, format="%.2f")
            estoque = st.number_input("Estoque", min_value=0)

        foto_url = st.text_input("URL da Imagem")

        if st.form_submit_button("Salvar Produto"):
            if nome and codigo_barras:
                st.session_state.produtos_db[codigo_barras] = {
                    "nome": nome,
                    "codigo_barras": codigo_barras,
                    "grupo": grupo,
                    "marca": marca,
                    "preco": preco,
                    "estoque": estoque,
                    "foto": foto_url if foto_url else "https://via.placeholder.com/150"
                }
                st.success("Produto cadastrado com sucesso!")
                st.session_state.ultimo_codigo = None
            else:
                st.error("Nome e código de barras são obrigatórios")

    # Visualização de produtos cadastrados
    st.subheader("📋 Produtos Cadastrados")
    if st.session_state.produtos_db:
        produtos_df = pd.DataFrame(st.session_state.produtos_db.values())
        st.dataframe(produtos_df[["nome", "codigo_barras", "grupo", "marca", "preco", "estoque"]])
    else:
        st.info("Nenhum produto cadastrado ainda")
# Lousa 7 – Cadastro de Cliente Integrado ao Google Sheets ou Sessão
import streamlit as st
import pandas as pd
import uuid

# ----------------------------- CADASTRO DE CLIENTE ----------------------------- #
def cadastro_cliente():
    st.header("👤 Cadastro de Cliente")

    # Tenta carregar clientes existentes da planilha
    try:
        clientes_df = pd.read_csv(URLS["cliente"])
        st.info(f"Dados externos disponíveis: {len(clientes_df)} clientes")
    except:
        clientes_df = pd.DataFrame()
        st.warning("Não foi possível carregar dados externos de clientes")

    with st.form("form_cliente"):
        col1, col2 = st.columns(2)

        with col1:
            nome = st.text_input("Nome Completo")
            documento = st.text_input("CPF/CNPJ")
            email = st.text_input("Email")

        with col2:
            telefone = st.text_input("Telefone")
            endereco = st.text_input("Endereço")
            cidade = st.text_input("Cidade")

        if st.form_submit_button("Salvar Cliente"):
            novo_cliente = {
                "ID": str(uuid.uuid4())[:8],
                "NOME": nome,
                "DOCUMENTO": documento,
                "EMAIL": email,
                "TELEFONE": telefone,
                "ENDERECO": endereco,
                "CIDADE": cidade
            }
            st.session_state.clientes_db.append(novo_cliente)
            st.success("Cliente cadastrado com sucesso!")

    st.subheader("📋 Clientes Cadastrados")
    if st.session_state.clientes_db:
        st.dataframe(pd.DataFrame(st.session_state.clientes_db))
    elif not clientes_df.empty:
        st.dataframe(clientes_df)
    else:
        st.info("Nenhum cliente cadastrado")
# Lousa 8 – Painel Financeiro com Filtros, Métricas e Gráficos
import streamlit as st
import pandas as pd
from datetime import datetime

# ----------------------------- PAINEL FINANCEIRO ----------------------------- #
def painel_financeiro():
    st.header("📊 Painel Financeiro")

    try:
        venda_ext_df = pd.read_csv(URLS["venda"])
        venda_ext_df["DATA"] = pd.to_datetime(venda_ext_df["DATA"], errors="coerce")
        st.success(f"Dados externos carregados: {len(venda_ext_df)} vendas")
    except:
        venda_ext_df = pd.DataFrame()
        st.warning("Não foi possível carregar dados externos de vendas")

    vendas_combinadas = st.session_state.vendas_db.copy()

    # Transformar as vendas em um DataFrame
    vendas_df = []
    for venda in vendas_combinadas:
        vendas_df.append({
            "id": venda.get("id", ""),
            "data": venda.get("data", ""),
            "cliente": venda.get("cliente", ""),
            "forma_pgto": venda.get("forma_pgto", ""),
            "total": venda.get("total", 0)
        })

    vendas_df = pd.DataFrame(vendas_df)

    # Converter datas
    vendas_df["data"] = pd.to_datetime(vendas_df["data"], errors="coerce")

    # Métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Vendas", f"{len(vendas_df)}")
    with col2:
        st.metric("Faturamento Total", f"R$ {vendas_df['total'].sum():.2f}")
    with col3:
        st.metric("Ticket Médio", f"R$ {vendas_df['total'].mean():.2f}")

    # Filtros
    st.subheader("Filtros")
    col1, col2 = st.columns(2)
    hoje = datetime.now().date()
    with col1:
        data_inicio = st.date_input("Data Inicial", hoje - pd.Timedelta(days=30), max_value=hoje)
    with col2:
        data_fim = st.date_input("Data Final", hoje, max_value=hoje)

    mask = (vendas_df["data"].dt.date >= data_inicio) & (vendas_df["data"].dt.date <= data_fim)
    vendas_filtradas = vendas_df[mask]

    if vendas_filtradas.empty:
        st.warning("Nenhuma venda no período selecionado")
        return

    st.subheader("📈 Análise de Vendas")
    vendas_por_dia = vendas_filtradas.groupby(vendas_filtradas["data"].dt.date)["total"].sum().reset_index()
    vendas_por_dia.columns = ["data", "total"]
    st.line_chart(vendas_por_dia.set_index("data"))

    st.subheader("💳 Vendas por Forma de Pagamento")
    vendas_por_pgto = vendas_filtradas.groupby("forma_pgto")["total"].sum().reset_index()
    st.bar_chart(vendas_por_pgto.set_index("forma_pgto"))

    st.subheader("🧾 Lista de Vendas no Período")
    st.dataframe(vendas_filtradas[["id", "data", "cliente", "forma_pgto", "total"]])
# Lousa 8 – Painel Financeiro com Filtros, Métricas e Gráficos
import streamlit as st
import pandas as pd
from datetime import datetime

# ----------------------------- PAINEL FINANCEIRO ----------------------------- #
def painel_financeiro():
    st.header("📊 Painel Financeiro")

    try:
        venda_ext_df = pd.read_csv(URLS["venda"])
        venda_ext_df["DATA"] = pd.to_datetime(venda_ext_df["DATA"], errors="coerce")
        st.success(f"Dados externos carregados: {len(venda_ext_df)} vendas")
    except:
        venda_ext_df = pd.DataFrame()
        st.warning("Não foi possível carregar dados externos de vendas")

    vendas_combinadas = st.session_state.vendas_db.copy()

    # Transformar as vendas em um DataFrame
    vendas_df = []
    for venda in vendas_combinadas:
        vendas_df.append({
            "id": venda.get("id", ""),
            "data": venda.get("data", ""),
            "cliente": venda.get("cliente", ""),
            "forma_pgto": venda.get("forma_pgto", ""),
            "total": venda.get("total", 0)
        })

    vendas_df = pd.DataFrame(vendas_df)

    # Converter datas
    vendas_df["data"] = pd.to_datetime(vendas_df["data"], errors="coerce")

    # Métricas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Vendas", f"{len(vendas_df)}")
    with col2:
        st.metric("Faturamento Total", f"R$ {vendas_df['total'].sum():.2f}")
    with col3:
        st.metric("Ticket Médio", f"R$ {vendas_df['total'].mean():.2f}")

    # Filtros
    st.subheader("Filtros")
    col1, col2 = st.columns(2)
    hoje = datetime.now().date()
    with col1:
        data_inicio = st.date_input("Data Inicial", hoje - pd.Timedelta(days=30), max_value=hoje)
    with col2:
        data_fim = st.date_input("Data Final", hoje, max_value=hoje)

    mask = (vendas_df["data"].dt.date >= data_inicio) & (vendas_df["data"].dt.date <= data_fim)
    vendas_filtradas = vendas_df[mask]

    if vendas_filtradas.empty:
        st.warning("Nenhuma venda no período selecionado")
        return

    st.subheader("📈 Análise de Vendas")
    vendas_por_dia = vendas_filtradas.groupby(vendas_filtradas["data"].dt.date)["total"].sum().reset_index()
    vendas_por_dia.columns = ["data", "total"]
    st.line_chart(vendas_por_dia.set_index("data"))

    st.subheader("💳 Vendas por Forma de Pagamento")
    vendas_por_pgto = vendas_filtradas.groupby("forma_pgto")["total"].sum().reset_index()
    st.bar_chart(vendas_por_pgto.set_index("forma_pgto"))

    st.subheader("🧾 Lista de Vendas no Período")
    st.dataframe(vendas_filtradas[["id", "data", "cliente", "forma_pgto", "total"]])
# Lousa 11 – Sidebar, Navegação e Função Principal do App
import streamlit as st
from datetime import datetime

# ----------------------------- SIDEBAR ----------------------------- #
def sidebar():
    with st.sidebar:
        st.image("https://i.imgur.com/Ka8kNST.png", width=200)
        st.title("ORION PDV")

        pagina = st.selectbox(
            "Menu Principal",
            [
                "🧾 Registrar Venda",
                "📦 Cadastrar Produto",
                "👤 Cadastrar Cliente",
                "📊 Painel Financeiro",
                "📜 Histórico de Vendas",
                "🗃️ Gerenciar Estoque",
                "📥 Importar Produtos via CSV",
                "⚙️ Configurações",
                "ℹ️ Sobre"
            ]
        )

        st.divider()
        st.write(f"📅 {datetime.now().strftime('%d/%m/%Y')}")
        st.write(f"🕒 {datetime.now().strftime('%H:%M:%S')}")

        if "usuario" in st.session_state:
            st.write(f"👤 Usuário: {st.session_state['usuario']}")
            if st.button("Sair", type="primary"):
                st.session_state.clear()
                st.rerun()

    return pagina

# ----------------------------- MAIN ----------------------------- #
def main():
    if "autenticado" not in st.session_state or not st.session_state.autenticado:
        autenticar_usuario()
        return

    pagina = sidebar()

    if pagina == "🧾 Registrar Venda":
        registrar_venda()
    elif pagina == "📦 Cadastrar Produto":
        cadastro_produto()
    elif pagina == "👤 Cadastrar Cliente":
        cadastro_cliente()
    elif pagina == "📊 Painel Financeiro":
        painel_financeiro()
    elif pagina == "📜 Histórico de Vendas":
        historico_vendas()
    elif pagina == "🗃️ Gerenciar Estoque":
        gerenciar_estoque()
    elif pagina == "📥 Importar Produtos via CSV":
        importar_produtos_csv()
    elif pagina == "⚙️ Configurações":
        configuracoes_sistema()
    elif pagina == "ℹ️ Sobre":
        sobre()

# ----------------------------- EXECUÇÃO ----------------------------- #
if __name__ == "__main__":
    main()
