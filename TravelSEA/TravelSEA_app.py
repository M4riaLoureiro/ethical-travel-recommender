"""
app.py

Streamlit application for TravelSEA Advisor that provides travel recommendations
using RAG (Retrieval Augmented Generation) with vector storage and LLM.

Usage:
    streamlit run app.py -- --config config.yaml
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

# Load environment variables from .env file
load_dotenv()


def load_config(config_path):
    """Load configuration from YAML file."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config


def initialize_vector_db_engine(db_config, embedding_config):
    """Initialize connection to vector database."""

    vectordb = PGVectorDB(
        db_config["name"],
        db_config["host"],
        db_config["password"],
        db_config["username"],
        db_config["port"],
        db_config["table_name"],
        embed_dim=embedding_config["embed_dim"],
    )

    llama_embedding_model = HuggingFaceEmbedding(
        model_name=(embedding_config["model_name"])
    )

    vectordb.build_index(llama_embedding_model)

    query_engine = vectordb.index.as_query_engine(
        vector_store_query_mode="hybrid", sparse_top_k=4
    )

    return query_engine


def get_rag_response(query, query_engine, llm):
    """
    Get response using RAG:
    1. Retrieve relevant documents
    2. Create prompt with context
    3. Get LLM response
    """
    # Retrieve relevant documents
    relevant_docs = query_engine.query(query)

    context = []
    for doc in relevant_docs:
        for source in doc.source_nodes:
            context.append(source.text)

    # Create prompt with context
    prompt = f"""You are a helpful travel assistant for Southeast Asia. 
    Use the following pieces of information to answer the user's question.
    If you don't know the answer based on the provided context, say so.
    
    Context:
    {' '.join([text for text in context])}
    
    Question: {query}
    
    Answer:"""

    # Get LLM response
    response = llm.predict(prompt)

    return response, relevant_docs


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
    st.set_page_config(page_title="TravelSEA Advisor", page_icon="🌏", layout="wide")

    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        st.error(
            "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable."
        )
        st.stop()

    # Initialize components
    print(config["embedding_model"])
    query_engine = initialize_vector_db_engine(
        config["database"], config["embedding_model"]
    )

    llm = ChatOpenAI(
        api_key=openai_api_key,
        model=config["llm"]["openai_model"],
        temperature=config["llm"]["temperature"],
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

    # Add a button to submit the question
    if st.button("Get Answer"):
        if user_question:
            try:
                with st.spinner("Searching for information..."):
                    response, relevant_docs = get_rag_response(
                        user_question, query_engine, llm
                    )

                # Display the response
                st.markdown("### Answer")
                st.write(response)

                # Optionally show relevant sources
                with st.expander("View Sources"):
                    for i, doc in enumerate(relevant_docs, 1):
                        st.markdown(f"**Source {i}:**")
                        st.markdown(doc.text)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a question.")

    # Footer with information about the project
    st.markdown("---")
    st.markdown(
        """
    ### About this project
    TravelSEA Advisor uses advanced AI technology to provide accurate and relevant travel information 
    about Southeast Asian countries. The recommendations are based on curated content from reliable 
    travel sources, with a focus on sustainable and responsible tourism.
    
    The application uses RAG (Retrieval Augmented Generation) to ensure responses are grounded in 
    factual information about the region.
    """
    )


if __name__ == "__main__":
    main()
