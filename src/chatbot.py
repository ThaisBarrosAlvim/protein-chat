import weaviate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain_ollama import OllamaEmbeddings
from langchain_weaviate.vectorstores import WeaviateVectorStore


def load_retriever():
    # TODO client creation must happen when question arrive
    weaviate_client = weaviate.connect_to_local(host='weaviate')
    db = WeaviateVectorStore(client=weaviate_client, index_name='ProteinCollection',
                             embedding=OllamaEmbeddings(model="mxbai-embed-large", base_url='http://ollama:11434'),
                             text_key='body')
    retriever = db.as_retriever(search_kwargs={'k': 20, 'alpha': 0.5})
    return retriever

def setup_qa_chain():
    prompt = """
    1. Use the following pieces of context to answer the question at the end.
            2. If you don't know the answer, just say "I don't know" but don't make up an answer on your own.
            3. Keep the answer crisp and limited to 3-4 sentences.
            
            Context: {context}
            
            Question: {question}
            
            After the answer, always say the source and page.
            Helpful Answer:
    """
    llm = Ollama(model="llama3", base_url='http://ollama:11434')
    retriever = load_retriever()

    qa_chain_prompt = PromptTemplate.from_template(prompt)

    llm_chain = LLMChain(
        llm=llm,
        prompt=qa_chain_prompt,
        callbacks=None,
        verbose=True
    )

    # Define how individual documents are formatted
    document_prompt = PromptTemplate(
        input_variables=["page_content", "title", "page"],
        template="Context:\ncontent:{page_content}\nsource:{title}\npage:{page}",
    )

    # Combine documents into a single context for the LLM chain
    combine_documents_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_variable_name="context",
        document_prompt=document_prompt,
        callbacks=None,
    )

    # Set up the RetrievalQA chain with the retriever and document combiner
    qa = RetrievalQA(
        combine_documents_chain=combine_documents_chain,
        verbose=True,
        retriever=retriever,
        return_source_documents=True,
    )
    return qa