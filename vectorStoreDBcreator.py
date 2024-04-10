import os

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from time import time

import constants

os.environ["OPENAI_API_KEY"] = constants.APIKEY

t1 = time()
text_loader_kwargs={'autodetect_encoding': True}
loader = DirectoryLoader("text_data/", glob="**/*.txt", loader_cls=TextLoader, show_progress=True, use_multithreading=True, silent_errors=True, loader_kwargs=text_loader_kwargs)
print("Loader Initialized.")
documents = loader.load()
print("Documents Loaded in ", time()-t1)
t1 = time()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
texts = text_splitter.split_documents(documents)
print("Text Splitted in ", time()-t1)

persist_directory = 'persist'

## here we are using OpenAI embeddings but in future we will swap out to local embeddings
t1 = time()
embedding = OpenAIEmbeddings()
print("Creating index")
vectordb = Chroma.from_documents(documents=texts,
                                embedding=embedding,
                                persist_directory=persist_directory)
print("Index created in ", time()-t1)
