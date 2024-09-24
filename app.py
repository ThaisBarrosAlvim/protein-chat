import traceback
from flask import Flask, render_template, request, jsonify
import chatbot  # Aqui você importa o arquivo que manipula o modelo local

app = Flask(__name__)

qa_chain = chatbot.setup_qa_chain()
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/message", methods=["POST"])
def get_bot_response():
    try:
        # Obtém a mensagem do usuário
        user_message = request.json['msg']

        # Obtém a resposta do modelo
        response = qa_chain(user_message)

        return jsonify({
            'result': response["result"],
            'context': [
                {
                    'id': i,
                    'file': doc.metadata["file_path"].split("/")[-1],
                    'page': doc.metadata["page"],
                    'title': doc.metadata.get("Title", "").strip(),
                    'doi': doc.metadata.get("doi", ""),
                    'content': doc.page_content
                } for i, doc in enumerate(response['source_documents'])
            ]
        })
    except Exception as e:
        error_message = str(e)
        error_trace = traceback.format_exc()

        return jsonify({
            'error': 'An error occurred while processing the request.',
            'message': error_message,
            'trace': error_trace
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
