import os
import sys

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import openai
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma

import constants

os.environ["OPENAI_API_KEY"] = constants.APIKEY

# Initializing the index
PERSIST = True

if PERSIST and os.path.exists("persist"):
  print("Reusing index...\n")
  vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
  index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
  #loader = TextLoader("data/data.txt") # Use this line if you only need data.txt
  loader = DirectoryLoader("data/")
  if PERSIST:
    index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
  else:
    index = VectorstoreIndexCreator().from_loaders([loader])

chain = ConversationalRetrievalChain.from_llm(
  llm=ChatOpenAI(model="gpt-3.5-turbo"),
  retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
)

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains
limiter = Limiter(app, key_func=get_remote_address)  # Rate limiter

@app.route('/', methods=['GET'])
def index():
    return 'Hello, World!'

@app.route('/query', methods=['POST'])
@limiter.limit("10 per minute")  # Allow only 10 requests per minute
def query():
    data = request.json
    query = data.get('query')
    chat_history = data.get('chat_history', [])

    if not query:
        return jsonify({'error': 'Query parameter is missing.'}), 400

    result = chain({"question": query, "chat_history": chat_history})

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=False)
