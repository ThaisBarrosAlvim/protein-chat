#!/bin/bash

# Verifica se os argumentos necessários foram fornecidos
if [ $# -ne 2 ]; then
  echo "Uso: $0 <arquivo-zip> <nome-do-container>"
  exit 1
fi

# Atribui os argumentos a variáveis
ZIP_FILE=$1
CONTAINER_NAME=$2
TEMP_DIR=$(mktemp -d)  # Cria um diretório temporário

# Extrai o nome do arquivo zip (sem extensão)
ZIP_NAME=$(basename "$ZIP_FILE" .zip)

# Unzip o arquivo para o diretório temporário
echo "Extraindo $ZIP_FILE para $TEMP_DIR..."
unzip "$ZIP_FILE" -d "$TEMP_DIR" || { echo "Erro ao descompactar $ZIP_FILE"; exit 1; }

# Copia o conteúdo descompactado para o container Docker
echo "Copiando conteúdo para o container $CONTAINER_NAME:/backups/..."
docker cp "$TEMP_DIR/." "$CONTAINER_NAME:/backups/" || { echo "Erro ao copiar arquivos para o container"; exit 1; }

# Executa o curl para restaurar o backup
echo "Executando curl para restaurar o backup..."
curl -X POST -H "Content-Type: application/json" -d '{ "id": "'"$ZIP_NAME"'" }' "http://localhost:8080/v1/backups/filesystem/$ZIP_NAME/restore" || { echo "Erro ao realizar a solicitação de restauração"; exit 1; }

# Limpa o diretório temporário
echo "Limpando arquivos temporários..."
rm -rf "$TEMP_DIR"

echo "Processo concluído com sucesso."
