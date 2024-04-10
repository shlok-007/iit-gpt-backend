import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain_community.vectorstores import Chroma

import constants

os.environ["OPENAI_API_KEY"] = constants.APIKEY

print("\nLoading saved index...\n")
vectorstore = Chroma(persist_directory="/var/www/prod-iit-gpt-backend/persist", embedding_function=OpenAIEmbeddings())
index = VectorStoreIndexWrapper(vectorstore=vectorstore)

chain = ConversationalRetrievalChain.from_llm(
  llm=ChatOpenAI(model="gpt-3.5-turbo"),
  retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
  rephrase_question=True
)

print("\n\n\n\n----------Server Started with  GPT-4---------------\n\n\n\n")

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

@app.route('/', methods=['GET'])
@limiter.limit("10 per minute")
def index():
    return 'IIT GPT is live!'

@app.route('/query', methods=['POST'])
@limiter.limit("10 per minute")  # Allow only 10 requests per minute
def query():
    data = request.json
    query = data.get('query')
    chat_history = data.get('chat_history', [])
    chat_history = [tuple(sublist) for sublist in chat_history]

    if not query:
        return jsonify({'error': 'Query parameter is missing.'}), 400

    result = chain({"question": query, "chat_history": chat_history})

    return jsonify(result)

if __name__ == '__main__':
    app.run()
