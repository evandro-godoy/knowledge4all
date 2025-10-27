import pandas as pd
import json
from pathlib import Path

def load_data(file_path: Path) -> pd.DataFrame:
    """
    Carrega e normaliza os dados JSON do Jira para um DataFrame do Pandas.
    """
    print(f"A carregar dados de '{file_path}'...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            dados_json = json.load(f)
        
        # 'json_normalize' achata a estrutura complexa do JSON
        # O 'record_path' diz onde está a lista de issues
        # O 'meta' diz quais campos do nível superior queremos manter
        df = pd.json_normalize(dados_json, record_path=['issues'], meta=['total'])
        
        # Simplificar nomes de colunas (ex: 'fields.summary' -> 'summary')
        df.columns = df.columns.str.replace('fields.', '', regex=False)
        
        print(f"Dados carregados. {len(df)} issues encontradas.")
        return df
        
    except FileNotFoundError:
        print(f"ERRO: Ficheiro '{file_path}' não encontrado.")
        return pd.DataFrame()
    except Exception as e:
        print(f"ERRO ao processar JSON: {e}")
        return pd.DataFrame()