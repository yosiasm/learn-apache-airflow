from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.operators.docker_operator import DockerOperator
import logging

default_args = {
    "owner": "airflow",
    "description": "news scraper using docker operator",
    "depend_on_past": False,
    "start_date": datetime(2022, 9, 27),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# with DAG('docker_operator_demo', default_args=default_args, schedule_interval="5 * * * *", catchup=False) as dag:


@dag(
    dag_id="News_Scraper_DAG",
    schedule_interval="@hourly",
    catchup=False,
    default_args=default_args,
)
def taskflow():
    health_check = DockerOperator(
        task_id="healthcheck",
        image="news_scraper_task",
        container_name="news_scraper_task_runner",
        api_version="auto",
        auto_remove=True,
        command="python3 health_check.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="scraperv2_default",
    )
    scrap = []
    for spider in [
        "antaranews",
        "beritapagi",
        "bisnisindonesia",
        "bukamatanews",
        "detiknews",
        "haluan",
        "jawapos",
        "kabarpapua",
        "kompas",
        "koransindo",
        "liputan6",
        "majalahinvestor",
        "mediaindonesia",
        "metrotvnews",
        "oposisicerdas",
        "papuainews",
        "pikiranrakyat",
        "poskota",
        "rakyatmerdeka",
        "republika",
        "rmol",
        "seputarpapua",
        "suaramerdeka",
        "tempo",
        "viva",
    ]:
        scrap.append(
            DockerOperator(
                task_id=f"scrap_{spider}",
                image="news_scraper_task",
                container_name=f"news_scraper_task_runner_{spider}",
                api_version="auto",
                auto_remove=True,
                command=f"python3 scrap_news.py {spider}",
                docker_url="unix://var/run/docker.sock",
                network_mode="scraperv2_default",
            )
        )

    load_to_datamart = DockerOperator(
        task_id="elastic_to_postgres",
        image="news_scraper_task",
        container_name="news_scraper_task_runner_load_to_datamart",
        api_version="auto",
        auto_remove=True,
        command="python3 elastic_to_postgres.py",
        docker_url="unix://var/run/docker.sock",
        network_mode="scraperv2_default",
    )

    health_check >> scrap >> load_to_datamart


dag = taskflow()
