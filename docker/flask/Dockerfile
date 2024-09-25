# Usa uma imagem base com Python
FROM python:3.9-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Copia os arquivos de requisitos para o container
COPY ./src/requirements.txt requirements.txt

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante dos arquivos da aplicação para o container
COPY ./src .

# Expõe a porta 8000 para o Gunicorn
EXPOSE 5000

# Define o comando para rodar o Gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "app:app"]