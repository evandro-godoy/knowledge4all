import pandas as pd
from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path

# Template HTML simples (pode ser movido para um ficheiro .html)
REPORT_TEMPLATE = """
<html>
<head>
    <title>Relatório de Análise - Jira Knowledge Miner</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2 { color: #0052CC; }
        table { border-collapse: collapse; width: 80%; margin-top: 15px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .metric { font-size: 1.2em; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Relatório de Análise - Jira Knowledge Miner</h1>
    
    <h2>Indicadores Principais (KPIs)</h2>
    <p>Total de Tickets Processados: <span class="metric">{{ kpis.total_tickets }}</span></p>
    <p>Tickets Abertos: <span class="metric">{{ kpis.total_abertos }}</span></p>
    <p>Tickets na Base de Conhecimento (Concluídos): <span class="metric">{{ kpis.total_concluidos }}</span></p>
    <p>Taxa de Cobertura (Abertos com Sugestão): <span class="metric">{{ "%.2f"|format(kpis.cobertura_perc) }}%</span></p>

    <h2>Distribuição de Tickets por Categoria (Top 10)</h2>
    <h3>Base de Conhecimento (Concluídos)</h3>
    {{ tabelas.dist_concluidos | safe }}
    
    <h3>Tickets Abertos</h3>
    {{ tabelas.dist_abertos | safe }}

    <h2>Sugestões Geradas (Amostra)</h2>
    {{ tabelas.sugestoes | safe }}
</body>
</html>
"""

def generate_report(df_abertos: pd.DataFrame, df_concluidos: pd.DataFrame, df_sugestoes: pd.DataFrame, output_path: Path):
    """
    Gera um relatório HTML com os principais indicadores.
    """
    print(f"A gerar relatório em '{output_path}'...")
    
    # 1. Calcular KPIs
    total_sugestoes = df_sugestoes['key_sugerida'].notna().sum()
    cobertura_perc = (total_sugestoes / len(df_abertos)) * 100 if len(df_abertos) > 0 else 0
    
    kpis = {
        "total_tickets": len(df_abertos) + len(df_concluidos),
        "total_abertos": len(df_abertos),
        "total_concluidos": len(df_concluidos),
        "cobertura_perc": cobertura_perc
    }
    
    # 2. Calcular Distribuição de Categorias
    # Usamos 'explode' para contar categorias separadamente
    dist_concluidos = df_concluidos['categories'].explode().value_counts().to_frame(name="Total")
    dist_abertos = df_abertos['categories'].explode().value_counts().to_frame(name="Total")

    # 3. Preparar tabelas para o Jinja2
    tabelas = {
        "dist_concluidos": dist_concluidos.head(10).to_html(),
        "dist_abertos": dist_abertos.head(10).to_html(),
        "sugestoes": df_sugestoes[df_sugestoes['similaridade'] > 0.2].head(20).to_html(index=False)
    }

    # 4. Renderizar o template
    template = Template(REPORT_TEMPLATE)
    html_output = template.render(kpis=kpis, tabelas=tabelas)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_output)
        
    print("Relatório gerado com sucesso.")