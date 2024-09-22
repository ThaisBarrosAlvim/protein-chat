from flask import Flask, render_template, request, jsonify
import chatbot  # Aqui você importa o arquivo que manipula o modelo local

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/message", methods=["POST"])
def get_bot_response():
    user_message = request.json['msg']  # Pega a mensagem enviada pelo usuário
    response = chatbot.get_response_from_local_model(user_message)  # Usa o modelo local para gerar a resposta
    return jsonify({'response': response})

if __name__ == "__main__":
    app.run(debug=True)
