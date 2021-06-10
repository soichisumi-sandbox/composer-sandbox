import os

from airflow import configuration
import pytest

tests_directory = os.path.dirname(os.path.realpath(__file__))
airflow_home = os.path.join(tests_directory, "airflow_home")
print(f'test_dir: {tests_directory}\nairflow_home: {airflow_home}')
# os.environ["AIRFLOW__CORE__DAGS_FOLDER"] = os.path.join(tests_directory, "dags")
os.environ["AIRFLOW__CORE__UNIT_TEST_MODE"] = "True"
os.environ["AIRFLOW_HOME"] = airflow_home
os.environ["AIRFLOW_CONFIG"] = "unittests.cfg"
os.environ["AIRFLOW_VAR_PROJECT_ID"] = "project_id"
# os.environ["AIRFLOW_VAR_KEY"] = "VAL"

testConf = {
    "key": "val"
}
for k, v in testConf.items():
    setattr(configuration.conf, k, v)


@pytest.fixture(scope="session", autouse=True)
def init_db():
    from airflow.utils import db
    # print("Attempting to reset the db using airflow command")
    # os.system("airflow resetdb -y")
    db.resetdb({})


# XCOM
from unittest.mock import patch

import pytest
from airflow.models.taskinstance import TaskInstance

XCOM_RETURN_KEY = 'return_value'
xcom_dict = dict()


@pytest.fixture(scope="session", autouse=True)
def init_test_xcom():
    global xcom_dict
    xcom_dict = {
        generate_xcom_key(key="xcomkey"): "xcomvalue"
    }


def generate_xcom_key(task_ids=None, key=XCOM_RETURN_KEY):
    return f'{task_ids}-{key}'


# @pytest.fixture
# def mock_xcom_pull():
#     def func(
#             self,
#             task_ids=None,
#             dag_id=None,
#             key=XCOM_RETURN_KEY,
#             include_prior_dates=False):
#         return xcom_dict[generate_xcom_key(task_ids=task_ids, key=key)]
#
#     with patch(TaskInstance, 'xcom_pull', func) as mock_pull:
#         yield mock_pull
#
#
# @pytest.fixture
# def mock_xcom_push():
#     def func(
#             self,
#             key,
#             value,
#             execution_date=None):
#         xcom_dict[generate_xcom_key(task_ids=task_ids, key=key)] = value
#
#     with patch(TaskInstance, 'xcom_push', func) as mock_push:
#         yield mock_push


def mock_xcom_pull(
        self,
        task_ids=None,
        dag_id=None,
        key=XCOM_RETURN_KEY,
        include_prior_dates=False):
    return xcom_dict[generate_xcom_key(task_ids=task_ids, key=key)]


def mock_xcom_push(
        self,
        key,
        value,
        execution_date=None):
    xcom_dict[generate_xcom_key(task_ids=task_ids, key=key)] = value
