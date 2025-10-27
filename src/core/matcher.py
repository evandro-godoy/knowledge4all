import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TicketMatcher:
    """
    Classe para treinar o vetorizador e encontrar correspondências.
    """
    def __init__(self):
        # Inicializa o vetorizador de NLP.
        # 'stop_words="english"' pode ser trocado por "portuguese" se
        # a biblioteca scikit-learn tiver o suporte, ou podemos
        # fornecer uma lista manual de stopwords.
        self.vectorizer = TfidfVectorizer(stop_words=None, max_df=0.85, min_df=1)
        self.kb_matrix = None
        self.kb_df = None

    def fit(self, kb_df: pd.DataFrame):
        """
        "Treina" o vetorizador na base de conhecimento.
        """
        print("A treinar vetorizador (TF-IDF) na Base de Conhecimento...")
        self.kb_df = kb_df
        # Garante que 'clean_text' não tenha valores nulos
        text_data = self.kb_df['clean_text'].fillna('')
        self.kb_matrix = self.vectorizer.fit_transform(text_data)
        print("Vetorizador treinado.")

    def find_matches(self, df_abertos: pd.DataFrame) -> pd.DataFrame:
        """
        Encontra as melhores correspondências para os tickets abertos.
        """
        print("A procurar correspondências para tickets abertos...")
        resultados = []

        for _, row_aberta in df_abertos.iterrows():
            texto_aberto = row_aberta['clean_text']
            categorias_aberta = row_aberta['categories']
            
            # 1. Filtro por Categoria (nosso primeiro método)
            # 'explode' transforma a lista de categorias em linhas individuais
            # para facilitar o match
            kb_filtrado_idx = self.kb_df['categories'].explode().isin(categorias_aberta)
            kb_filtrado = self.kb_df[kb_filtrado_idx]
            
            melhor_match = None
            melhor_score = 0.0

            if not kb_filtrado.empty:
                # 2. Matching por Similaridade (nosso segundo método)
                
                # Obter os índices reais do DataFrame original para usar a matrix TF-IDF
                indices_filtrados = kb_filtrado.index
                
                # Vetorizar o texto da tarefa aberta
                vetor_aberto = self.vectorizer.transform([texto_aberto])
                
                # Calcular similaridade de cossenos apenas contra a base filtrada
                # Usamos os índices para fatiar a matrix principal
                matrix_filtrada = self.kb_matrix[self.kb_df.index.isin(indices_filtrados)]
                scores = cosine_similarity(vetor_aberto, matrix_filtrada)
                
                if scores.size > 0:
                    melhor_score_local = scores[0].max()
                    if melhor_score_local > 0.1: # Um limiar mínimo para ser sugestão
                        melhor_idx_local = scores[0].argmax()
                        melhor_match_global_idx = kb_filtrado.index[melhor_idx_local]
                        
                        melhor_match = self.kb_df.loc[melhor_match_global_idx]
                        melhor_score = melhor_score_local
            
            # Guardar o resultado
            resultados.append({
                'key_aberta': row_aberta['key'],
                'resumo_aberto': row_aberta['summary'],
                'categorias': categorias_aberta,
                'key_sugerida': melhor_match['key'] if melhor_match is not None else None,
                'solucao_sugerida': melhor_match['solution'] if melhor_match is not None else None,
                'similaridade': melhor_score
            })
        
        return pd.DataFrame(resultados)