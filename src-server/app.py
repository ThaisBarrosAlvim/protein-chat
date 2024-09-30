import requests
from flask import Flask, render_template, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/message", methods=["POST"])
def get_bot_response():
    try:
        # Obtém a mensagem do usuário
        user_message = request.json['msg']

        # Faz a requisição POST para a API com o JSON contendo a mensagem
        api_url = "http://frp.protein-chat.space/message"
        headers = {'Content-Type': 'application/json'}
        payload = {'msg': user_message}

        # Envia a requisição para a API
        response = requests.post(api_url, json=payload, headers=headers)

        # Verifica se a requisição foi bem-sucedida
        if response.status_code == 200:
            # Retorna a resposta da API
            return jsonify(response.json())
        else:
            return jsonify(response.json()), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
