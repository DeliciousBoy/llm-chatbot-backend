from kedro.pipeline import node, Pipeline, pipeline  # noqa
from .nodes import scraping


def create_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=scraping,
                inputs=None,
                outputs="raw_forum_data",
                name="scrape_forum_data",
            ),
        ]
    )
