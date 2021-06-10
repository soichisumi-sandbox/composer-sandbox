from __future__ import print_function

import datetime

from airflow import models
from airflow.operators import bash_operator
from airflow.operators import python_operator
from airflow.contrib.operators.dataflow_operator import DataflowTemplateOperator

from airflow.models import Variable

default_dag_args = {
    # The start_date describes when a DAG is valid / can be run. Set this to a
    # fixed point in time rather than dynamically, since it is evaluated every
    # time a DAG is parsed. See:
    # https://airflow.apache.org/faq.html#what-s-the-deal-with-start-date
    'start_date': datetime.datetime(2018, 1, 1),
}

# Define a DAG (directed acyclic graph) of tasks.
# Any task you create within the context manager is automatically added to the
# DAG object.
with models.DAG(
        'dag_sample_w_template',
        schedule_interval=None,  # datetime.timedelta(days=1),
        default_args=default_dag_args,
        ) as dag:

    def set_xcom_fn(ds, **kwargs):
        ti = kwargs["ti"]
        ti.xcom_push(
            key="xcomkey",
            value="xcomvalue"
        )

    def greeting(ds, **kwargs):
        import logging
        conf, ti = kwargs["dag_run"].conf or {}, kwargs["ti"]
        logging.info(f'Hello! conf: {conf.get("key")}, xcom: {ti.xcom_pull(key="xcomkey")}')

    set_xcoms = python_operator.PythonOperator(
        task_id="set_xcoms",
        provide_context=True,
        python_callable=set_xcom_fn
    )

    greet_python = python_operator.PythonOperator(
        task_id='greeting',
        provide_context=True,
        python_callable=greeting)

    # bash_command='echo dagrun: {{ dag_run.conf }} / airflow_val: {{ var.value.project_id }}'
    yo_dagrun = bash_operator.BashOperator(
        task_id='yo',
        bash_command='echo dagrun: {{ dag_run.conf["key"] }} / airflow_val: {{ var.value.project_id }}'
    )

    # Likewise, the goodbye_bash task calls a Bash script.
    goodbye_bash = bash_operator.BashOperator(
        task_id='bye',
        bash_command='echo {{ ti.xcom_pull(key="xcomkey") }}')

    # Define the order in which the tasks complete by using the >> and <<
    # operators. In this example, hello_python executes before goodbye_bash.
    set_xcoms >> greet_python >> yo_dagrun >> goodbye_bash
