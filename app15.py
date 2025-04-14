def analisar_danfe(texto):
    produtos = []
    padrao = re.findall(r"\d+\s+\d+\)?\s+((\w+\s?)+)\s+\d+\s+\w+\s+(\d+)\s+([\d,]+)\s+([\d,]+)", texto)
    for item in padrao:
        try:
            descricao = item[0].strip()
            quantidade = int(item[2])
            valor_unitario = float(item[3].replace('.', '').replace(',', '.'))
            valor_total = float(item[4].replace('.', '').replace(',', '.'))
            codigo = str(uuid.uuid4())[:13]
            produtos.append({
                "descricao": descricao,
                "quantidade": quantidade,
                "valor_unitario": valor_unitario,
                "valor_total": valor_total,
                "codigo_barras": codigo
            })
        except:
            continue
    return produtos

def analisar_cupom_fiscal(texto):
    produtos = []
    linhas = re.findall(r'(\d{3})\s+(\d+)\s+(.+?)\s+(\d+)UN\s*X\s*(\d+,\d+)', texto)
    if not linhas:
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

def interface_importar_produtos(texto_extraido, tipo_documento):
    st.subheader("📦 Produtos Detectados")
    produtos = analisar_danfe(texto_extraido) if tipo_documento == "Imagem de Nota" else analisar_cupom_fiscal(texto_extraido)

    if not produtos:
        st.warning("Nenhum produto detectado no documento.")
        return

    st.success(f"{len(produtos)} produtos identificados com sucesso!")

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
        if produtos:
            preco_exemplo = produtos[0]["valor_unitario"] * (1 + margem / 100)
            st.markdown(f"💡 Exemplo: Preço venda = R$ **{preco_exemplo:.2f}**")

    if st.button("✅ Importar Produtos"):
        total_importados = importar_para_estoque(produtos, margem)
        st.success(f"{total_importados} produtos importados ao estoque.")
        st.rerun()

def importar_para_estoque(produtos_extraidos, margem_lucro):
    if 'produtos_db' not in st.session_state:
        st.session_state.produtos_db = {}

    total_importados = 0

    for p in produtos_extraidos:
        codigo = p["codigo_barras"]

        if codigo in st.session_state.produtos_db:
            st.session_state.produtos_db[codigo]["estoque"] += p["quantidade"]
        else:
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
