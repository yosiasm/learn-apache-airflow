Install DB and Apache Airflow
1. Change your directory to scraperv2
2. Run ```docker-compose up``` for install elasticsearch, postgres, apache airflow
3. Change your directory to scraperv2/postgres_init_scripts
4. Run ```psql -h localhost -p 5433 -U airflow -d news_datamart -f postgres_init.sql``` for create database table

Install Task Docker Image
1. Change your directory to task-image/news_scraper
2. Build task image by running ```docker build -t news_scraper_task .```
3. Start your DAG in ```localhost:8080```

Install Dashboard
1. Change your directory to dashboard
2. Install dependencies by running ```pip install -r requirements.txt```
3. Run ```streamlit run main.py```
4. Streamlit will redirect you into your browser