# Protein Chatbot: Retrieval-based Q&A on Magnesium-binding Protein Structures

[![](https://raw.githubusercontent.com/ThaisBarrosAlvim/protein-chat/main/src/static/images/protein-chat-webpage.png)](https://github.com/ThaisBarrosAlvim/protein-chat)

* [Live Demo](http://protein-chat.space)
-----------------

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codebeat badge](https://codebeat.co/badges/22def691-1b91-4fa4-86fa-8791769512ee)](https://codebeat.co/projects/github-com-thaisbarrosalvim-protein-chat-main)

This project provides a chatbot that leverages AI models for answering questions related to protein structures with magnesium-binding sites. It processes a dataset of **7,613 articles** from the **[RCSB PDB](https://www.rcsb.org/)**, each detailing a protein structure with magnesium sites. These articles are processed using a **[RecursiveCharacterTextSplitter](https://api.python.langchain.com/en/latest/character/langchain_text_splitters.character.RecursiveCharacterTextSplitter.html)** from the Langchain library and stored in **[Weaviate](https://weaviate.io/)**, a vector database optimized for similarity searches.

The system uses **[Ollama](https://ollama.com/)** (running the **[llama3.1 model](https://ollama.com/library/llama3.1)**) to perform natural language processing and generate human-like responses. The chatbot is built with **[Flask](https://github.com/pallets/flask)** for the web interface and uses **[Gunicorn](https://github.com/benoitc/gunicorn)** as the WSGI server, making it highly scalable and efficient.

## Table of Contents
1. [Overview](#overview)
2. [Features](#features)
3. [Requirements](#requirements)
4. [Setup](#setup)
5. [Usage](#usage)
6. [Future Improvements](#future-improvements)
7. [Contributing](#contributing)
8. [License](#license)

## Overview

This application uses **Langchain**, **Weaviate**, and **Ollama** models to answer questions based on pre-loaded protein data. It retrieves similar contexts from the Weaviate vector store and uses Ollama for generating human-like responses. The setup also includes a Flask web application for user interaction.

## Features

- **Flask Web App**: Provides a simple user interface to interact with the chatbot.
- **Retrieval-Based Q&A**: Uses Weaviate to retrieve the most relevant information and responds with concise, accurate answers.
- **AI-Powered Responses**: Ollama model (Mistral) is used for generating natural language answers.
- **Weaviate Dashboard**: View and manage the vector store via a dashboard.

## Requirements
- **Linux OS**: This project requires a Linux-based system to ensure compatibility with NVIDIA GPU support and other dependencies.
- **Docker**: For containerizing and running services.
- **NVIDIA GPU**: Requires Docker to be configured with NVIDIA GPU support.

## Setup

Follow these steps to set up and run the project on your local machine:

### 1. Install NVIDIA Container Toolkit for GPU Support

Follow the [official NVIDIA installation guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html#installation) to set up GPU support in Docker.

### 2. Clone the Repository

```bash
git clone https://github.com/ThaisBarrosAlvim/protein-chat.git
cd protein-chat
```

### 3. Build and Run the Docker Containers

Use Docker Compose to set up the Weaviate, Ollama, and Flask services:

```bash
docker compose up --build
```

This command will build and start the Weaviate, Ollama, and Flask services.

### 4. Load the Protein Data Snapshot into Weaviate

Once Weaviate is running, follow these steps to load the dataset:

1. Download the snapshot file [protein-articles4.zip](https://drive.google.com/file/d/1cNFL05dGc6pe14Irzj7_bp-cX3uUUHbP/view?usp=sharing).
2. Run the following script to restore the dataset:

   ```bash
   sudo sh scripts/weaviate-restore-backup.sh protein-articles4.zip protein-chat-weaviate-1
   ```

## Usage

Once the setup is complete, open your browser and go to `http://localhost:8000` to interact with the chatbot. Type in a question related to protein data, and the system will retrieve relevant information from the Weaviate vector store and generate an answer using the Ollama model.

### API Endpoints

- `/`: The homepage where users can interact with the chatbot.
- `/message`: The POST endpoint to send questions and receive responses.

## Future Improvements

1. **Prompt Engineering Enhancements**:
    - Refine the prompts sent to the Ollama model to improve the consistency and accuracy of responses. This includes testing various phrasing techniques and adjusting the context length to ensure the system handles a wider range of questions effectively.

2. **CPU Support for Docker-Compose**:
    - Create a `docker-compose-cpu.yml` file to run without GPU support, enabling the project to function on platforms other than Linux, including macOS and Windows. This will broaden the availability of the project and make it accessible to more users.

3. **Accessible Context for Users**:

   3.1 **Download PDFs from Context**:
    - Allow users to download the PDFs that the system used as context to formulate the answers. This will ensure users have direct access to the sources for further exploration.

   3.2 **Context Highlight in PDFs**:
    - Implement a feature that marks the exact sections used in the answer directly within the PDF viewer on the web page. Users can visually see which part of the document contributed to the response.

4. **Model Selection for Querying**:
    - Enable users to choose the language model that will be used to answer their queries. This allows more flexibility and customization depending on the needs or preferences of the user.

5. **Selective Context PDFs**:
    - Give users the ability to choose which PDFs from the dataset should be used as context for answering questions. This way, users can narrow down the context or focus on specific documents they deem most relevant.

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue for any feature suggestions or bug fixes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

