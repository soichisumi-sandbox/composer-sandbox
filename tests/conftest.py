import os

import pytest

tests_directory = os.path.dirname(os.path.realpath(__file__))
airflow_home = os.path.join(tests_directory, "airflow_home")
print(f'test_dir: {tests_directory}\nairflow_home: {airflow_home}')
# os.environ["AIRFLOW__CORE__DAGS_FOLDER"] = os.path.join(tests_directory, "dags")
os.environ["AIRFLOW__CORE__UNIT_TEST_MODE"] = "True"
os.environ["AIRFLOW_HOME"] = airflow_home
os.environ["AIRFLOW_CONFIG"] = "unittests.cfg"
os.environ["AIRFLOW_VAR_PROJECT_ID"] = "project_id"
os.environ["AIRFLOW_VAR_KEY"] = "VAL"


@pytest.fixture(scope="session", autouse=True)
def init_db():
    from airflow.utils import db
    # print("Attempting to reset the db using airflow command")
    # os.system("airflow resetdb -y")
    db.resetdb({})
