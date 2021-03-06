from collections import defaultdict

from airflow.executors.base_executor import BaseExecutor
from airflow.utils.state import State
from airflow.utils.db import create_session


class MockExecutor(BaseExecutor):
    """
    MockExecutor is used for unit testing purposes.
    """

    def __init__(self, do_update=True, *args, **kwargs):
        self.do_update = do_update
        self._running = []

        # A list of "batches" of tasks
        self.history = []
        # All the tasks, in a stable sort order
        self.sorted_tasks = []

        # If multiprocessing runs in spawn mode,
        # arguments are to be pickled but lambda is not picclable.
        # So we should pass self.success instead of lambda.
        self.mock_task_results = defaultdict(self.success)

        super(MockExecutor, self).__init__(*args, **kwargs)

    def success(self):
        return State.SUCCESS

    def heartbeat(self):
        if not self.do_update:
            return

        with create_session() as session:
            self.history.append(list(self.queued_tasks.values()))

            # Create a stable/predictable sort order for events in self.history
            # for tests!
            def sort_by(item):
                key, val = item
                (dag_id, task_id, date, try_number) = key
                (cmd, prio, queue, sti) = val
                # Sort by priority (DESC), then date,task, try
                return -prio, date, dag_id, task_id, try_number

            open_slots = self.parallelism - len(self.running)
            sorted_queue = sorted(self.queued_tasks.items(), key=sort_by)
            for index in range(min((open_slots, len(sorted_queue)))):
                (key, (_, _, _, simple_ti)) = sorted_queue[index]
                self.queued_tasks.pop(key)
                state = self.mock_task_results[key]
                ti = simple_ti.construct_task_instance(session=session, lock_for_update=True)
                ti.set_state(state, session=session)
                self.change_state(key, state)

    def terminate(self):
        pass

    def end(self):
        self.sync()

    def change_state(self, key, state):
        super(MockExecutor, self).change_state(key, state)
        # The normal event buffer is cleared after reading, we want to keep
        # a list of all events for testing
        self.sorted_tasks.append((key, state))

    def mock_task_fail(self, dag_id, task_id, date, try_number=1):
        """
        Set the mock outcome of running this particular task instances to
        FAILED.
        If the task identified by the tuple ``(dag_id, task_id, date,
        try_number)`` is run by this executor it's state will be FAILED.
        """
        self.mock_task_results[(dag_id, task_id, date, try_number)] = State.FAILED
