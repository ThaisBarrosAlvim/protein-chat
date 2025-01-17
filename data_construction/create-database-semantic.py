import json

import weaviate
from langchain.schema import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
from weaviate.collections.classes.config import DataType, Property, Configure


def save_docs_to_jsonl(array, file_path: str) -> None:
    with open(file_path, 'w') as jsonl_file:
        for doc in array:
            jsonl_file.write(doc.json() + '\n')


def ensure_utf8(text):
    return text.encode('utf-8', errors='replace').decode('utf-8')


def load_docs_from_jsonl(file_path):
    array = []

    with open(file_path, 'r', encoding='utf-8') as jsonl_file:
        lines = jsonl_file.readlines()

    for i, line in enumerate(lines):
        # Converte a linha para UTF-8, garantindo que todos os caracteres sejam válidos
        utf8_line = ensure_utf8(line)
        data = json.loads(utf8_line)
        results = Document(**data)
        array.append(results)

    return array


if __name__ == '__main__':
    # Carregar os documentos e aplicar a conversão
    docs = load_docs_from_jsonl('/home/thais/WorkSpaces/TCC/dabases-dumps/data_finish.jsonl')

    embeddings = HuggingFaceEmbeddings()
    text_splitter = SemanticChunker(embeddings, min_chunk_size=2000)
    split_docs = text_splitter.split_documents(docs)

    save_docs_to_jsonl(split_docs, '/home/thais/WorkSpaces/TCC/dabases-dumps/data_finish_semantic-2k.jsonl')

    weaviate_client = weaviate.connect_to_local()
    weaviate_client.collections.create(
        "ProteinCollectionSemantic2k",
        vectorizer_config=Configure.Vectorizer.text2vec_ollama(
            api_endpoint="http://ollama:11434",  # If using Docker, use this to contact your local Ollama instance
            model="mxbai-embed-large",  # The model to use, e.g. "nomic-embed-text"
        ),
        properties=[  # properties configuration is optional
            Property(name="title", data_type=DataType.TEXT, skip_vectorization=True),
            Property(name="body", data_type=DataType.TEXT),
            Property(name="page", data_type=DataType.INT, skip_vectorization=True),
            Property(name="doi", data_type=DataType.TEXT, skip_vectorization=True),
            Property(name="pk", data_type=DataType.TEXT, skip_vectorization=True),
            Property(name="proteins_structures", data_type=DataType.TEXT_ARRAY),
        ]
    )

    collection = weaviate_client.collections.get("ProteinCollectionSemantic2k")

    from tqdm import tqdm

    with collection.batch.dynamic() as batch:
        # Inicializa o progresso com tqdm
        for src_obj in tqdm(split_docs, desc="Processando documentos", unit="doc"):
            try:
                weaviate_obj = {
                    "pk": src_obj.metadata.get("id", ''),
                    "doi": src_obj.metadata.get("doi", ''),
                    "page": src_obj.metadata.get("page", ''),
                    "title": src_obj.metadata.get("title", ''),
                    "body": src_obj.page_content,
                    "proteins_structures": src_obj.metadata.get("proteins_structures", []),
                }

                batch.add_object(
                    properties=weaviate_obj,
                )
            except Exception as err:
                print(f'Error: {err}, on id {src_obj.metadata.get("id", "")}')
    weaviate_client.close()

    weaviate_client = weaviate.connect_to_local()
    result = weaviate_client.backup.create(
        backup_id="protein-articles-semantic-2k",
        backend="filesystem",
        include_collections=["ProteinCollectionSemantic2k", ],
        wait_for_completion=True,
    )

    print(result)

    weaviate_client.close()
