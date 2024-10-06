"""
init_vector_db.py

This script initializes the vector database for the TravelSEA Advisor application.
It processes PDF documents, creates embeddings, and stores them in a PostgreSQL database.
Processed documents are cached to avoid reprocessing.

Usage:
    python prep.py --config config.yaml
"""

import argparse
import pickle
from pathlib import Path

import psycopg2
import yaml
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from tqdm import tqdm

# from marker.logger import configure_logging
# from marker.models import load_all_models
from utils.process_and_index_documents import (
    download_and_process_pdf_file,
    list_pdf_files,
)
from utils.vector_storage import PGVectorDB


class VectorDBInitializer:
    """Handles the initialization of the vector database."""

    def __init__(self, db_config, processing_config):
        self.db_config = db_config
        self.processing_config = processing_config

        # Initialize splitters
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=processing_config["chunk_size"],
            chunk_overlap=processing_config["chunk_overlap"],
        )

        self.markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
        )

    def setup_database(self):
        """Creates a fresh database for vector storage."""
        try:
            conn = psycopg2.connect(
                host=self.db_config["host"],
                user=self.db_config["username"],
                password=self.db_config["password"],
                database="postgres",
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

            with conn.cursor() as cursor:
                cursor.execute(f"DROP DATABASE IF EXISTS {self.db_config['name']}")
                cursor.execute(f"CREATE DATABASE {self.db_config['name']}")

            print(f"Database {self.db_config['name']} created successfully")

            conn.close()
        except psycopg2.Error as e:
            print(f"Database setup failed: {str(e)}")
            raise

    def process_documents(self):
        """Process all PDF documents or load from cache if available."""
        cache_path = (
            Path(self.processing_config["data_directory"]) / "docs_processed.pickle"
        )

        # Check if cached processed documents exist
        if cache_path.exists():
            print("Found cached processed documents. Loading from cache...")
            try:
                with open(cache_path, "rb") as f:
                    documents = pickle.load(f)
                print(f"Successfully loaded {len(documents)} documents from cache")
                return documents
            except Exception as e:
                print(f"Error loading cached documents: {str(e)}")
                print("Proceeding with document processing...")

        # Process documents if no cache exists or loading cache failed
        try:
            filenames = list_pdf_files(self.processing_config["data_directory"])
            print(f"Found {len(filenames)} PDF files to process")

            configure_logging()
            model_lst = load_all_models()
            documents = []

            for filename in tqdm(filenames, desc="Processing documents"):
                print(f"Processing file: {filename}")
                splitted_doc = download_and_process_pdf_file(
                    filename,
                    self.text_splitter,
                    self.markdown_splitter,
                    model_lst,
                    reference_folder=self.processing_config["data_directory"],
                )
                documents.extend(splitted_doc)

            # Cache the processed documents
            print("Caching processed documents...")
            try:
                with open(cache_path, "wb") as f:
                    pickle.dump(documents, f)
                print("Successfully cached processed documents")
            except Exception as e:
                print(f"Error caching documents: {str(e)}")

            return documents
        except Exception as e:
            print(f"Document processing failed: {str(e)}")
            raise

    def initialize_vector_db(self, documents):
        """Initialize and populate the vector database."""
        try:
            vectordb = PGVectorDB(
                self.db_config["name"],
                self.db_config["host"],
                self.db_config["password"],
                self.db_config["username"],
                self.db_config["port"],
                self.db_config["table_name"],
            )

            embedding_model = HuggingFaceEmbedding(
                model_name=self.processing_config["embedding_model_name"]
            )
            vectordb.build_index(embedding_model)

            for doc in tqdm(documents, desc="Adding documents to vector DB"):
                vectordb.add_document(doc)

            print("Vector database initialization completed successfully")
        except Exception as e:
            print(f"Vector database initialization failed: {str(e)}")
            raise


def load_config(config_path):
    """Load configuration from YAML file."""
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config["database"], config["processing"]


def main():
    parser = argparse.ArgumentParser(
        description="Initialize vector database for TravelSEA Advisor"
    )
    parser.add_argument("--config", required=True, help="Path to configuration file")
    args = parser.parse_args()

    try:
        # Load configuration
        db_config, processing_config = load_config(args.config)

        # Initialize and run the database setup
        initializer = VectorDBInitializer(db_config, processing_config)

        # Setup fresh database
        print("Setting up database...")
        initializer.setup_database()

        # Process documents or load from cache
        print("Starting document processing or loading from cache...")
        documents = initializer.process_documents()

        # Initialize vector database
        print("Initializing vector database...")
        initializer.initialize_vector_db(documents)

        print("Vector database initialization completed successfully")

    except Exception as e:
        print(f"Initialization failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
