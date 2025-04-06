"""
This is a boilerplate pipeline 'data_processing'
generated using Kedro 0.19.12
"""

from kedro.pipeline import node, Pipeline, pipeline  # noqa
from .nodes import process_text


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=process_text,
                inputs="raw_forum_data",
                outputs="cleaned_forum_data",
                name="process_text_node",
            )
        ]
    )
