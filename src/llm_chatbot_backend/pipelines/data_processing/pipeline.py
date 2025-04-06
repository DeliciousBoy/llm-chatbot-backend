"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.19.12
"""

from kedro.pipeline import node, Pipeline, pipeline  # noqa
from .nodes import process_text, embed_forum_data, store_to_chroma


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=process_text,
                inputs="raw_forum_data",
                outputs="cleaned_forum_data",
                name="process_text_node",
            ),
            node(
                func=embed_forum_data,
                inputs="cleaned_forum_data",
                outputs="embedded_forum_data",
                name="embed_data_node",
            ),
            node(
                func=store_to_chroma,
                inputs={
                    "embedded_data": "embedded_forum_data",
                    "persist_path": "params:chroma_persist_path",
                },
                outputs="chroma_store",
                name="vector_db_node",
            ),
        ]
    )
