from os import path
from airflow import models

DAG_DIR = path.join(path.dirname(__file__), "..", "composer_sandbox")

# ref: https://github.com/godatadriven/airflow-testing-examples/blob/master/tests/dags/test_dag_integrity.py
# ref2: https://airflow.apache.org/docs/apache-airflow/1.10.15/best-practices.html#testing-a-dag
def test_dags():
    dagbag = models.DagBag(dag_folder=DAG_DIR, include_examples=False)

    assert dagbag.import_errors == {}
    assert len(dagbag.dags) is 2

    for dag in dagbag.dags:
        assert dag is not None
