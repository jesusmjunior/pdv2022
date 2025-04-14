# Lousa 1 - Módulo de Configuração e Integração com Google Vision
import streamlit as st
import pandas as pd
import requests
import base64
import json
from datetime import datetime
import uuid
import hashlib
from PIL import Image
import io

# Configuração da Página
st.set_page_config(page_title="ORION PDV I.A. 🔐 OCR via Google Vision", layout="wide")

# Carregamento da chave do serviço (deve estar no mesmo diretório)
with open("zeta-bonbon-424022-b5-691a49c9946f.json") as f:
    google_vision_credentials = json.load(f)

# URLS das planilhas
URLS = {
    "grupo": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=528868130&single=true&output=csv",
    "marcas": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=832596780&single=true&output=csv",
    "cliente": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1645177762&single=true&output=csv",
    "produto": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1506891785&single=true&output=csv",
    "pgto": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1061064660&single=true&output=csv",
    "venda": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS0r3XE4DpzlYJjZwjc2c_pW_K3euooN9caPedtSq-nH_aEPnvx1jrcd9t0Yhg8fqXfR3j5jM2OyUQQ/pub?gid=1817416820&single=true&output=csv"
}

# Carregamento OCR via Google Vision API
def extrair_texto_google_vision(imagem_pil):
    # Converte imagem para base64
    buffered = io.BytesIO()
    imagem_pil.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()

    payload = {
        "requests": [{
            "image": {"content": img_base64},
            "features": [{"type": "TEXT_DETECTION"}]
        }]
    }

    response = requests.post(
        url="https://vision.googleapis.com/v1/images:annotate",
        params={"key": google_vision_credentials["private_key_id"]},  # alternativo: chave no token
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload)
    )

    try:
        data = response.json()
        texto = data['responses'][0]['textAnnotations'][0]['description']
        return texto
    except Exception as e:
        st.error("Erro ao processar OCR com Google Vision.")
        return ""
# Lousa 2 - Upload de documento + extração OCR integrada
st.header("📤 Upload de Documento - Nota Fiscal ou Cupom")
st.markdown("""
<div style="background-color:#f9f9f9; padding:15px; border-left:4px solid #2196f3; margin-bottom:20px;">
    <b>Instruções:</b><br>
    1. Faça upload de uma imagem (JPG/PNG)<br>
    2. O sistema usará <i>Google Vision</i> para extrair o texto<br>
    3. Verifique e edite os dados extraídos conforme necessário
</div>
""", unsafe_allow_html=True)

# Upload
imagem_upload = st.file_uploader("📎 Enviar Imagem da Nota/Cupom", type=["jpg", "jpeg", "png"])

texto_extraido = ""
img_preview = None

if imagem_upload:
    try:
        img_preview = Image.open(imagem_upload)
        st.image(img_preview, caption="📷 Pré-visualização da Imagem", use_column_width=True)

        with st.spinner("🔍 Extraindo texto via Google Vision..."):
            texto_extraido = extrair_texto_google_vision(img_preview)

        if texto_extraido:
            st.success("✅ Texto extraído com sucesso!")
            with st.expander("📝 Texto OCR Extraído"):
                st.text_area("Conteúdo Detectado:", value=texto_extraido, height=250)

        else:
            st.warning("⚠️ Nenhum texto detectado na imagem.")
    except Exception as e:
        st.error("Erro ao processar imagem. Verifique se está em formato válido.")
# Lousa 3 - Análise do Texto OCR Extraído (DANFE ou CUPOM)
def analisar_danfe(texto):
    produtos = []
    # Expressão regular para blocos de produto (ex: notas fiscais padrão)
    padrao = re.findall(r"\d+\s+\d+\)?\s+((\w+\s?)+)\s+\d+\s+\w+\s+(\d+)\s+([\d,]+)\s+([\d,]+)", texto)

    for item in padrao:
        try:
            descricao = item[0].strip()
            quantidade = int(item[2])
            valor_unitario = float(item[3].replace('.', '').replace(',', '.'))
            valor_total = float(item[4].replace('.', '').replace(',', '.'))

            # Tentar localizar código de barras
            codigo_barras = re.search(r'C[ÓO]D[\s:]*(BARRAS)?[:\s]*(\d+)', texto, re.IGNORECASE)
            codigo = codigo_barras.group(2) if codigo_barras else str(uuid.uuid4())[:13]

            produtos.append({
                "descricao": descricao,
                "quantidade": quantidade,
                "valor_unitario": valor_unitario,
                "valor_total": valor_total,
                "codigo_barras": codigo
            })
        except Exception as e:
            continue
    return produtos

def analisar_cupom_fiscal(texto):
    produtos = []
    # Tentativa 1: padrão com código, descrição, quantidade, valor unit
    linhas = re.findall(r'(\d{3})\s+(\d+)\s+(.+?)\s+(\d+)UN\s*X\s*(\d+,\d+)', texto)

    if not linhas:
        # Tentativa 2: formato alternativo
        linhas = re.findall(r'(\d+)\s+(.+?)\s+(\d+)xX\s*(\d+,\d+)', texto)

    for item in linhas:
        try:
            if len(item) == 5:
                descricao = item[2].strip()
                quantidade = int(item[3])
                valor_unitario = float(item[4].replace(',', '.'))
                codigo = item[1]
            else:
                descricao = item[1].strip()
                quantidade = int(item[2])
                valor_unitario = float(item[3].replace(',', '.'))
                codigo = str(uuid.uuid4())[:13]

            produtos.append({
                "descricao": descricao,
                "quantidade": quantidade,
                "valor_unitario": valor_unitario,
                "valor_total": round(quantidade * valor_unitario, 2),
                "codigo_barras": codigo
            })
        except:
            continue
    return produtos
# Lousa 4 - Interface para exibição e confirmação da importação
def interface_importar_produtos(texto_extraido, tipo_documento):
    st.subheader("📦 Produtos Detectados")
    produtos = []

    if tipo_documento in ["PDF", "Imagem de Nota"]:
        produtos = analisar_danfe(texto_extraido)
    elif tipo_documento == "Cupom":
        produtos = analisar_cupom_fiscal(texto_extraido)

    if not produtos:
        st.warning("Nenhum produto detectado no documento.")
        return

    st.success(f"{len(produtos)} produtos identificados com sucesso!")

    # Preview dos dados extraídos
    df_preview = pd.DataFrame(produtos)
    st.dataframe(df_preview)

    col1, col2 = st.columns(2)

    with col1:
        margem = st.number_input(
            "Margem de Lucro (%)",
            min_value=0.0,
            max_value=500.0,
            value=30.0,
            step=5.0
        )

    with col2:
        preco_exemplo = produtos[0]["valor_unitario"] * (1 + margem / 100)
        st.markdown(f"💡 Exemplo: Preço venda = R$ **{preco_exemplo:.2f}**")

    if st.button("✅ Importar Produtos"):
        total_importados = importar_para_estoque(produtos, margem)
        st.success(f"{total_importados} produtos importados ao estoque.")
        st.rerun()
# Lousa 5 - Função de Importação para Estoque com lógica fuzzy
def importar_para_estoque(produtos_extraidos, margem_lucro):
    if 'produtos_db' not in st.session_state:
        st.session_state.produtos_db = {}

    total_importados = 0

    for p in produtos_extraidos:
        codigo = p["codigo_barras"]

        # Se código já existe, atualiza estoque
        if codigo in st.session_state.produtos_db:
            st.session_state.produtos_db[codigo]["estoque"] += p["quantidade"]
        else:
            # Se código ausente ou inválido, gera UUID parcial
            if not codigo or codigo == "SEM_CODIGO":
                codigo = str(uuid.uuid4())[:13]

            preco_venda = p["valor_unitario"] * (1 + margem_lucro / 100)

            st.session_state.produtos_db[codigo] = {
                "nome": p["descricao"],
                "codigo_barras": codigo,
                "grupo": "Importado",
                "marca": "Desconhecida",
                "preco": round(preco_venda, 2),
                "preco_custo": p["valor_unitario"],
                "margem_lucro": margem_lucro,
                "estoque": p["quantidade"],
                "foto": "https://via.placeholder.com/150"
            }

        total_importados += 1

    return total_importados
# Lousa 6 - Scanner OCR + Entrada Manual com Preview
def leitor_codigo_barras():
    st.subheader("📷 Leitor Inteligente de Código de Barras")

    tab1, tab2 = st.tabs(["📸 Escanear Imagem", "⌨️ Digitar Código"])

    codigo_extraido = None

    with tab1:
        imagem = st.file_uploader("📎 Enviar imagem com código de barras", type=["jpg", "jpeg", "png"])
        if imagem:
            try:
                imagem_pil = Image.open(imagem)
                st.image(imagem_pil, width=300)
                with st.spinner("Extraindo via Google Vision..."):
                    texto = extrair_texto_google_vision(imagem_pil)
                codigo_extraido = extrair_codigo_barras(texto)
                if codigo_extraido:
                    st.success(f"Código detectado: {codigo_extraido}")
                else:
                    st.warning("Nenhum código extraído. Tente digitar manualmente.")
            except Exception as e:
                st.error("Erro ao processar a imagem.")

    with tab2:
        codigo_manual = st.text_input("Digite o código de barras manualmente")
        if codigo_manual and len(codigo_manual) >= 8:
            codigo_extraido = codigo_manual
            st.success(f"Código manual: {codigo_manual}")

    # Atualizar estado global
    if codigo_extraido:
        st.session_state.ultimo_codigo = codigo_extraido

        # Se estiver no banco, mostrar produto
        if codigo_extraido in st.session_state.get("produtos_db", {}):
            produto = st.session_state.produtos_db[codigo_extraido]
            st.info(f"Produto: {produto['nome']}")
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(produto['foto'], width=150)
            with col2:
                st.write(f"**Preço:** R$ {produto['preco']:.2f}")
                st.write(f"**Estoque:** {produto['estoque']} unidades")
        else:
            st.warning("⚠️ Código ainda não cadastrado.")
    return st.session_state.get("ultimo_codigo", None)
# Lousa 7 - Registro de Venda via Busca ou Scanner
def registrar_venda():
    st.header("🧾 Nova Venda")

    abas = st.tabs(["🔍 Buscar Produto", "📷 Scanner"])

    with abas[0]:
        termo = st.text_input("Digite o nome ou código do produto")
        resultados = []
        if termo:
            for cod, prod in st.session_state.produtos_db.items():
                if termo.lower() in prod["nome"].lower() or termo in prod["codigo_barras"]:
                    resultados.append(prod)

        if resultados:
            for prod in resultados:
                with st.container():
                    st.image(prod["foto"], width=150)
                    st.write(f"**{prod['nome']}** - R$ {prod['preco']:.2f}")
                    qtd = st.number_input(
                        f"Qtd ({prod['codigo_barras']})", min_value=1, max_value=prod["estoque"], step=1, key=f"qtd_{prod['codigo_barras']}"
                    )
                    if st.button(f"Adicionar {prod['nome']}", key=f"add_{prod['codigo_barras']}"):
                        adicionar_ao_carrinho(prod['codigo_barras'], qtd)

    with abas[1]:
        cod_lido = leitor_codigo_barras()
        if cod_lido and cod_lido in st.session_state.produtos_db:
            prod = st.session_state.produtos_db[cod_lido]
            qtd = st.number_input(f"Qtd {prod['nome']}", min_value=1, max_value=prod["estoque"], step=1)
            if st.button("Adicionar ao Carrinho", key="add_scan"):
                adicionar_ao_carrinho(cod_lido, qtd)

    # Carrinho
    st.subheader("🛒 Carrinho")
    if not st.session_state.carrinho:
        st.info("Carrinho vazio")
    else:
        total = 0
        for i, item in enumerate(st.session_state.carrinho):
            st.write(f"{item['quantidade']}x {item['produto']} - R$ {item['total']:.2f}")
            total += item["total"]
            if st.button("❌ Remover", key=f"del_{i}"):
                remover_do_carrinho(i)

        st.metric("Total", f"R$ {total:.2f}")
        cliente = st.text_input("Cliente", value="Consumidor Final")
        pgto = st.selectbox("Forma de Pagamento", ["Dinheiro", "Pix", "Cartão", "Crediário"])
        if st.button("💳 Finalizar Venda"):
            venda_id = str(uuid.uuid4())[:6]
            registrar_venda_db(cliente, pgto, total)
            st.success(f"Venda {venda_id} concluída com sucesso!")
# Lousa 8 - Funções auxiliares de venda
def adicionar_ao_carrinho(codigo_barras, qtd):
    produto = st.session_state.produtos_db[codigo_barras]
    if produto["estoque"] >= qtd:
        total = round(produto["preco"] * qtd, 2)
        st.session_state.carrinho.append({
            "codigo_barras": codigo_barras,
            "produto": produto["nome"],
            "quantidade": qtd,
            "preco_unit": produto["preco"],
            "total": total
        })
        st.session_state.produtos_db[codigo_barras]["estoque"] -= qtd
        st.success(f"{qtd}x {produto['nome']} adicionado(s) ao carrinho.")
    else:
        st.error("Estoque insuficiente.")

def remover_do_carrinho(index):
    item = st.session_state.carrinho[index]
    st.session_state.produtos_db[item["codigo_barras"]]["estoque"] += item["quantidade"]
    st.session_state.carrinho.pop(index)
    st.rerun()

def registrar_venda_db(cliente, forma_pgto, total):
    venda_id = str(uuid.uuid4())[:8].upper()
    nova_venda = {
        "id": venda_id,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cliente": cliente,
        "forma_pgto": forma_pgto,
        "itens": st.session_state.carrinho.copy(),
        "total": total
    }
    st.session_state.vendas_db.append(nova_venda)
    recibo = gerar_recibo_html(nova_venda)
    st.download_button("📄 Baixar Recibo", recibo, file_name=f"recibo_{venda_id}.html", mime="text/html")
    st.session_state.carrinho = []

def gerar_recibo_html(venda):
    html = f"""
    <!DOCTYPE html><html><head><meta charset="UTF-8"><title>Recibo</title>
    <style>
        body {{ font-family: Arial; max-width:600px; margin:auto; padding:20px; }}
        .header {{ text-align:center; margin-bottom:20px; }}
        .linha {{ border-top:1px dashed #000; margin:10px 0; }}
        .total {{ font-weight:bold; font-size:1.2em; }}
        table {{ width:100%; border-collapse:collapse; margin:15px 0; }}
        th, td {{ padding:8px; text-align:left; border-bottom:1px solid #ddd; }}
        th {{ background-color:#f2f2f2; }}
        .footer {{ text-align:center; margin-top:30px; font-size:0.9em; color:#555; }}
    </style></head><body>
    <div class="header">
        <h2>ORION PDV</h2><h3>RECIBO ELETRÔNICO</h3>
    </div>
    <div class="linha"></div>
    <p><strong>Data:</strong> {venda['data']}</p>
    <p><strong>Cliente:</strong> {venda['cliente']}</p>
    <p><strong>Pagamento:</strong> {venda['forma_pgto']}</p>
    <div class="linha"></div>
    <table><thead><tr><th>Produto</th><th>Qtd</th><th>Unit</th><th>Total</th></tr></thead><tbody>
    """
    for item in venda["itens"]:
        html += f"""
        <tr><td>{item['produto']}</td><td>{item['quantidade']}</td>
        <td>R$ {item['preco_unit']:.2f}</td><td>R$ {item['total']:.2f}</td></tr>"""
    html += f"""
    </tbody></table>
    <div class="linha"></div>
    <p class="total">Total: R$ {venda['total']:.2f}</p>
    <div class="linha"></div>
    <div class="footer">
        <p>Obrigado pela preferência!</p>
        <p><small>Gerado em: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</small></p>
    </div>
    </body></html>
    """
    return html
# Lousa 9 - Módulo de Cadastro de Produto com scanner e integração Sheets
def cadastro_produto():
    st.header("📦 Cadastro de Produto")

    # Carregar dados externos
    try:
        grupo_df = pd.read_csv(URLS["grupo"])
        grupos = list(grupo_df["DESCRICAO"].dropna())
    except:
        grupos = ["Alimentos", "Higiene", "Limpeza", "Diversos"]

    try:
        marca_df = pd.read_csv(URLS["marcas"])
        marcas = list(marca_df["DESCRICAO"].dropna())
    except:
        marcas = ["Outras", "Genérica", "Não Informada"]

    usar_scanner = st.checkbox("📷 Usar scanner para obter o código")
    if usar_scanner:
        st.info("Escaneie o código do produto")
        cod_lido = leitor_codigo_barras()
    else:
        cod_lido = ""

    with st.form("form_produto"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Produto")
            codigo = st.text_input("Código de Barras", value=cod_lido or st.session_state.get("ultimo_codigo", ""))
            grupo = st.selectbox("Grupo", grupos)
        with col2:
            preco = st.number_input("Preço de Venda", min_value=0.01, step=0.01)
            estoque = st.number_input("Estoque Inicial", min_value=0)
            marca = st.selectbox("Marca", marcas)

        foto_url = st.text_input("URL da Imagem do Produto")

        if st.form_submit_button("Salvar Produto"):
            if nome and codigo:
                st.session_state.produtos_db[codigo] = {
                    "nome": nome,
                    "codigo_barras": codigo,
                    "grupo": grupo,
                    "marca": marca,
                    "preco": preco,
                    "estoque": estoque,
                    "foto": foto_url or "https://via.placeholder.com/150"
                }
                st.success("Produto cadastrado com sucesso!")
                st.session_state.ultimo_codigo = None
            else:
                st.error("⚠️ Nome e código de barras são obrigatórios.")

    # Tabela de produtos cadastrados
    st.subheader("📋 Produtos no Sistema")
    produtos_df = pd.DataFrame(st.session_state.produtos_db.values())
    st.dataframe(produtos_df[["nome", "codigo_barras", "preco", "estoque"]])
# Lousa 10 - Módulo de Cadastro de Clientes
def cadastro_cliente():
    st.header("👤 Cadastro de Cliente")

    # Tentativa de leitura do banco externo
    try:
        clientes_ext = pd.read_csv(URLS["cliente"])
        st.success(f"✅ {len(clientes_ext)} clientes carregados do Google Sheets")
    except:
        clientes_ext = pd.DataFrame()
        st.warning("⚠️ Não foi possível carregar os dados externos")

    with st.form("form_cliente"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo")
            doc = st.text_input("CPF ou CNPJ")
            email = st.text_input("Email")
        with col2:
            tel = st.text_input("Telefone")
            end = st.text_input("Endereço")
            cidade = st.text_input("Cidade")

        if st.form_submit_button("Salvar Cliente"):
            novo = {
                "ID": str(uuid.uuid4())[:8],
                "NOME": nome,
                "DOCUMENTO": doc,
                "EMAIL": email,
                "TELEFONE": tel,
                "ENDERECO": end,
                "CIDADE": cidade
            }
            if 'clientes_db' not in st.session_state:
                st.session_state.clientes_db = []
            st.session_state.clientes_db.append(novo)
            st.success("🎉 Cliente cadastrado!")

    st.subheader("📋 Lista de Clientes")
    if st.session_state.get("clientes_db"):
        st.dataframe(pd.DataFrame(st.session_state.clientes_db))
    elif not clientes_ext.empty:
        st.dataframe(clientes_ext[["NOME", "DOCUMENTO", "EMAIL", "CIDADE"]])
    else:
        st.info("Nenhum cliente disponível.")
# Lousa 11 - Painel Financeiro com dados externos e internos
def painel_financeiro():
    st.header("📊 Painel Financeiro")

    vendas_combinadas = []
    try:
        df_ext = pd.read_csv(URLS["venda"])
        df_ext["DATA"] = pd.to_datetime(df_ext["DATA"], errors="coerce")
        vendas_combinadas.extend(df_ext.to_dict(orient="records"))
        st.success(f"✅ {len(df_ext)} vendas externas carregadas")
    except:
        st.warning("⚠️ Dados externos não acessíveis")

    vendas_combinadas.extend(st.session_state.vendas_db)

    if not vendas_combinadas:
        st.info("Nenhuma venda disponível para análise.")
        return

    vendas_df = pd.DataFrame([
        {
            "ID": v.get("id", ""),
            "DATA": pd.to_datetime(v.get("data", ""), errors="coerce"),
            "CLIENTE": v.get("cliente", ""),
            "PGTO": v.get("forma_pgto", ""),
            "TOTAL": v.get("total", 0)
        } for v in vendas_combinadas
    ])

    vendas_df.dropna(subset=["DATA"], inplace=True)

    total_vendas = len(vendas_df)
    soma_total = vendas_df["TOTAL"].sum()
    ticket_medio = vendas_df["TOTAL"].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric("🧾 Total de Vendas", f"{total_vendas}")
    col2.metric("💰 Faturamento", f"R$ {soma_total:.2f}")
    col3.metric("📈 Ticket Médio", f"R$ {ticket_medio:.2f}")

    with st.expander("📅 Vendas Registradas"):
        st.dataframe(vendas_df.sort_values("DATA", ascending=False).reset_index(drop=True))
# Lousa 12 - Módulo de Autenticação e Controle de Sessão
USUARIOS = {
    "admjesus": {
        "nome": "Jesus Martins",
        "senha_hash": hashlib.sha256("senha123".encode()).hexdigest()
    }
}

def autenticar_usuario():
    if st.session_state.get("autenticado"):
        st.sidebar.success(f"👤 Usuário: {st.session_state['usuario']}")
        if st.sidebar.button("🔓 Sair"):
            st.session_state["autenticado"] = False
            st.session_state["usuario"] = None
            st.experimental_rerun()
        return True

    st.title("🔐 Login - ORION PDV")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://github.com/jesusmjunior/pdv2022/blob/69ff7f9ecaa6209d10cec3ea589f803b56180c32/logo.webp", width=200)

    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        if usuario in USUARIOS:
            hash_inserida = hashlib.sha256(senha.encode()).hexdigest()
            if hash_inserida == USUARIOS[usuario]["senha_hash"]:
                st.session_state["autenticado"] = True
                st.session_state["usuario"] = usuario
                st.success("✅ Login realizado com sucesso!")
                st.experimental_rerun()
            else:
                st.error("❌ Senha incorreta.")
        else:
            st.error("❌ Usuário não encontrado.")

    return False
# Lousa 13 - Menu Principal e Roteamento Modular
def main():
    st.set_page_config(page_title="ORION PDV I.A.", layout="wide")

    # Autenticação obrigatória
    if not autenticar_usuario():
        return

    st.sidebar.title("📋 Menu Principal")
    pagina = st.sidebar.radio("Ir para:", [
        "Registrar Venda",
        "Cadastrar Produto",
        "Cadastrar Cliente",
        "Painel Financeiro",
        "Importar Documento OCR"
    ])

    match pagina:
        case "Registrar Venda":
            registrar_venda()
        case "Cadastrar Produto":
            cadastro_produto()
        case "Cadastrar Cliente":
            cadastro_cliente()
        case "Painel Financeiro":
            painel_financeiro()
        case "Importar Documento OCR":
            interface_importar_produtos(
                texto_extraido="",
                tipo_documento=st.sidebar.selectbox("Tipo de Documento", ["Imagem de Nota", "Cupom"])
            )

# Execução
if __name__ == "__main__" or True:
    main()
