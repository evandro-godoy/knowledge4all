import pandas as pd
import re

# Definição das palavras-chave (nosso modelo de classificação)
CLASSIFICADORES = {
    "NORMAS_RH": ["férias", "norma", "vestimenta", "dress code", "conduta", "reembolso"],
    "DOCUMENTOS": ["documento", "formulário", "template"],
    "ACESSO_SISTEMAS": ["acesso", "login", "senha", "parou de funcionar", "não consigo aceder", "seguroauto"]
}

# Status que consideramos "Concluído"
STATUS_CONCLUIDO = ["Concluído", "Resolvido", "Fechado", "Done"]

def clean_text(text: str) -> str:
    """
    Limpa o texto: minúsculas e remove pontuação/números.
    Esta é uma etapa fundamental do processamento de NLP.
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"[^a-zà-ú\s]", "", text) # Mantém apenas letras e espaços
    text = re.sub(r"\s+", " ", text).strip() # Remove espaços extras
    return text

def classify_task(text: str) -> list:
    """
    Classifica uma tarefa com base no seu texto limpo.
    """
    categorias_encontradas = []
    for categoria, palavras in CLASSIFICADORES.items():
        if any(palavra in text for palavra in palavras):
            categorias_encontradas.append(categoria)
    
    return categorias_encontradas if categorias_encontradas else ["OUTROS"]

def extract_solution(row: pd.Series) -> str:
    """
    Extrai a solução do último comentário.
    """
    try:
        # A coluna 'comment.comments' é uma lista de dicts
        comentarios = row.get('comment.comments', [])
        if comentarios and isinstance(comentarios, list) and len(comentarios) > 0:
            return comentarios[-1].get('body', 'N/A')
    except Exception:
        pass
    return "Solução não registada em comentário."

def process_tickets(df: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
    """
    Processa o DataFrame principal, limpa, classifica e divide
    em tarefas abertas e base de conhecimento (concluídas).
    """
    print("A processar e classificar tickets...")
    
    # Combinar resumo e descrição para ter o texto completo
    df['full_text'] = df['summary'].fillna('') + " " + df['description'].fillna('')
    
    # Aplicar limpeza de NLP
    df['clean_text'] = df['full_text'].apply(clean_text)
    
    # Aplicar classificação (Modelo de Regras NLP)
    df['categories'] = df['clean_text'].apply(classify_task)
    
    # Separar os DataFrames
    df_concluidos = df[df['status.name'].isin(STATUS_CONCLUIDO)].copy()
    df_abertos = df[~df['status.name'].isin(STATUS_CONCLUIDO)].copy()
    
    # Extrair a solução apenas dos concluídos
    df_concluidos['solution'] = df_concluidos.apply(extract_solution, axis=1)
    
    print(f"Processamento concluído: {len(df_abertos)} abertas, {len(df_concluidos)} concluídas (Base de Conhecimento).")
    return df_abertos, df_concluidos