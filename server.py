import os
import sys

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import openai
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_openai import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain_community.llms import OpenAI
from langchain_community.vectorstores import Chroma

import constants

os.environ["OPENAI_API_KEY"] = constants.APIKEY

# Initializing the index
PERSIST = True

if PERSIST and os.path.exists("/var/www/prod-iit-gpt-backend/persist"):
  print("Reusing index...\n")
  vectorstore = Chroma(persist_directory="/var/www/prod-iit-gpt-backend/persist", embedding_function=OpenAIEmbeddings())
  index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
  #loader = TextLoader("data/data.txt") # Use this line if you only need data.txt
  loader = DirectoryLoader("/var/www/iit-gpt-backend/data/")
  if PERSIST:
    index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
  else:
    index = VectorstoreIndexCreator().from_loaders([loader])

chain = ConversationalRetrievalChain.from_llm(
  llm=ChatOpenAI(model="gpt-4"),
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
