import datetime
import json
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="GlútenZero | Vida sem Glúten",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS customizada
st.markdown(
    """
    <style>
    .main {
        background-color: #FAFAFA;
    }
    .stAppHeader {
        background-color: rgba(255, 255, 255, 0.8);
    }
    .card-seguro {
        background-color: #E8F5E9;
        border-left: 5px solid #2E7D32;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .card-atencao {
        background-color: #FFFDE7;
        border-left: 5px solid #F57F17;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .card-perigo {
        background-color: #FFEBEE;
        border-left: 5px solid #C62828;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# DADOS EM MEMÓRIA / BANCO DE DADOS LOCAL
# -----------------------------------------------------------------------------

ALIMENTOS_DB = [
    {
        "nome": "Arroz (Branco, Integral, Parboilizado)",
        "categoria": "Grãos e Cereais",
        "status": "Permitido",
        "detalhes": "Naturalmente isento de glúten. Cuidado apenas com contaminação em grãos a granel.",
    },
    {
        "nome": "Feijão, Lentilha e Grão-de-Bico",
        "categoria": "Leguminosas",
        "status": "Permitido",
        "detalhes": "Excelente fonte de proteínas e fibras. Lave bem antes do cozimento.",
    },
    {
        "nome": "Farinha de Trigo",
        "categoria": "Farinhas e Fermentos",
        "status": "Proibido",
        "detalhes": "Contém glúten em alta quantidade. Substitua por farinha de arroz, amido de milho ou fécula de batata.",
    },
    {
        "nome": "Aveia",
        "categoria": "Grãos e Cereais",
        "status": "Atenção",
        "detalhes": "A aveia em si não tem glúten, mas quase toda aveia no Brasil sofre contaminação cruzada no campo ou no processamento. Consuma apenas as rotuladas 'NÃO CONTÉM GLÚTEN'.",
    },
    {
        "nome": "Cerveja Tradicional",
        "categoria": "Bebidas",
        "status": "Proibido",
        "detalhes": "Feita à base de cevada/malte. Busque versões purificadas ou elaboradas especificamente para celíacos.",
    },
    {
        "nome": "Batata, Mandioca e Inhame",
        "categoria": "Tubérculos",
        "status": "Permitido",
        "detalhes": "Tubérculos in natura são 100% seguros e ótimas fontes de carboidrato.",
    },
    {
        "nome": "Molho de Soja (Shoyu)",
        "categoria": "Temperos e Molhos",
        "status": "Atenção",
        "detalhes": "A maioria das marcas tradicionais leva trigo na composição. Opte por 'Shoyu Tamari' ou marcas sem glúten.",
    },
    {
        "nome": "Pão Francês Tradicional",
        "categoria": "Padaria",
        "status": "Proibido",
        "detalhes": "Feito com farinha de trigo. Nunca consumir.",
    },
    {
        "nome": "Massa / Macarrão Tradicional",
        "categoria": "Massas",
        "status": "Proibido",
        "detalhes": "Contém sêmola/trigo. Substitua por macarrão de arroz, milho ou konjac.",
    },
    {
        "nome": "Tapioca (Goma de Mandioca)",
        "categoria": "Farinhas e Fermentos",
        "status": "Permitido",
        "detalhes": "Opção prática e naturalmente sem glúten para o café da manhã ou lanches.",
    },
]

RECEITAS_DB = [
    {
        "nome": "Pão de Queijo Mineiro",
        "categoria": "Café da Manhã",
        "tempo": "35 min",
        "porcoes": "12 unidades",
        "ingredientes": [
            "500g de polvilho azedo",
            "250ml de leite integral",
            "100ml de óleo vegetal",
            "1 colher de chá de sal",
            "2 ovos",
            "200g de queijo meia cura ou prato ralado",
        ],
        "modo_preparo": (
            "1. Ferva o leite com o óleo e o sal.\n"
            "2. Em uma tigela, despeje a mistura fervente sobre o polvilho para escaldar.\n"
            "3. Espere esfriar um pouco e adicione os ovos e o queijo ralado.\n"
            "4. Sove bem a massa até ficar homogênea e modelável.\n"
            "5. Faça bolinhas, coloque em uma assadeira e asse em forno pré-aquecido a 200°C por 25 minutos."
        ),
    },
    {
        "nome": "Panqueca Rápida de Banana e Aveia Sem Glúten",
        "categoria": "Lanches",
        "tempo": "10 min",
        "porcoes": "1 porção",
        "ingredientes": [
            "1 banana madura amassada",
            "1 ovo",
            "2 colheres de sopa de aveia sem glúten",
            "1 pitada de canela em pó",
        ],
        "modo_preparo": (
            "1. Misture todos os ingredientes em uma tigela pequena até obter uma massa uniforme.\n"
            "2. Unte uma frigideira antiaderente com um pouco de óleo de coco ou manteiga.\n"
            "3. Despeje a massa em fogo baixo e doure dos dois lados.\n"
            "4. Sirva com mel ou frutas picadas."
        ),
    },
    {
        "nome": "Bolo de Fubá Crespo",
        "categoria": "Sobremesas",
        "tempo": "45 min",
        "porcoes": "8 fatias",
        "ingredientes": [
            "2 xícaras de fubá mimoso",
            "1 xícara de açúcar",
            "3 ovos",
            "1 xícara de leite",
            "1/2 xícara de óleo",
            "1 colher de sopa de fermento químico em pó",
        ],
        "modo_preparo": (
            "1. Bata no liquidificador os ovos, o açúcar, o leite e o óleo.\n"
            "2. Adicione o fubá e bata até incorporar.\n"
            "3. Misture delicadamente o fermento com uma espátula.\n"
            "4. Despeje em forma untada e enfarinhada com fubá.\n"
            "5. Asse a 180°C por cerca de 35 a 40 minutos."
        ),
    },
]

DIARIO_FILE = "diario_gluten.json"


def carregar_diario():
    if os.path.exists(DIARIO_FILE):
        try:
            with open(DIARIO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def salvar_diario(registros):
    with open(DIARIO_FILE, "w", encoding="utf-8") as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)


# -----------------------------------------------------------------------------
# INTERFACE DO USUÁRIO
# -----------------------------------------------------------------------------

st.sidebar.title("🌾 GlútenZero")
st.sidebar.caption("Seu guia seguro para uma vida saudável sem glúten")

menu = st.sidebar.radio(
    "Navegação",
    [
        "🔍 Guia de Alimentos",
        "📖 Receitas Sem Glúten",
        "📝 Diário & Sintomas",
        "🛡️ Contaminação Cruzada",
    ],
)

# -----------------------------------------------------------------------------
# ABA 1: GUIA DE ALIMENTOS
# -----------------------------------------------------------------------------
if menu == "🔍 Guia de Alimentos":
    st.title("🔍 Guia & Busca de Alimentos")
    st.write(
        "Consulte rapidamente quais alimentos são seguros, exigem atenção ou devem ser totalmente evitados."
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        busca = st.text_input(
            "Pesquisar alimento:",
            placeholder="Ex: Arroz, Aveia, Molho de soja...",
        )
    with col2:
        categorias = ["Todas"] + sorted(
            list(set(a["categoria"] for a in ALIMENTOS_DB))
        )
        cat_selecionada = st.selectbox("Filtrar por Categoria:", categorias)

    status_filtro = st.multiselect(
        "Filtrar por Status:",
        ["Permitido", "Atenção", "Proibido"],
        default=["Permitido", "Atenção", "Proibido"],
    )

    # Filtragem
    resultados = ALIMENTOS_DB
    if busca:
        resultados = [
            a
            for a in resultados
            if busca.lower() in a["nome"].lower()
            or busca.lower() in a["detalhes"].lower()
        ]
    if cat_selecionada != "Todas":
        resultados = [
            a for a in resultados if a["categoria"] == cat_selecionada
        ]
    resultados = [a for a in resultados if a["status"] in status_filtro]

    st.markdown("---")
    st.subheader(f"Resultados ({len(resultados)})")

    if not resultados:
        st.info("Nenhum alimento encontrado com os filtros selecionados.")
    else:
        for item in resultados:
            if item["status"] == "Permitido":
                st.markdown(
                    f"""
                <div class="card-seguro">
                    <h4>🟢 {item['nome']} <small>({item['categoria']})</small></h4>
                    <p><strong>Status:</strong> Seguro / Liberado</p>
                    <p>{item['detalhes']}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            elif item["status"] == "Atenção":
                st.markdown(
                    f"""
                <div class="card-atencao">
                    <h4>🟡 {item['nome']} <small>({item['categoria']})</small></h4>
                    <p><strong>Status:</strong> Atenção / Risco de Contaminação</p>
                    <p>{item['detalhes']}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                <div class="card-perigo">
                    <h4>🔴 {item['nome']} <small>({item['categoria']})</small></h4>
                    <p><strong>Status:</strong> Proibido / Contém Glúten</p>
                    <p>{item['detalhes']}</p>
                </div>
                """,
                    unsafe_allow_html=True,
                )

# -----------------------------------------------------------------------------
# ABA 2: RECEITAS SEM GLÚTEN
# -----------------------------------------------------------------------------
elif menu == "📖 Receitas Sem Glúten":
    st.title("📖 Receitas Sem Glúten")
    st.write("Opções fáceis e saborosas para o seu dia a dia.")

    cat_rec = st.selectbox(
        "Filtrar por Refeição:",
        ["Todas", "Café da Manhã", "Almoço/Jantar", "Lanches", "Sobremesas"],
    )

    receitas_filtradas = RECEITAS_DB
    if cat_rec != "Todas":
        receitas_filtradas = [
            r for r in RECEITAS_DB if r["categoria"] == cat_rec
        ]

    st.markdown("---")

    for rec in receitas_filtradas:
        with st.expander(f"🍞 {rec['nome']} ({rec['categoria']})"):
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"⏱️ **Tempo de preparo:** {rec['tempo']}")
            with col_b:
                st.write(f"🍽️ **Rendimento:** {rec['porcoes']}")

            st.markdown("#### Ingredientes:")
            for ing in rec["ingredientes"]:
                st.write(f"- {ing}")

            st.markdown("#### Modo de Preparo:")
            st.write(rec["modo_preparo"])

# -----------------------------------------------------------------------------
# ABA 3: DIÁRIO DE REFEIÇÕES E SINTOMAS
# -----------------------------------------------------------------------------
elif menu == "📝 Diário & Sintomas":
    st.title("📝 Diário de Refeições e Sintomas")
    st.write(
        "Acompanhe o que você come e como seu corpo reage para identificar sensibilidades ou contaminações acidentais."
    )

    registros = carregar_diario()

    with st.form("form_diario"):
        st.subheader("Novo Registro")
        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data:", datetime.date.today())
            refeicao = st.text_input(
                "O que você comeu?",
                placeholder="Ex: Arroz, feijão, salada e frango grelhado",
            )
        with col2:
            bem_estar = st.slider(
                "Nível de Bem-Estar (1 = Péssimo, 5 = Excelente):", 1, 5, 5
            )
            sintomas = st.multiselect(
                "Sintomas apresentados:",
                [
                    "Nenhum",
                    "Dor abdominal",
                    "Estufamento / Gases",
                    "Diarreia",
                    "Cansaço / Fadiga",
                    "Dor de cabeça",
                    "Erupções na pele",
                ],
                default=["Nenhum"],
            )

        observacoes = st.text_area(
            "Observações adicionais (ex: comeu fora de casa?):"
        )
        submetido = st.form_submit_button("Salvar no Diário")

        if submetido:
            if not refeicao:
                st.error("Por favor, descreva o que você comeu.")
            else:
                novo_registro = {
                    "data": str(data),
                    "refeicao": refeicao,
                    "bem_estar": bem_estar,
                    "sintomas": sintomas,
                    "observacoes": observacoes,
                }
                registros.append(novo_registro)
                salvar_diario(registros)
                st.success("Registro adicionado com sucesso!")

    st.markdown("---")
    st.subheader("Histórico do Diário")

    if not registros:
        st.info("Nenhum registro encontrado.")
    else:
        df = pd.DataFrame(registros)

        # Gráfico visual de bem-estar ao longo do tempo
        if len(df) > 1:
            fig = px.line(
                df,
                x="data",
                y="bem_estar",
                title="Evolução do Bem-Estar ao Longo do Tempo",
                markers=True,
                range_y=[0.5, 5.5],
            )
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True)

# -----------------------------------------------------------------------------
# ABA 4: CONTAMINAÇÃO CRUZADA & GUIA EDUCATIVO
# -----------------------------------------------------------------------------
elif menu == "🛡️ Contaminação Cruzada":
    st.title("🛡️ Guia de Prevenção e Contaminação Cruzada")
    st.write(
        "A contaminação cruzada ocorre quando um alimento sem glúten entra em contato direto ou indireto com partículas de glúten."
    )

    st.markdown("### 🍳 Cuidados Fundamentais na Cozinha")

    col_1, col_2 = st.columns(2)

    with col_1:
        st.success("✅ O que fazer")
        st.write("- Use torradeiras e airfryers exclusivas para sem glúten.")
        st.write(
            "- Tenha tábuas de corte separadas (especialmente de madeira)."
        )
        st.write(
            "- Lave bem louças com esponjas novas e exclusivas para utensílios sem glúten."
        )
        st.write(
            "- Limpe balcões e mesas antes de manipular alimentos seguros."
        )

    with col_2:
        st.danger("❌ O que evitar")
        st.write(
            "- Não utilize o mesmo óleo onde foram fritos empanados com trigo."
        )
        st.write(
            "- Evite potes de manteiga/requeijão onde facas com farelos de pão foram passadas."
        )
        st.write(
            "- Não aproveite a água do cozimento de massas tradicionais."
        )
        st.write(
            "- Evite comprar grãos e farinhas a granel pelo alto risco de contaminação nos recipientes."
        )

    st.markdown("---")
    st.markdown("### 📜 Como Ler Rótulos de Alimentos")
    st.info(
        "No Brasil (Lei nº 10.674/2003), todos os alimentos industrializados devem obrigatoriamente informar no rótulo se contêm ou não glúten."
    )

    st.write(
        "1. **'NÃO CONTÉM GLÚTEN':** Seguro para consumo por celíacos e intolerantes.\n"
        "2. **'CONTÉM GLÚTEN':** Contém trigo, cevada, centeio, aveia comum ou derivados.\n"
        "3. **Alerta de Contaminação Cruzada:** Mesmo sem ingredientes com glúten, se o rótulo disser *'Pode conter trigo/glúten'*, significa que o produto compartilha maquinário e NÃO é seguro."
    )
