import logging
import traceback
from flask import Flask, render_template, request, jsonify
import chatbot  # Aqui você importa o arquivo que manipula o modelo local

app = Flask(__name__)

db_size_divided, db_semantic_divided = chatbot.load_databases()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/message", methods=["POST"])
def get_bot_response():
    try:
        # get vars
        user_message = request.json['msg']
        config = request.json['config']

        # Database config
        db = config.get('db', 'size-divided')
        if db == 'size-divided':
            database = db_size_divided
        else: # semantic-divided
            database = db_semantic_divided

        # Search type config
        search_type = config.get('searchType', 'hybrid')
        if search_type == 'hybrid':  # keyword search and vector search
            alpha = 0.5
        elif search_type == 'vector-similarity':  # vector search
            alpha = 1
        else:  # keyword search
            alpha = 0

        qtd_docs = config.get('docsQtd', 20)
        model_name = config.get('model', chatbot.VALID_MODELS[0])
        used_config = {
            'db': db,
            'model': model_name,
            'docsQtd': qtd_docs,
            'searchType': search_type,
            # 'history': qtd_docs, # TODO implement
        }
        qa_chain = chatbot.setup_retrieval_chain(database, qtd_docs=qtd_docs, alpha=alpha,
                                                 model_name=model_name)

        # Retrieve Augmented Generation occurs here:
        response = qa_chain.invoke({"input": user_message})

        # Format response
        context = []
        for i, doc in enumerate(response['context']):
            context.append({
                'id': i,
                'proteins_structures': ", ".join(doc.metadata["proteins_structures"]),
                'page': doc.metadata["page"],
                'title': doc.metadata.get("title", "").strip(),
                'doi': doc.metadata.get("doi", ""),
                'content': doc.page_content
            })

        return jsonify({'result': response["answer"], 'context': context, 'used_config': used_config})

    except Exception as e:
        logging.error(f'Error in API message: {e}', exc_info=True)
        error_message = str(e)
        error_trace = traceback.format_exc()

        return jsonify({
            'error': 'An error occurred while processing the request.',
            'message': error_message,
            'trace': error_trace
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
