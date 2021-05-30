from __future__ import print_function

import datetime

from airflow import models
from airflow.decorators.base import get_unique_task_id
from airflow.operators import bash_operator
from airflow.operators import python_operator
from airflow.contrib.operators.dataflow_operator import DataflowTemplateOperator

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
        'dag_sample',
        schedule_interval=datetime.timedelta(days=1),
        default_args=default_dag_args) as dag:
    def greeting():
        import logging
        logging.info('Hello World!')

    # An instance of an operator is called a task. In this case, the
    # hello_python task calls the "greeting" Python function.
    hello_python = python_operator.PythonOperator(
        task_id='hello',
        python_callable=greeting)

    yo_dagrun = bash_operator.BashOperator(
        task_id='yo',
        bash_command='echo dagrun: {{ dag_run.conf }}'
    )

    # Likewise, the goodbye_bash task calls a Bash script.
    goodbye_bash = bash_operator.BashOperator(
        task_id='bye',
        bash_command='echo Goodbye.')

    # Define the order in which the tasks complete by using the >> and <<
    # operators. In this example, hello_python executes before goodbye_bash.
    hello_python >> yo_dagrun >> goodbye_bash