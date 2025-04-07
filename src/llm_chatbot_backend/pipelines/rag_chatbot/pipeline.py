"""
This is a boilerplate pipeline 'rag_chatbot'
generated using Kedro 0.19.12
"""

from kedro.pipeline import node, Pipeline, pipeline  # noqa
from .nodes import retrieve_relevant_documents


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=retrieve_relevant_documents,
                inputs=[
                    "params:user_query",
                    "params:embedding_model",
                    "params:chroma_persist_path",
                ],
                outputs=None,
                name="retrieve_node",
            ),
        ]
    )
