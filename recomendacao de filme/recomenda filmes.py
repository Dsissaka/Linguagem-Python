import re
import pandas as pd
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

def prepara_arquivo(dados):
    palavras_remover = ["the", "as", "and", "from", "of", "by", "for", "or", "a"]
    
    for coluna in dados.columns:
        dados[coluna] = dados[coluna].astype(str).apply(lambda linha: re.sub(r'[^\w\s;]', '', linha))
        dados[coluna] = dados[coluna].apply(lambda linha: ' '.join([palavra for palavra in linha.split() if palavra.lower() not in palavras_remover]))
    
    return dados

def monta_grafo(arquivo, pesos):
    aux = pd.read_csv(arquivo)
    aux = prepara_arquivo(aux)
    dados_filtrados = aux[['show_id', 'title','type', 'director', 'cast', 'country', 'rating', 'listed_in', 'description']]

    for coluna in ['show_id', 'title', 'type', 'director', 'cast', 'country', 'rating', 'listed_in', 'description']:
        dados_filtrados[coluna] = dados_filtrados[coluna].fillna('')

    dados_filtrados['features'] = (
        dados_filtrados['type'] + " " * int(pesos['type']) +
        dados_filtrados['title'] + " " * int(pesos['title']) +
        dados_filtrados['director'] + " " * int(pesos['director']) +
        dados_filtrados['cast'] + " " * int(pesos['cast']) +
        dados_filtrados['country'] + " " * int(pesos['country']) +
        dados_filtrados['rating'] + " " * int(pesos['rating']) +
        dados_filtrados['listed_in'] + " " * int(pesos['listed_in']) +
        dados_filtrados['description'] + " " * int(pesos['description'])
    )

    vetorizer = TfidfVectorizer()
    vetor_semelhanca = vetorizer.fit_transform(dados_filtrados['features'])

    similaridade = cosine_similarity(vetor_semelhanca)

    grafo = nx.Graph()

    for idx, row in aux.iterrows():
        grafo.add_node(row['show_id'], title=row['title'])

    lim_min_similaridade = 0.1
    for i in range(similaridade.shape[0]):
        for j in range(i + 1, similaridade.shape[1]):
            if similaridade[i, j] > lim_min_similaridade:
                grafo.add_edge(aux.iloc[i]['show_id'], aux.iloc[j]['show_id'], weight=similaridade[i, j])

    return grafo

def recomenda_filmes(grafo, filme, filhos):
    vizinhos = sorted(
        grafo[filme].items(),
        key=lambda x: x[1]['weight'],
        reverse=True
    )
    
    recomendacoes = [(grafo.nodes[v[0]]['title'], v[1]['weight']) for v in vizinhos[:filhos]]
    return recomendacoes

def main():
    
    pesos = {
        'type': 3,
        'title': 3,
        'director': 1,
        'cast': 3,
        'country': 0.5,
        'rating': 2,
        'listed_in': 5,
        'description': 5
    }
    arquivo = 'C:/Users/issak/OneDrive/Área de Trabalho/Issaka/UFGD/Engenharia da Computação/Trabalhos/Teoria Dos Grafos/Trabalho 2/disney_plus_titles.csv'
    grafo = monta_grafo(arquivo, pesos)

    filme_id = 's' + input("qual o id do filme base para recomendacao: ") 
    if filme_id not in grafo:
        print("valor invalido")
    else:
        filhos = int(input("qual a quantidade de filhos para o grafo? "))
        recomendacoes = recomenda_filmes(grafo, filme_id, filhos)
        if recomendacoes:
            print("\nrecomendacao baseada no filme selecionado:")
            for titulo, peso in recomendacoes:
                print(f" - {titulo} (similaridade: {peso:.2f})")

if __name__ == "__main__":
    main()
