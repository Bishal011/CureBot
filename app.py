


from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.chains import create_retrieval_chain
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from src.helper import download_hugging_face_embeddings
from src.prompt import system_prompt
import os
import requests

app = Flask(__name__)

# Load environment variables
load_dotenv()
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
GROK_API_KEY = os.environ.get("GROK_API_KEY")

# Validate environment variables
if not PINECONE_API_KEY:
    raise ValueError("Pinecone API key missing in .env file.")
if not GROK_API_KEY:
    raise ValueError("Grok API key missing in .env file.")

# Load embedding model
embeddings = download_hugging_face_embeddings()

# Define index name
index_name = "medicalbot"

# Use LangChain Pinecone wrapper compatible with Pinecone v3
docsearch = PineconeVectorStore(
    index_name=index_name,
    embedding=embeddings,
    pinecone_api_key=PINECONE_API_KEY
)

# Set up retriever
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Groq API call
def groq_api_call(prompt, api_key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "messages": [{"role": "user", "content": prompt}],
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

# Prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

# Process chain
def grok_chain(input_text):
    retrieved_docs = retriever.invoke(input_text)
    context = "\n".join([doc.page_content for doc in retrieved_docs])
    complete_prompt = system_prompt.format(context=context) + f"\n\nUser's question: {input_text}"
    response = groq_api_call(complete_prompt, GROK_API_KEY)
    if response:
        return response['choices'][0]['message']['content']
    return "Sorry, I couldn't retrieve an answer."

# Routes
@app.route("/")
def index():
    return render_template("chart.html")

# # chart operation
@app.route("/get", methods=["POST"])
def chat():
    msg = request.form.get("msg")
    input_text = msg
    print(f"Received query: {input_text}")

    try:
        result = grok_chain(input_text)  # Get the response from grok_chain
        print("Response:", result)

        # Return the result as JSON
        return jsonify({"response": result})  # Send back the response to the frontend
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request."}), 500

    

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)


