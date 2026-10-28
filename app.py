"""
Dashboard Quadro de Medalhas Olímpicas (Verão, 1992-2020)
Disciplina: Visualização de Dados - IF Sudeste MG

Requisitos do trabalho:
  * Pizza com filtro de país (ouro/prata/bronze)
  * Filtro de tipo de medalha (Ouro, Prata, Bronze, Todos) nos gráficos
  * Filtro de ano olímpico (país sede) no gráfico de barras
  * Dash + Plotly Express, deploy no Render
Extras: indicadores (KPIs), perfil do país e seção de comparação entre países
        (seletor múltiplo + clique no mapa).
"""
import os

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, State, dcc, html, no_update

# ------------------------------------------------------------------
# 1. Dados
# ------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(BASE_DIR, "Summer_olympic_Medals.csv"))

for c in ("Country_Name", "Host_country"):
    df[c] = df[c].replace("United States", "United States of America")

ANO_INICIAL, ANO_FINAL = 1992, 2020
df = df[(df["Year"] >= ANO_INICIAL) & (df["Year"] <= ANO_FINAL)].copy()
df["Total_Medals"] = df["Gold"] + df["Silver"] + df["Bronze"]
ANOS = sorted(df["Year"].unique())

# ------------------------------------------------------------------
# 2. Configurações visuais e filtros
# ------------------------------------------------------------------
MEDALHAS = {  # tipo -> (coluna, cor, escala do mapa)
    "Todos": ("Total_Medals", "#0085C7", "YlOrRd"),
    "Ouro": ("Gold", "#F4C300", "YlOrBr"),
    "Prata": ("Silver", "#9aa0a6", "Greys"),
    "Bronze": ("Bronze", "#cd7f32", "Oranges"),
}
COR_MEDALHA = {"Ouro": "#F4C300", "Prata": "#B8BDC4", "Bronze": "#cd7f32"}
ICONE = {"Ouro": "🥇", "Prata": "🥈", "Bronze": "🥉"}
AROS = ["#0085C7", "#F4C300", "#000000", "#009F3D", "#DF0024"]  # cores olímpicas
PALETA = px.colors.qualitative.Bold

sedes = df.groupby("Year")[["Host_country", "Host_city"]].first().reset_index()
opcoes_ano = [{"label": f"Todos ({ANO_INICIAL}-{ANO_FINAL})", "value": "Todos"}] + [
    {"label": f"{r.Year} - {r.Host_country} ({r.Host_city})", "value": int(r.Year)}
    for r in sedes.itertuples()
]
paises = sorted(df["Country_Name"].unique())
opcoes_pais = [{"label": p, "value": p} for p in paises]
PAIS_PADRAO = "Brazil" if "Brazil" in paises else paises[0]
COMPARAR_PADRAO = [p for p in ("Brazil", "Argentina", "Japan") if p in paises]
MAX_COMPARAR = 6


def estilo(fig, altura=None):
    """Visual padrão de todos os gráficos."""
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, Roboto, Arial, sans-serif", size=13, color="#1f2937"),
        title=dict(font=dict(size=17), x=0.02),
        margin=dict(l=20, r=20, t=60, b=30),
        legend=dict(title=None),
    )
    if altura:
        fig.update_layout(height=altura)
    return fig


def fig_vazia(titulo, msg="Sem medalhas para o filtro selecionado"):
    fig = px.scatter(title=titulo)
    fig.add_annotation(text=msg, showarrow=False, font=dict(size=16, color="#6b7280"))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return estilo(fig, 380)


# ------------------------------------------------------------------
# 3. Figuras
# ------------------------------------------------------------------
def criar_mapa(tipo):
    col, _, escala = MEDALHAS[tipo]
    dados = df.groupby("Country_Name")[col].sum().reset_index()
    dados = dados[dados[col] > 0]
    fig = px.choropleth(
        dados, locations="Country_Name", locationmode="country names",
        color=col, hover_name="Country_Name", color_continuous_scale=escala,
        labels={col: "Medalhas"},
        title=f"Medalhas ({tipo}) por país, {ANO_INICIAL}-{ANO_FINAL}  ·  clique num país para compará-lo",
    )
    fig.update_geos(showframe=False, showcoastlines=False,
                    projection_type="natural earth", bgcolor="rgba(0,0,0,0)")
    fig.update_layout(coloraxis_colorbar=dict(title="Medalhas", thickness=12))
    return estilo(fig, 500)


def criar_area(tipo):
    col, _, _ = MEDALHAS[tipo]
    top10 = df.groupby("Country_Name")[col].sum().nlargest(10).index
    dados = (
        df[df["Country_Name"].isin(top10)]
        .pivot_table(index="Year", columns="Country_Name", values=col,
                     aggfunc="sum", fill_value=0)
        .reset_index()
        .melt(id_vars="Year", var_name="Country_Name", value_name="Medalhas")
    )
    fig = px.area(dados, x="Year", y="Medalhas", color="Country_Name",
                  color_discrete_sequence=PALETA,
                  title=f"Top 10 países ({tipo}) ao longo dos anos",
                  labels={"Year": "Ano", "Country_Name": "País"})
    fig.update_xaxes(tickmode="array", tickvals=ANOS, title=None)
    fig.update_yaxes(title=None)
    return estilo(fig, 420)


def criar_barras(tipo, ano):
    col, cor, _ = MEDALHAS[tipo]
    base = df if ano == "Todos" else df[df["Year"] == ano]
    if ano == "Todos":
        periodo = f"{ANO_INICIAL}-{ANO_FINAL}"
    else:
        s = sedes[sedes["Year"] == ano].iloc[0]
        periodo = f"{ano} · {s.Host_country}"
    titulo = f"Top 10 países ({tipo}), {periodo}"
    dados = base.groupby("Country_Name")[col].sum()
    dados = dados[dados > 0].nlargest(10).reset_index()
    if dados.empty:
        return fig_vazia(titulo)
    fig = px.bar(dados, x="Country_Name", y=col, text=col, title=titulo,
                 color_discrete_sequence=[cor],
                 labels={"Country_Name": "País", col: "Medalhas"})
    fig.update_traces(textposition="outside", marker_line_width=0)
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    return estilo(fig, 380)


def criar_pizza(pais, tipo):
    titulo = f"{pais}: medalhas por tipo ({ANO_INICIAL}-{ANO_FINAL})"
    s = df[df["Country_Name"] == pais][["Gold", "Silver", "Bronze"]].sum()
    dados = pd.DataFrame({"Medalha": ["Ouro", "Prata", "Bronze"],
                          "Quantidade": [s["Gold"], s["Silver"], s["Bronze"]]})
    if tipo != "Todos":
        dados = dados[dados["Medalha"] == tipo]
    dados = dados[dados["Quantidade"] > 0]
    if dados.empty:
        return fig_vazia(titulo)
    fig = px.pie(dados, names="Medalha", values="Quantidade", title=titulo,
                 color="Medalha", color_discrete_map=COR_MEDALHA, hole=0.35)
    fig.update_traces(textinfo="value+percent", textfont_size=15,
                      marker=dict(line=dict(color="white", width=3)))
    return estilo(fig, 380)


def criar_comparacao_barras(selecionados, tipo):
    titulo = "Medalhas por tipo"
    if not selecionados:
        return fig_vazia(titulo, "Escolha pelo menos um país")
    s = (df[df["Country_Name"].isin(selecionados)]
         .groupby("Country_Name")[["Gold", "Silver", "Bronze"]].sum()
         .rename(columns={"Gold": "Ouro", "Silver": "Prata", "Bronze": "Bronze"})
         .reindex(selecionados).reset_index()
         .melt(id_vars="Country_Name", var_name="Medalha", value_name="Quantidade"))
    if tipo != "Todos":
        s = s[s["Medalha"] == tipo]
    fig = px.bar(s, x="Country_Name", y="Quantidade", color="Medalha",
                 barmode="group", text="Quantidade", title=titulo,
                 color_discrete_map=COR_MEDALHA,
                 labels={"Country_Name": "País"})
    fig.update_traces(textposition="outside", marker_line_width=0)
    fig.update_xaxes(title=None)
    fig.update_yaxes(title=None)
    return estilo(fig, 400)


def criar_comparacao_linhas(selecionados, tipo):
    col, _, _ = MEDALHAS[tipo]
    titulo = f"Evolução por edição ({tipo})"
    if not selecionados:
        return fig_vazia(titulo, "Escolha pelo menos um país")
    d = (df[df["Country_Name"].isin(selecionados)]
         .pivot_table(index="Year", columns="Country_Name", values=col,
                      aggfunc="sum", fill_value=0)
         .reindex(ANOS, fill_value=0)
         .reset_index()
         .melt(id_vars="Year", var_name="Country_Name", value_name="Medalhas"))
    fig = px.line(d, x="Year", y="Medalhas", color="Country_Name", markers=True,
                  color_discrete_sequence=PALETA, title=titulo,
                  labels={"Year": "Ano", "Country_Name": "País"})
    fig.update_traces(line=dict(width=3), marker=dict(size=9))
    fig.update_xaxes(tickmode="array", tickvals=ANOS, title=None)
    fig.update_yaxes(title=None)
    return estilo(fig, 400)


# ------------------------------------------------------------------
# 4. Componentes de layout
# ------------------------------------------------------------------
CARD = {"background": "white", "borderRadius": "14px", "padding": "14px 16px",
        "boxShadow": "0 2px 10px rgba(15,23,42,0.08)", "flex": "1",
        "minWidth": "340px"}
LINHA = {"display": "flex", "flexWrap": "wrap", "gap": "16px", "marginBottom": "16px"}
ROTULO = {"fontWeight": "600", "fontSize": "13px", "color": "#475569",
          "display": "block", "marginBottom": "6px"}


def kpi(titulo, valor, detalhe="", cor="#0085C7"):
    return html.Div(
        style={**CARD, "minWidth": "190px", "borderTop": f"5px solid {cor}"},
        children=[
            html.Div(titulo, style={"fontSize": "12px", "color": "#64748b",
                                    "textTransform": "uppercase", "letterSpacing": "0.05em"}),
            html.Div(valor, style={"fontSize": "30px", "fontWeight": "700", "margin": "4px 0"}),
            html.Div(detalhe, style={"fontSize": "13px", "color": "#64748b"}),
        ],
    )


def titulo_secao(txt, sub=""):
    return html.Div(style={"margin": "26px 4px 12px"}, children=[
        html.H2(txt, style={"margin": 0, "fontSize": "22px"}),
        html.Div(sub, style={"color": "#64748b", "fontSize": "14px"}),
    ])


app = Dash(__name__)
app.title = "Quadro de Medalhas Olímpicas"
server = app.server  # usado pelo gunicorn no Render

app.layout = html.Div(
    style={"background": "#eef2f7", "minHeight": "100vh",
           "fontFamily": "Segoe UI, Roboto, Arial, sans-serif", "color": "#1f2937"},
    children=[
        # cabeçalho
        html.Div(
            style={"background": "linear-gradient(120deg,#0b1f3a,#16467a)",
                   "color": "white", "padding": "26px 20px 22px", "textAlign": "center"},
            children=[
                html.Div(style={"display": "flex", "justifyContent": "center", "gap": "10px",
                                "marginBottom": "10px"},
                         children=[html.Div(style={"width": "26px", "height": "26px",
                                                   "borderRadius": "50%",
                                                   "border": f"5px solid {c}"})
                                   for c in AROS]),
                html.H1("Quadro de Medalhas Olímpicas", style={"margin": 0, "fontSize": "34px"}),
                html.Div(f"Jogos de Verão, {ANO_INICIAL} a {ANO_FINAL}",
                         style={"opacity": 0.8, "marginTop": "4px"}),
            ],
        ),

        html.Div(style={"maxWidth": "1400px", "margin": "0 auto", "padding": "0 16px 30px"}, children=[
            # filtro global (fixo no topo ao rolar)
            html.Div(
                style={**CARD, "flex": "none", "position": "sticky", "top": "8px", "zIndex": 10,
                       "margin": "-18px 0 8px", "display": "flex", "alignItems": "center",
                       "gap": "18px", "flexWrap": "wrap"},
                children=[
                    html.Span("Tipo de medalha", style={**ROTULO, "marginBottom": 0}),
                    dcc.RadioItems(
                        id="filtro-medalha",
                        options=[{"label": f"{ICONE.get(m, '🏅')} {m}", "value": m} for m in MEDALHAS],
                        value="Todos", inline=True,
                        labelStyle={"marginRight": "22px", "fontSize": "16px", "cursor": "pointer"},
                    ),
                    html.Span("→ vale para todos os gráficos", style={"color": "#94a3b8", "fontSize": "13px"}),
                ],
            ),

            # indicadores
            html.Div(id="kpis", style={**LINHA, "marginTop": "16px"}),

            # mapa
            html.Div(style=LINHA, children=[
                html.Div(style=CARD, children=[dcc.Graph(id="grafico-mapa")]),
            ]),

            # área + barras (com filtro de ano)
            html.Div(style=LINHA, children=[
                html.Div(style=CARD, children=[dcc.Graph(id="grafico-area")]),
                html.Div(style=CARD, children=[
                    html.Label("Ano olímpico / país sede", style=ROTULO),
                    dcc.Dropdown(id="filtro-ano", options=opcoes_ano, value="Todos", clearable=False),
                    dcc.Graph(id="grafico-barras"),
                ]),
            ]),

            titulo_secao("Foco em um país", "Escolha um país para ver o detalhe de ouro, prata e bronze"),
            html.Div(style=LINHA, children=[
                html.Div(style=CARD, children=[
                    html.Label("País", style=ROTULO),
                    dcc.Dropdown(id="filtro-pais", options=opcoes_pais, value=PAIS_PADRAO, clearable=False),
                    dcc.Graph(id="grafico-pizza"),
                ]),
                html.Div(style={**CARD, "display": "flex", "flexDirection": "column",
                                "justifyContent": "center", "gap": "14px"}, id="perfil-pais"),
            ]),

            titulo_secao("Comparar países",
                         "Selecione até 6 países, ou clique num país no mapa para adicioná-lo"),
            html.Div(style={**CARD, "flex": "none", "marginBottom": "16px"}, children=[
                dcc.Dropdown(id="filtro-comparar", options=opcoes_pais, value=COMPARAR_PADRAO,
                             multi=True, placeholder="Escolha os países para comparar..."),
            ]),
            html.Div(id="cartoes-comparacao", style=LINHA),
            html.Div(style=LINHA, children=[
                html.Div(style=CARD, children=[dcc.Graph(id="comparar-barras")]),
                html.Div(style=CARD, children=[dcc.Graph(id="comparar-linhas")]),
            ]),

            html.Div("Dados: Summer Olympic Medals (Kaggle) · Trabalho de Visualização de Dados, IF Sudeste MG",
                     style={"textAlign": "center", "color": "#94a3b8", "fontSize": "13px",
                            "marginTop": "20px"}),
        ]),
    ],
)


# ------------------------------------------------------------------
# 5. Callbacks
# ------------------------------------------------------------------
@app.callback(Output("kpis", "children"), Input("filtro-medalha", "value"))
def atualizar_kpis(tipo):
    col, cor, _ = MEDALHAS[tipo]
    por_pais = df.groupby("Country_Name")[col].sum()
    lider = por_pais.idxmax()
    return [
        kpi(f"Medalhas ({tipo})", f"{int(por_pais.sum()):,}".replace(",", "."),
            f"{ANO_INICIAL}-{ANO_FINAL}", cor),
        kpi("Países com medalha", int((por_pais > 0).sum()), "no filtro selecionado", "#009F3D"),
        kpi("Líder", lider, f"{int(por_pais.max())} medalhas ({tipo})", "#DF0024"),
        kpi("Edições", len(ANOS), f"{ANOS[0]} a {ANOS[-1]}", "#000000"),
    ]


@app.callback(Output("grafico-mapa", "figure"), Input("filtro-medalha", "value"))
def atualizar_mapa(tipo):
    return criar_mapa(tipo)


@app.callback(Output("grafico-area", "figure"), Input("filtro-medalha", "value"))
def atualizar_area(tipo):
    return criar_area(tipo)


@app.callback(Output("grafico-barras", "figure"),
              Input("filtro-medalha", "value"), Input("filtro-ano", "value"))
def atualizar_barras(tipo, ano):
    return criar_barras(tipo, ano)


@app.callback(Output("grafico-pizza", "figure"),
              Input("filtro-pais", "value"), Input("filtro-medalha", "value"))
def atualizar_pizza(pais, tipo):
    return criar_pizza(pais, tipo)


@app.callback(Output("perfil-pais", "children"),
              Input("filtro-pais", "value"), Input("filtro-medalha", "value"))
def atualizar_perfil(pais, tipo):
    col, cor, _ = MEDALHAS[tipo]
    ranking = df.groupby("Country_Name")[col].sum().sort_values(ascending=False)
    ranking = ranking[ranking > 0]
    total = int(ranking.get(pais, 0))
    pos = f"#{list(ranking.index).index(pais) + 1} de {len(ranking)}" if pais in ranking.index else "sem medalhas"
    por_ano = df[df["Country_Name"] == pais].groupby("Year")[col].sum()
    if por_ano.sum() > 0:
        a = int(por_ano.idxmax())
        s = sedes[sedes["Year"] == a].iloc[0]
        melhor = f"{a} · {s.Host_city}"
        melhor_det = f"{int(por_ano.max())} medalhas ({tipo})"
    else:
        melhor, melhor_det = "-", ""
    return [
        html.H3(f"Perfil: {pais}", style={"margin": 0}),
        kpi(f"Medalhas ({tipo})", total, f"{ANO_INICIAL}-{ANO_FINAL}", cor),
        kpi("Posição no ranking", pos, f"entre os países com medalha ({tipo})", "#009F3D"),
        kpi("Melhor edição", melhor, melhor_det, "#F4C300"),
    ]


@app.callback(Output("filtro-comparar", "value"),
              Input("grafico-mapa", "clickData"),
              State("filtro-comparar", "value"),
              prevent_initial_call=True)
def adicionar_pelo_mapa(click, atuais):
    """Clicar num país no mapa adiciona ele à comparação."""
    if not click:
        return no_update
    pais = click["points"][0].get("location")
    if pais not in paises:
        return no_update
    atuais = list(atuais or [])
    if pais in atuais:
        return no_update
    atuais.append(pais)
    return atuais[-MAX_COMPARAR:]


@app.callback(Output("cartoes-comparacao", "children"),
              Input("filtro-comparar", "value"), Input("filtro-medalha", "value"))
def atualizar_cartoes(selecionados, tipo):
    if not selecionados:
        return [html.Div("Escolha países acima para comparar.", style={"color": "#64748b", "padding": "8px"})]
    selecionados = selecionados[:MAX_COMPARAR]
    col, _, _ = MEDALHAS[tipo]
    ranking = df.groupby("Country_Name")[col].sum().sort_values(ascending=False)
    cartoes = []
    for i, p in enumerate(selecionados):
        s = df[df["Country_Name"] == p][["Gold", "Silver", "Bronze", "Total_Medals"]].sum()
        pos = list(ranking.index).index(p) + 1 if p in ranking.index else "-"
        cartoes.append(html.Div(
            style={**CARD, "minWidth": "210px", "borderTop": f"5px solid {PALETA[i % len(PALETA)]}"},
            children=[
                html.Div(p, style={"fontSize": "18px", "fontWeight": "700"}),
                html.Div(f"{int(s['Total_Medals'])} medalhas no total",
                         style={"color": "#64748b", "fontSize": "13px", "marginBottom": "8px"}),
                html.Div(f"🥇 {int(s['Gold'])}   🥈 {int(s['Silver'])}   🥉 {int(s['Bronze'])}",
                         style={"fontSize": "17px"}),
                html.Div(f"Ranking ({tipo}): #{pos}",
                         style={"color": "#64748b", "fontSize": "13px", "marginTop": "8px"}),
            ],
        ))
    return cartoes


@app.callback(Output("comparar-barras", "figure"),
              Input("filtro-comparar", "value"), Input("filtro-medalha", "value"))
def atualizar_comparar_barras(selecionados, tipo):
    return criar_comparacao_barras((selecionados or [])[:MAX_COMPARAR], tipo)


@app.callback(Output("comparar-linhas", "figure"),
              Input("filtro-comparar", "value"), Input("filtro-medalha", "value"))
def atualizar_comparar_linhas(selecionados, tipo):
    return criar_comparacao_linhas((selecionados or [])[:MAX_COMPARAR], tipo)


if __name__ == "__main__":
    app.run(debug=False, port=int(os.environ.get("PORT", 8050)))
