"""
app.py

Streamlit application for TravelSEA Advisor that provides travel recommendations
using RAG (Retrieval Augmented Generation) with vector storage and LLM.

Usage:
    streamlit run TravelSEA_app.py -- --config config.yaml
"""

import argparse
import sys
from pathlib import Path
import yaml
import streamlit as st
from utils.vector_storage import PGVectorDB
from langchain_openai import ChatOpenAI
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import os
from dotenv import load_dotenv
from pydantic import BaseModel
import json

# Load environment variables from .env file
load_dotenv()


class AppConfig(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    class Database(BaseModel):
        name: str
        host: str
        password: str
        username: str
        port: int
        table_name: str

    class EmbeddingModel(BaseModel):
        embed_model_name: str
        embed_dim: int

    class LLM(BaseModel):
        openai_model: str
        temperature: float

    database: Database
    embedding_model: EmbeddingModel
    llm: LLM


def load_config(config_path):
    """Load configuration from YAML file."""
    with open(config_path, "r") as f:
        config_dict = yaml.safe_load(f)
    return AppConfig(**config_dict)

def save_dict_to_json(file_path, new_data):
    # Check if the file exists
    if os.path.exists(file_path):
        # Load the existing data
        with open(file_path, "r") as file:
            try:
                data = json.load(file)
                # Ensure data is a list (to handle multiple dictionaries)
                if not isinstance(data, list):
                    data = [data]
            except json.JSONDecodeError:
                # If file is empty or contains invalid JSON, start with an empty list
                data = []
    else:
        # If file doesn't exist, start with an empty list
        data = []

    # Append the new dictionary to the list
    data.append(new_data)

    # Save the updated list back to the file
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)


def initialize_vector_db_engine(db_config, embedding_config):
    """Initialize connection to vector database."""
    vectordb = PGVectorDB(
        db_config.name,
        db_config.host,
        db_config.password,
        db_config.username,
        db_config.port,
        db_config.table_name,
        embed_dim=embedding_config.embed_dim,
    )

    llama_embedding_model = HuggingFaceEmbedding(
        model_name=embedding_config.embed_model_name
    )

    vectordb.build_index(llama_embedding_model)

    query_engine = vectordb.index.as_query_engine(
        vector_store_query_mode="hybrid", sparse_top_k=4
    )

    return query_engine


def get_rag_response(query: str, query_engine, llm) -> str:
    """
    Get response using RAG:
    1. Retrieve relevant documents
    2. Create prompt with context
    3. Get LLM response
    """
    # Retrieve relevant documents
    relevant_docs = query_engine.query(query)

    context = []
    for doc in relevant_docs.source_nodes:
        context.append(doc.text)

    context = "\n\n".join([doc for doc in context])

    # Create prompt with context
    prompt_template = """You are TravelSEA Advisor, an AI travel assistant specialized in sustainable tourism in Southeast Asia. 
        Use the following context to answer the question. If you cannot find the answer in the context, 
        say so politely and suggest what information might be helpful to better answer the question.
        
        Context: {context}
        
        Question: {query}
        
        Answer: """

    prompt = prompt_template.format(context=context, query=query)

    # Get LLM response
    response = llm.predict(prompt)

    return response


def main():
    # Parse command line arguments
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description="TravelSEA Advisor Streamlit App")
        parser.add_argument(
            "--config", required=True, help="Path to configuration file"
        )
        args = parser.parse_args()
        config = load_config(args.config)
    else:
        # Streamlit cloud deployment or local run without args
        config_path = Path(__file__).parent / "config.yaml"
        config = load_config(config_path)

    # Set page config
    st.set_page_config(page_title="🌏 TravelSEA Advisor", page_icon="🌏", layout="wide")

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        st.error(
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
        )
        st.stop()

    # Initialize components
    query_engine = initialize_vector_db_engine(config.database, config.embedding_model)

    llm = ChatOpenAI(
        api_key=openai_api_key,
        model=config.llm.openai_model,
        temperature=config.llm.temperature,
    )

    # Application header
    st.title("🌏 TravelSEA Advisor")
    st.markdown(
        """
    Welcome to TravelSEA Advisor! This application helps you plan your journey through Southeast Asia
    by providing personalized travel recommendations with a focus on sustainable tourism.
    
    Ask any questions about:
    - 🏰 Places to visit
    - 🍜 Local cuisine
    - 🎨 Cultural experiences
    - 🌿 Sustainable travel options
    - 📅 Best times to visit
    - 💡 Travel tips
    """
    )

    # User input
    user_question = st.text_input(
        "What would you like to know about traveling in Southeast Asia?",
        placeholder="e.g., What are the must-visit temples in Cambodia?",
    )

    json_feedback_path = "../feedback.json"
    # Add a button to submit the question
    if st.button("Get Recommendations"):
        if user_question:
            try:
                with st.spinner("Generating recommendations..."):
                    response = get_rag_response(user_question, query_engine, llm)

                # Display the response
                st.markdown("### 📝 Recommendations")
                st.write(response)

                answer_dic = {"question": user_question, "answer": response}
                # Add feedback buttons
                col1, col2, _ = st.columns([1, 1, 3])
                with col1:
                    if st.button("👍 Helpful"):
                        answer_dic["feedback"] = "helpful"
                        save_dict_to_json(json_feedback_path, answer_dic)
                        st.success("Thank you for your feedback!")
                with col2:
                    if st.button("👎 Not Helpful"):
                        answer_dic["feedback"] = "not helpful"
                        save_dict_to_json(json_feedback_path, answer_dic)
                        st.info(
                            "Thank you for your feedback! We'll work on improving our responses."
                        )

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a question.")

    # Footer with information about the project
    st.markdown("---")
    st.markdown(
        """
    #### About TravelSEA Advisor
    TravelSEA Advisor uses advanced AI technology to provide accurate and relevant travel information 
    about Southeast Asian countries. The recommendations are based on curated content from reliable 
    travel sources, with a focus on sustainable and responsible tourism.
    
    The application uses RAG (Retrieval Augmented Generation) to ensure responses are grounded in 
    factual information about the region.
    
    For more information about the project, visit our [GitHub repository](https://github.com/M4riaLoureiro/ethical-travel-recommender).
    """
    )


if __name__ == "__main__":
    main()
