import weaviate
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaEmbeddings
from langchain_weaviate.vectorstores import WeaviateVectorStore

VALID_MODELS = ('llama3.1:8b',)
OLLAMA_BASE_URL = 'http://ollama:11434'


def load_databases():
    # TODO client creation must happen when question arrive
    weaviate_client = weaviate.connect_to_local(host='weaviate')
    embedding = OllamaEmbeddings(model="mxbai-embed-large", base_url=OLLAMA_BASE_URL)

    db_size_divided = WeaviateVectorStore(client=weaviate_client, index_name='ProteinCollection',
                                          embedding=embedding,
                                          text_key='body')
    db_semantic_divided = WeaviateVectorStore(client=weaviate_client, index_name='ProteinCollectionSemantic',
                                              embedding=embedding,
                                              text_key='body')

    db_semantic_divided2k = WeaviateVectorStore(client=weaviate_client, index_name='ProteinCollectionSemantic2k',
                                                embedding=embedding,
                                                text_key='body')
    return db_size_divided, db_semantic_divided, db_semantic_divided2k


def setup_retriever(database, qtd_docs, alpha=0.5):
    return database.as_retriever(search_kwargs={'k': qtd_docs, 'alpha': alpha})


def setup_retrieval_chain(database, qtd_docs, alpha, model_name):
    assert model_name in VALID_MODELS, 'Invalid model name: {}'.format(model_name)

    llm = Ollama(model=model_name, base_url=OLLAMA_BASE_URL)
    retriever = setup_retriever(database, qtd_docs, alpha)

    system_prompt = """
            1. Use the following pieces of context to answer the question at the end.
            2. If you don't know the answer, just say "I don't know" but don't make up an answer on your own.
            3. Keep the answer crisp and limited to 3-4 sentences.
            
            Context: {context}"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )

    # Define how individual documents are formatted
    document_prompt = PromptTemplate(
        input_variables=["page_content", "title", "page"],
        template="Context:\ncontent:{page_content}\nsource:{title}\npage:{page}",
    )

    # Combine documents into a single context for the LLM chain
    combine_documents_chain = create_stuff_documents_chain(llm=llm, prompt=prompt,
                                                           document_prompt=document_prompt,
                                                           document_variable_name='context')
    retrieval_chain = create_retrieval_chain(retriever, combine_documents_chain)

    return retrieval_chain
