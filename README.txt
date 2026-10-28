Dashboard Quadro de Medalhas Olimpicas - Visualizacao de Dados (IFSEMG)
Dupla: <NOME ALUNO 1> e <NOME ALUNO 2>

LINK DO DASHBOARD NO RENDER: <COLAR AQUI A URL https://....onrender.com>

Arquivos
- app.py                     codigo-fonte (Dash + Plotly Express)
- requirements.txt           dependencias
- Summer_olympic_Medals.csv  base de dados
- render.yaml                configuracao de deploy no Render

Funcionalidades
- Mapa, area empilhada (top 10) e barras (top 10) - 1992 a 2020
- NOVO: grafico de pizza (ouro/prata/bronze) com filtro de pais
- NOVO: filtro global de tipo de medalha (Ouro, Prata, Bronze, Todos) nos 3 graficos
        (mapa, area empilhada/barras) e na pizza
- NOVO: filtro de ano olimpico (pais sede) aplicado ao grafico de barras

Executar localmente
  pip install -r requirements.txt
  python app.py        ->  http://127.0.0.1:8050

Deploy no Render: Web Service | Build: pip install -r requirements.txt | Start: gunicorn app:server
