from llama_index.core import Settings
from llama_index.core.indices.vector_store.base import VectorStoreIndex
from llama_index.core.schema import TextNode
from llama_index.core.storage.storage_context import StorageContext
from llama_index.vector_stores.postgres import PGVectorStore


class PGVectorDB:

    def __init__(
        self,
        db_name,
        host,
        password,
        username,
        port,
        table_name,
        hybrid_search=True,
        embed_dim=1024,
    ):

        self.vector_store = PGVectorStore.from_params(
            database=db_name,
            host=host,
            password=password,
            port=port,
            user=username,
            table_name=table_name,
            hybrid_search=hybrid_search,
            text_search_config="english",
            embed_dim=embed_dim,
        )

    def build_index(self, embedding_model):

        Settings.embed_model = embedding_model

        self.storage_context = StorageContext.from_defaults(
            vector_store=self.vector_store
        )

        self.index = VectorStoreIndex.from_documents(
            [], storage_context=self.storage_context
        )

    def add_document(self, document):

        llama_node = TextNode(
            text=document["content"],
            metadata=document["metadata"],
            id_=document["metadata"]["document_id"],
        )

        self.index.insert_nodes([llama_node])
