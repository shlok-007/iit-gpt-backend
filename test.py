import os
import sys

# import openai
from langchain.chains import ConversationalRetrievalChain
# from langchain.chains import ConversationalRetrievalChain, RetrievalQA
# from langchain_community.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
# from langchain_community.document_loaders import DirectoryLoader, TextLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
# from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
# from langchain_community.llms import OpenAI
from langchain_community.vectorstores import Chroma
# from time import time

import constants

os.environ["OPENAI_API_KEY"] = constants.APIKEY

# Enable to save to disk & reuse the model (for repeated queries on the same data)
# PERSIST = True

query = None
if len(sys.argv) > 1:
  query = sys.argv[1]

# if PERSIST and os.path.exists("db"):
#   print("Reusing index...\n")

vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
index = VectorStoreIndexWrapper(vectorstore=vectorstore)


# else:
#   #loader = TextLoader("data/data.txt") # Use this line if you only need data.txt
#   t1 = time()
#   text_loader_kwargs={'autodetect_encoding': True}
#   loader = DirectoryLoader("text_data/", glob="**/*.txt", loader_cls=TextLoader, show_progress=True, use_multithreading=True, silent_errors=True, loader_kwargs=text_loader_kwargs)
#   print("Loader Initialized.")
#   documents = loader.load()
#   print("Documents Loaded in ", time()-t1)
#   t1 = time()
#   text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#   texts = text_splitter.split_documents(documents)
#   print("Text Splitted in ", time()-t1)

#   persist_directory = 'db'

#   ## here we are using OpenAI embeddings but in future we will swap out to local embeddings
#   t1 = time()
#   embedding = OpenAIEmbeddings()
#   print("Creating index")
#   vectordb = Chroma.from_documents(documents=texts,
#                                   embedding=embedding,
#                                   persist_directory=persist_directory)
#   print("Index created in ", time()-t1)

#   # print("Document Loaded.")
#   if PERSIST:
#     print("\n\n\n\n --------------creating and storing index----------------------\n\n\n\n")
#     index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
#   else:
#     index = VectorstoreIndexCreator().from_loaders([loader])

chain = ConversationalRetrievalChain.from_llm(
  llm=ChatOpenAI(model="gpt-4"),
  retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
  # rephrase_question=True
)

chat_history = []
while True:
  if not query:
    query = input("Prompt: ")
  if query in ['quit', 'q', 'exit']:
    sys.exit()
  result = chain({"question": query, "chat_history": chat_history})
  print(result['answer'])

  chat_history.append((query, result['answer']))
  query = None