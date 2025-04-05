"""
This is a boilerplate pipeline 'web_scraping'
generated using Kedro 0.19.12
"""

from kedro.pipeline import node, Pipeline, pipeline  # noqa
from .nodes import test


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=test,
                inputs=None,
                outputs="forum_raw_data",
                name="scrape_forum_data",
            ),
        ]
    )
