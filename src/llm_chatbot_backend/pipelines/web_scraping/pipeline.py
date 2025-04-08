from kedro.pipeline import node, Pipeline, pipeline  # noqa
from .nodes import run_scraping_pipeline


def create_pipeline(**kwargs) -> Pipeline:
    return Pipeline(
        [
            node(
                func=run_scraping_pipeline,
                inputs="params:web_scraping",
                outputs="raw_forum_data",
                name="scraping_node",
            ),
        ]
    )
