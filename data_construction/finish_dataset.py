import json

def convert_json_to_jsonl(input_json_file, output_jsonl_file):
    """
    Converte um arquivo JSON contendo uma lista de objetos em um arquivo JSONL.

    Args:
        input_json_file (str): O caminho do arquivo JSON de entrada.
        output_jsonl_file (str): O caminho do arquivo JSONL de saída.
    """
    try:
        # Abrir e carregar o arquivo JSON
        with open(input_json_file, 'r') as json_file:
            data = json.load(json_file)

        # Verificar se o dado carregado é uma lista
        if isinstance(data, list):
            # Abrir o arquivo JSONL para escrita
            with open(output_jsonl_file, 'w') as jsonl_file:
                # Escrever cada objeto da lista em uma linha separada
                for obj in data:
                    jsonl_file.write(json.dumps(obj) + '\n')
            print(f"Conversão para JSONL concluída. Arquivo salvo como {output_jsonl_file}.")
        else:
            print("O arquivo JSON não contém uma lista.")
    except FileNotFoundError:
        print(f"Arquivo {input_json_file} não encontrado.")
    except json.JSONDecodeError:
        print(f"Erro ao decodificar o arquivo JSON {input_json_file}.")

# Exemplo de uso
if __name__ == '__main__':
    input_json_file = 'dataset_protein_articles.json'  # Arquivo JSON de entrada
    output_jsonl_file = 'dataset_protein_articles.jsonl'  # Arquivo JSONL de saída

    convert_json_to_jsonl(input_json_file, output_jsonl_file)
