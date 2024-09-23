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
        response = qa_chain(user_message)["result"]

        return jsonify({'response': response})

    except Exception as e:
        print('error: ', e,'\n\n', traceback.format_exc())
        error_message = str(e)
        error_trace = traceback.format_exc()

        return jsonify({
            'error': 'Ocorreu um erro ao processar a solicitação.',
            'message': error_message,
            'trace': error_trace
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
