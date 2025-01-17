import json
import random


def shuffle_and_truncate_jsonl(input_file, output_file, limit):
    data = []

    # Abrir o arquivo JSONL e carregar os dados
    with open(input_file, 'r') as infile:
        for line in infile:
            data.append(json.loads(line.strip()))

    # Embaralhar os dados
    random.shuffle(data)

    # Truncar os dados até o limite escolhido
    truncated_data = data[:limit]

    # Salvar os dados truncados no arquivo de saída
    with open(output_file, 'w') as outfile:
        for entry in truncated_data:
            json.dump(entry, outfile)
            outfile.write('\n')


# Exemplo de uso
input_file = 'dataset_protein_articles.jsonl'
output_file = 'dataset_protein_articles_trunc.jsonl'
limit = 1500  # Número de linhas truncadas

shuffle_and_truncate_jsonl(input_file, output_file, limit)
