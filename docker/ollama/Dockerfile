FROM ollama/ollama

# Copia o script shell para o container
COPY ./docker/ollama/run_ollama.sh /tmp/run_ollama.sh

# Define o diretório de trabalho
WORKDIR /tmp

# Dá permissão de execução ao script
RUN chmod +x run_ollama.sh

# Expõe a porta 11434
EXPOSE 11434

# Define o script como entrypoint
ENTRYPOINT ["/tmp/run_ollama.sh"]
