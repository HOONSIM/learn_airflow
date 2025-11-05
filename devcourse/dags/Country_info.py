import requests
from airflow import DAG
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
import logging

def get_Redshift_connection(autocommit=True):
    hook = PostgresHook(postgres_conn_id='redshift_dev_db')
    conn = hook.get_conn()
    conn.autocommit = autocommit
    return conn.cursor()

@task
def extract_transform():
    response = requests.get("https://restcountries.com/v3.1/all?fields=name,area,population")
    countries = response.json()
    records = []

    for country in countries:
        name = country['name']['common']
        population = country['population']
        area = country['area']

        records.append([name, population, area])
    
    return records


@task
def load(schema, table, records):
    logging.info("load started")
    cur = get_Redshift_connection()
    try:
        cur.execute("BEGIN;")
        cur.execute(f"DROP TABLE IF EXISTS {schema}.{table};")
        cur.execute(f"""
            CREATE TABLE {schema}.{table} (
                name varchar(256) primary key,
                population int,
                area float
                );
            """)
        # DELETE FROM을 먼저 수행 -> FULL REFRESH을 하는 형태
        for r in records:
            sql = f"INSERT INTO {schema}.{table} VALUES ('{r[0]}', {r[1]}, {r[2]});"
            print(sql)
            cur.execute(sql)
        cur.execute("COMMIT;")   # cur.execute("END;")
    except Exception as error:
        print(error)
        cur.execute("ROLLBACK;")
        raise

    logging.info("load done")


with DAG(
    dag_id = 'CountryInfo',
    start_date = datetime(2025,11,4),
    catchup=False,
    tags=['API'],
    schedule = '30 6 * * 6'
) as dag:

    results = extract_transform()
    load("simhoon1023", "country_info", results)