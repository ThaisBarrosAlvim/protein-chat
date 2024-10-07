import json
import os
import logging
from collections.abc import Iterable
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import ollama
from tqdm import tqdm  # Importando tqdm para a barra de progresso


# Função para carregar os documentos do arquivo JSONL
def load_docs_from_jsonl(file_path):
    array = []
    with open(file_path, 'r') as jsonl_file:
        for line in jsonl_file:
            data = json.loads(line)
            obj = Document(**data)
            array.append(obj)
    return array


# Função para criar perguntas e respostas usando o modelo LLM
def create_qa(content):
    response = ollama.chat(model='llama3.1:8b-instruct-q4_0', format='json', messages=[
        {
            'role': 'system',
            'content': 'You are an API that converts bodies of text into a list of 1 to 5 different questions and answers about technical info into a JSON format. Each item in this array '
                       'contains a single question with a single answer. Only respond with the JSON and no additional text. Do not generate questions about specific info like names, institutions or references.'
                       'Questions should include all context needed to understand. Do not create questions like this: "What is the purpose of this article/<article name>?" '
                       'Answers must have as much possible of context, do not answer with just one phrase. '
                       'Format exemple: {"result": [{"question": "a list of strings", "answer": "a list of strings"}, {"question": "a list of strings", "answer": "a list of strings"}, {"question": "a list of strings", "answer": "a list of strings"} ]}',
        },
        {
            'role': 'user',
            'content': (
                           f'This is a part of article named: {content.metadata["Title"]}\n' if "Title" in content.metadata else "") + content.page_content + f'\n\nRespond only with valid JSON'
        },
    ])
    try:
        created_qa = json.loads(response['message']['content']).get('result')
        if (not isinstance(created_qa, Iterable)
                or not all(set(c.keys()) == {'answer', 'question'} and
                           isinstance(c['answer'], str) and isinstance(c['question'], str)
                           for c in created_qa)):
            logging.warning(f'Invalid format generated: "{created_qa}"')
            created_qa = {}
    except Exception as err:
        logging.error(f'Error while loading json: "{str(err)}", response: {response["message"]["content"]}')
        created_qa = {}

    return created_qa


# Função para carregar o progresso do arquivo de log
def load_log():
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, 'r') as log_file:
            return json.load(log_file)
    return {'last_processed_index': 0}


# Função para salvar o progresso no arquivo de log
def save_log(index):
    with open(LOG_FILE_PATH, 'w') as log_file:
        json.dump({'last_processed_index': index}, log_file)
    logging.info(f'Saved progress at index {index}')


# Função para salvar os dados processados no arquivo JSON
def save_output(data):
    # Carrega os dados existentes, se o arquivo já existir
    if os.path.exists(OUTPUT_FILE_PATH):
        with open(OUTPUT_FILE_PATH, 'r') as output_file:
            existing_data = output_file.readlines()
        # Remove quebras de linha e converte as strings JSON em objetos
        existing_data = [json.loads(line) for line in existing_data]
    else:
        existing_data = []

    # Extende os dados existentes com os novos dados
    existing_data.extend(data)

    # Abre o arquivo para escrever no formato JSONL
    with open(OUTPUT_FILE_PATH, 'w') as output_file:
        for obj in existing_data:
            output_file.write(json.dumps(obj) + '\n')

    logging.info(f'Saved chunk of data to {OUTPUT_FILE_PATH}')


# Função principal para processar os documentos em lotes de 100
def process_documents(docs, start_index):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=4000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(docs)

    # Calcula o total de batches
    total_batches = (len(split_docs) - start_index) // CHUNK_SIZE + 1

    # Usando tqdm para criar uma barra de progresso para os batches
    with tqdm(total=total_batches, desc="Processing Batches", unit="batch") as pbar:
        for i in range(start_index, len(split_docs), CHUNK_SIZE):
            batch = split_docs[i:i + CHUNK_SIZE]

            generated_qas = []

            # Barra de progresso para os chunks dentro de cada batch
            with tqdm(total=len(batch), desc=f"Processing Chunks in Batch {i // CHUNK_SIZE + 1}",
                      unit="chunk") as chunk_bar:
                for chunk in batch:
                    generated_qas.extend(create_qa(chunk))
                    # Atualiza a barra de progresso dos chunks
                    chunk_bar.update(1)

            transformed_data = [
                {
                    'instruction': item['question'],
                    'input': '',
                    'output': item['answer']
                }
                for item in generated_qas
            ]

            # Salvar o progresso e os dados processados
            save_output(transformed_data)
            save_log(i + CHUNK_SIZE)

            logging.info(f'Processed batch ending at index {i + CHUNK_SIZE}')

            # Atualiza a barra de progresso dos batches
            pbar.update(1)

    logging.info('Processing completed.')


# Configuração do logging
logging.basicConfig(
    filename='create_dataset.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('ollama').setLevel(logging.WARNING)

# Caminho dos arquivos
LOG_FILE_PATH = 'create_dataset_log.json'
OUTPUT_FILE_PATH = 'dataset_protein_articles.jsonl'
CHUNK_SIZE = 100

if __name__ == '__main__':
    # Carregar os documentos e o progresso do log
    docs = load_docs_from_jsonl('data_finish.jsonl')
    log_data = load_log()
    start_index = log_data.get('last_processed_index', 0)

    if start_index > 0:
        logging.info(f'Resuming from index {start_index}')

    # Processar os documentos a partir do ponto onde o script foi interrompido
    process_documents(docs, start_index)
