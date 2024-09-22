from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain

def load_retriever():
    embeddings = HuggingFaceEmbeddings()
    qdrant = QdrantVectorStore.from_existing_collection(
        embedding=embeddings,
        collection_name="protein_data",
        url="http://localhost:6333",
    )
    retriever = qdrant.as_retriever(search_type="similarity", search_kwargs={"k": 20})
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
    llm = Ollama(model="mistral")
    retriever = load_retriever()

    QA_CHAIN_PROMPT = PromptTemplate.from_template(prompt)

    # Create an LLM chain with the prompt template
    llm_chain = LLMChain(
        llm=llm,
        prompt=QA_CHAIN_PROMPT,
        callbacks=None,
        verbose=True
    )

    # Define how individual documents are formatted
    document_prompt = PromptTemplate(
        input_variables=["page_content", "source", "page"],
        template="Context:\ncontent:{page_content}\nsource:{source}\npage:{page}",
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

def get_response_from_local_model(user_input):
    qa = setup_qa_chain()
    print(f'question: {user_input}')
    return qa(user_input)["result"]
