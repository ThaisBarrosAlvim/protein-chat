import weaviate
import time
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.llms.ollama import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaEmbeddings
from langchain_weaviate import WeaviateVectorStore


def benchmark_model(model_name, ollama_base_url, weaviate_host, num_docs):

    prompt = """
        1. Use the following pieces of context to answer the question at the end.
        2. If you don't know the answer, just say "I don't know" but don't make up an answer on your own.
        3. Keep the answer crisp and limited to 3-4 sentences.
                
        Context: {context}
        
        Question: {question}
        
        After the answer, always say the source and page.
        Helpful Answer:
    """

    # Capturando o tempo de início
    start_time = time.time()

    # Configurando o LLM e o cliente Weaviate
    llm = Ollama(model=model_name, base_url=ollama_base_url)
    weaviate_client = weaviate.Client(weaviate_host)
    db = WeaviateVectorStore(client=weaviate_client, index_name='ProteinCollection',
                             embedding=OllamaEmbeddings(model="mxbai-embed-large", base_url=ollama_base_url),
                             text_key='body')

    # Configurando o retriever com o número de documentos a serem buscados
    retriever = db.as_retriever(search_kwargs={'k': num_docs, 'alpha': 0.5})

    # Definindo o template do prompt para a chain
    qa_chain_prompt = PromptTemplate.from_template(prompt)

    llm_chain = LLMChain(
        llm=llm,
        prompt=qa_chain_prompt,
        callbacks=None,
        verbose=True
    )

    # Template para formatar os documentos individualmente
    document_prompt = PromptTemplate(
        input_variables=["page_content", "title", "page"],
        template="Context:\ncontent:{page_content}\nsource:{title}\npage:{page}",
    )

    # Combinando os documentos para o LLM chain
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_variable_name="context",
        document_prompt=document_prompt,
        callbacks=None,
    )

    # Configurando a chain de QA com o retriever e o combinador de documentos
    qa = RetrievalQA(
        combine_documents_chain=combine_documents_chain,
        verbose=True,
        retriever=retriever,
        return_source_documents=True,
    )

    # Executando a consulta e benchmark
    question = "What is the role of magnesium in protein binding?"
    response = qa.run(question)

    # Capturando o tempo de fim
    end_time = time.time()

    # Calculando o tempo total de execução
    total_time = end_time - start_time

    return response, total_time


if __name__ == '__main__':
    # Parâmetros de exemplo para a chamada
    model_name = "qwen:4b"  # Nome do modelo que você deseja usar no Ollama
    ollama_base_url = "http://ollama:11434"  # URL base onde o serviço Ollama está rodando
    weaviate_host = "weaviate"  # Host onde o Weaviate está rodando
    num_docs = 1  # Número de documentos a serem recuperados pelo retriever

    # Chamada da função
    response, total_time = benchmark_model(model_name, ollama_base_url, weaviate_host, num_docs)

    # Exibição da resposta e do tempo de execução
    print("Resposta:", response['result'])
    print(f"Tempo total de execução: {total_time:.2f} segundos")
