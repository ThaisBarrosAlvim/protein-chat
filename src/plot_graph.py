import weaviate
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
from weaviate.collections.classes.grpc import MetadataQuery

# Conectando ao cliente Weaviate local
weaviate_client = weaviate.connect_to_local()
try:
    collection = weaviate_client.collections.get("ProteinCollection")

    # Realizando a busca
    response = collection.query.hybrid(
        query="what is mobile loop ?",
        return_metadata=MetadataQuery(score=True, explain_score=True, distance=True, is_consistent=True),
        limit=30,
        include_vector=True,
    )

    # Coletando os vetores retornados
    vectors = []
    for o in response.objects:
        vectors.append(o.vector['default'])  # Adicionando cada vetor à lista

    # Convertendo a lista para um array numpy
    vectors = np.array(vectors)

    # Reduzindo para 2D usando t-SNE (ou você pode usar PCA se preferir)
    tsne = TSNE(n_components=2, perplexity=20, random_state=42)  # Ajustando perplexity para 2
    reduced_vectors = tsne.fit_transform(vectors)

    # Plotando os vetores reduzidos
    plt.figure(figsize=(8, 6))
    plt.scatter(reduced_vectors[:, 0], reduced_vectors[:, 1], color='blue')

    # Adicionando títulos e labels para o gráfico
    plt.title('Plot of Vectors Returned from Weaviate Search (t-SNE Reduced)')
    plt.xlabel('Dimension 1')
    plt.ylabel('Dimension 2')

    # Exibir o gráfico
    plt.show()
finally:
    # Fechando a conexão
    weaviate_client.close()
