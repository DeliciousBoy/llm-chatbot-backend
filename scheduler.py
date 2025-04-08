import logging
import subprocess

from apscheduler.schedulers.blocking import BlockingScheduler

logger = logging.getLogger(__name__)


def run_kedro_pipeline():
    logger.info("Running Kedro pipeline...")
    try:
        subprocess.run(
            ["kedro", "run", "--pipeline", "web_scraping"],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running Kedro pipeline: {e}")


if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(run_kedro_pipeline, trigger="interval", minutes=1)
    logger.info("Scheduler started. Running Kedro pipeline every minute.")
    scheduler.start()
