Dashboard Quadro de Medalhas Olimpicas
Trabalho Pratico Dash e Plotly - Visualizacao de Dados
IF Sudeste de Minas Gerais

Dupla:
- Alexandre Araujo
- Cauan Etienne

LINK DO DASHBOARD (RENDER):
https://dashboard-olimpiadas-txmt.onrender.com
(No plano gratuito do Render, o primeiro acesso pode levar ~50 segundos para carregar.)

CODIGO NO GITHUB:
https://github.com/alex4ndrej7/dashboard-olimpiadas

Arquivos
- app.py                     codigo-fonte (Dash + Plotly Express)
- requirements.txt           dependencias
- Summer_olympic_Medals.csv  base de dados
- render.yaml                configuracao de deploy no Render

Funcionalidades
- Mapa, area empilhada (top 10) e barras (top 10), de 1992 a 2020
- Grafico de pizza (ouro/prata/bronze) com filtro de pais
- Filtro global de tipo de medalha (Ouro, Prata, Bronze, Todos)
- Filtro de ano olimpico (pais sede) aplicado ao grafico de barras
- Extras: indicadores (KPIs), perfil do pais e comparacao entre paises
  (seletor multiplo ou clique no mapa)

Executar localmente
  pip install -r requirements.txt
  python app.py        ->  http://127.0.0.1:8050

Deploy no Render: Web Service | Build: pip install -r requirements.txt | Start: gunicorn app:server
