import os
import time
from os import path
from unittest import mock
from unittest.mock import patch

import pytest
from airflow import models, settings, configuration
from airflow.models import DagRun, TaskInstance
from airflow.executors.debug_executor import DebugExecutor
from airflow.utils import state
from airflow.utils.timezone import datetime
from pytest_mock import MockerFixture
from sqlalchemy.orm.session import Session as SASession
from typing import List

from tests import conftest

DAG_DIR = path.join(path.dirname(__file__), "..", "composer_sandbox")
DEFAULT_DATE = datetime(2020, 1, 1)


# ref: https://github.com/godatadriven/airflow-testing-examples/blob/master/tests/dags/test_dag_integrity.py
# ref2: https://airflow.apache.org/docs/apache-airflow/1.10.15/best-practices.html#testing-a-dag
def test_dags():
    dagbag = models.DagBag(dag_folder=DAG_DIR, include_examples=False)  # type: models.DagBag

    assert dagbag.import_errors == {}
    assert len(dagbag.dags) is 2

    for k, v in dagbag.dags.items():
        assert k is not None
        assert v is not None
        print(f'k: {k}, v: {v}')


def test_dag_sample_w_template_actual_run():
    dagbag = models.DagBag(dag_folder=DAG_DIR, include_examples=False)
    dag = dagbag.get_dag(dag_id="dag_sample_w_template")  # type: models.DAG

    dag.run(
        start_date=DEFAULT_DATE,
        ignore_first_depends_on_past=True,
        verbose=True,
        executor=DebugExecutor(),
    )

    session = settings.Session()  # type: SASession
    dagruns = session.query(DagRun) \
        .filter(DagRun.dag_id == dag.dag_id) \
        .order_by(DagRun.execution_date) \
        .all()  # type: List[models.DagRun]

    assert len(dagruns) == 1
    assert dagruns[0].execution_date == DEFAULT_DATE
    assert dagruns[0].state == state.State.SUCCESS


# c = Client(None, None)
# c.trigger_dag(dag_id=dag.dag_id, run_id='test_run_id', execution_date=DEFAULT_DATE, conf={})
# def cond() -> bool:

# executor = MockExecutor()
# job = BackfillJob(
#     dag=dag,
#     executor=executor,
#     start_date=DEFAULT_DATE,
#     end_date=DEFAULT_DATE,
#     ignore_first_depends_on_past=True,
# )
# job.run()

# @pytest.mark.skip()
def test_dag_sample_w_template_mock(mocker: MockerFixture, mock_xcom_pull, mock_xcom_push):
    # Besides undoing the mocking automatically after the end of the test
    # https://github.com/pytest-dev/pytest-mock#pytest-mock
    mocker.patch.object(TaskInstance, 'xcom_pull', mock_xcom_pull)
    mocker.patch.object(TaskInstance, 'xcom_push', mock_xcom_push)

    dagbag = models.DagBag(dag_folder=DAG_DIR, include_examples=False)
    dag = dagbag.get_dag(dag_id="dag_sample_w_template")  # type: models.DAG

    dagrun = dag.create_dagrun(
        run_id="run_id",
        state=state.State.RUNNING,
        execution_date=DEFAULT_DATE,
        conf=configuration.conf
    )

    for t in dagrun.dag.tasks:
        ti = TaskInstance(task=t, execution_date=DEFAULT_DATE)

        # print(f'ctx: {ctx}')
        print(
            f'taskid: {ti.task_id}, \
            privide_context: {ti.task.provide_context if hasattr(ti.task, "provide_context") else "False"} \
            callable: {ti.task.python_callable.__name__ if hasattr(ti.task, "python_callable") else "False"} \
            bash_command: {ti.task.bash_command if hasattr(ti.task, "bash_command") else "False"}'
        )

        # if hasattr(ti.task, "provide_context"):
        ti.render_templates()

        print(
            f'taskid: {ti.task_id}, \
            privide_context: {ti.task.provide_context if hasattr(ti.task, "provide_context") else "False"} \
            callable: {ti.task.python_callable.__name__ if hasattr(ti.task, "python_callable") else "False"} \
            bash_command: {ti.task.bash_command if hasattr(ti.task, "bash_command") else "False"}'
        )
        print(f'task: {ti.task_id} ok')

