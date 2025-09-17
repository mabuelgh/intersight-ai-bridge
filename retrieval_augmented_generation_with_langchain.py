# SPDX-License-Identifier: Apache-2.0
"""
Retrieval Augmented Generation (RAG) Implementation with Langchain
==================================================================
This script demonstrates a RAG implementation using LangChain, Milvus and vLLM.
RAG enhances LLM responses by retrieving relevant context from a document collection.

Features:
- Local folder content loading and chunking for multiple files
- Vector storage with Milvus
- Embedding generation with vLLM
- Question answering with context

Prerequisites:
1. Install dependencies:
   pip install -U vllm \
               langchain_milvus langchain_openai \
               langchain_community beautifulsoup4 \
               langchain-text-splitters
2. Ensure your Docker Compose services are running:
   docker-compose up -d

Usage:
python retrieval_augmented_generation_with_langchain_offline.py --directory-path /path/to/your/documents/folder

Notes:
- The script now uses the vLLM services defined in your docker-compose.yml.
- `vllm-embedded-llm` serves embeddings on `http://localhost:8001/v1` (host port 8001) with model name `rag`.
- `vllm` serves chat on `http://localhost:8000/v1` (host port 8000) with model name `Phi-4-mini-instruct`.
- **Make sure the specified directory exists and contains the files you want to process.**
- By default, it will load all `.txt` files in the directory and its subdirectories. You can adjust the `glob` pattern or `loader_cls` for other file types.
- The Milvus URI (`./milvus_demo.db`) assumes a local file-based Milvus instance. If you plan to containerize Milvus, this URI will need further adjustment.
"""
import argparse
from argparse import Namespace
from typing import Any

# Changed import for local folder loading
from langchain_community.document_loaders import DirectoryLoader, TextLoader # Added DirectoryLoader
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_milvus import Milvus
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


# Modified function to load from a local directory path
def load_and_split_documents(config: dict[str, Any]):
    """Load and split documents from a local directory path"""
    try:
        # Use DirectoryLoader to load all files from the specified directory.
        # loader_cls specifies which loader to use for each file (e.g., TextLoader for .txt).
        # glob specifies a pattern to match files (e.g., "**/*.txt" for all text files recursively).
        loader = DirectoryLoader(
            config["directory_path"],
            glob="**/*.txt",  # Adjust this glob pattern for specific file types (e.g., "*.pdf", "*.md")
            loader_cls=TextLoader, # Use TextLoader for all matched files
            recursive=True # Set to True to search subdirectories
        )
        docs = loader.load()
        if not docs:
            print(f"Warning: No documents found in {config['directory_path']} matching the glob pattern.")
            return []

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config["chunk_size"],
            chunk_overlap=config["chunk_overlap"],
        )
        splits = text_splitter.split_documents(docs)
        return splits
    except FileNotFoundError:
        print(f"Error: Directory not found at {config['directory_path']}. Please check the path.")
        return []
    except Exception as e:
        print(f"Error loading and splitting documents: {e}")
        return []


def create_vector_store(splits: list[Document], config: dict[str, Any]):
    """Create a vector store from document splits"""
    try:
        embeddings = OpenAIEmbeddings(
            model=config["embedding_model"],
            openai_api_base=config["embedding_api_base"],
            openai_api_key="sk-no-key-required",
        )
        vector_store = Milvus.from_documents(
            documents=splits,
            embedding=embeddings,
            collection_name=config["collection_name"],
            connection_args={"uri": config["milvus_uri"]},
        )
        return vector_store
    except Exception as e:
        print(f"Error creating vector store: {e}")
        return None


def setup_rag_chain(vector_store: Milvus, config: dict[str, Any]):
    """Set up the RAG chain"""
    try:
        retriever = vector_store.as_retriever()
        llm = ChatOpenAI(
            model=config["chat_model"],
            openai_api_base=config["chat_api_base"],
            temperature=0,
            openai_api_key="sk-no-key-required",
        )

        template = """Answer the question based on the following context in priority then search outside:
{context}

Question: {question}
"""
        prompt = PromptTemplate.from_template(template)

        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )
        return rag_chain
    except Exception as e:
        print(f"Error setting up RAG chain: {e}")
        return None


def run_rag_query(rag_chain, query: str):
    """Run a query through the RAG chain"""
    try:
        response = rag_chain.invoke(query)
        return response
    except Exception as e:
        print(f"Error running RAG query: {e}")
        return "An error occurred during query processing."


def parse_arguments() -> Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Retrieval Augmented Generation with Langchain (Offline Document Parsing)"
    )
    # Changed argument from --file-path to --directory-path
    parser.add_argument(
        "--directory-path",
        type=str,
        required=True, # Made required as it's the primary input now
        help="Path to the local directory containing documents (e.g., /home/user/my_docs)",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Chunk size for text splitting",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Chunk overlap for text splitting",
    )
    parser.add_argument(
        "--embedding-model",
        type=str,
        # Updated to match your docker-compose for embedding model
        default="/app/model/rag",
        help="Embedding model name",
    )
    parser.add_argument(
        "--embedding-api-base",
        type=str,
        # Updated to use the Docker service name for the embedding LLM
        default="http://localhost:8001/v1",
        help="Embedding service API base URL",
    )
    parser.add_argument(
        "--chat-model",
        type=str,
        # Updated to match your docker-compose for chat model
        default="/app/model/",
        help="Chat model name",
    )
    parser.add_argument(
        "--chat-api-base",
        type=str,
        # Updated to use the Docker service name for the chat LLM
        default="http://localhost:8000/v1",
        help="Chat service API base URL",
    )
    parser.add_argument(
        "--milvus-uri",
        type=str,
        default="./milvus_demo.db",
        help="Milvus connection URI",
    )
    parser.add_argument(
        "--collection-name",
        type=str,
        default="rag_collection",
        help="Milvus collection name",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    config = vars(args)  # Convert Namespace to dict for easier access

    print(f"Loading and splitting documents from directory: {config['directory_path']}...")
    splits = load_and_split_documents(config)
    if not splits:
        print("No documents loaded or split. Exiting.")
        return
    print(f"Successfully loaded and split {len(splits)} document chunks.")

    print("Creating vector store...")
    vector_store = create_vector_store(splits, config)
    if not vector_store:
        print("Failed to create vector store. Exiting.")
        return

    print("Setting up RAG chain...")
    rag_chain = setup_rag_chain(vector_store, config)
    if not rag_chain:
        print("Failed to set up RAG chain. Exiting.")
        return

    while True:
        query = input("\nEnter your query (type 'exit' to quit): ")
        if query.lower() == "exit":
            break
        if not query.strip():
            continue

        print("\nRunning RAG query...")
        response = run_rag_query(rag_chain, query)
        print("\nResponse:")
        print(response)


if __name__ == "__main__":
    main()