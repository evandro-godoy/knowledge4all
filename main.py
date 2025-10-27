from pathlib import Path
from jira_knowledge_miner.utils import data_loader
from jira_knowledge_miner.core import processor, matcher
from jira_knowledge_miner.reporting import generator

# Definir caminhos (Pathlib torna isto mais robusto)
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "dados_jira.json"
REPORT_FILE = BASE_DIR / "reports" / "report_analise_jira.html"

def run_pipeline():
    """
    Orquestra a execução completa da pipeline de análise.
    """
    print("--- Iniciando Pipeline JiraKnowledgeMiner ---")
    
    # 1. Carregar Dados
    df_raw = data_loader.load_data(DATA_FILE)
    if df_raw.empty:
        print("Pipeline interrompida: Não foi possível carregar os dados.")
        return

    # 2. Processar e Classificar
    df_abertos, df_concluidos = processor.process_tickets(df_raw)
    
    if df_concluidos.empty:
        print("Pipeline interrompida: Nenhuma Base de Conhecimento (tickets concluídos) encontrada.")
        return

    # 3. Preparar o Matcher
    ticket_matcher = matcher.TicketMatcher()
    ticket_matcher.fit(df_concluidos)

    # 4. Encontrar Sugestões
    df_sugestoes = ticket_matcher.find_matches(df_abertos)
    
    # 5. Gerar Relatório
    # Certificar que a pasta de relatórios existe
    REPORT_FILE.parent.mkdir(exist_ok=True)
    generator.generate_report(df_abertos, df_concluidos, df_sugestoes, REPORT_FILE)
    
    print(f"--- Pipeline Concluída --- \nRelatório disponível em: {REPORT_FILE}")

# Ponto de entrada do script
if __name__ == "__main__":
    run_pipeline()