from src.task import Task, TaskState, ExtendedTask, Priority


class TestTask:
    task = Task(Priority.HIGH, 45, 16)

    def test_init(self):
        assert self.task.leftTimeToRun == 45, 'Wrong TTR of task'
        assert self.task.pid == 16, 'Wrong PID of task'
        assert self.task.priority == Priority.HIGH, 'Wrong priority of task'
        assert self.task.state == TaskState.SUSPENDED, 'Wrong state of task'

    def test_setter(self):
        self.task.state = TaskState.RUNNING
        assert self.task.state == TaskState.RUNNING, 'Wrong state of task'
        self.task.state = TaskState.READY
        assert self.task.state == TaskState.READY, 'Wrong state of task'
        self.task.state = TaskState.WAITING
        assert self.task.state == TaskState.WAITING, 'Wrong state of task'
        self.task.leftTimeToRun = 120
        assert self.task.leftTimeToRun == 120, 'Wrong TTR of task'
        self.task.leftTimeToRun = 0
        assert self.task.leftTimeToRun == 0, 'Wrong TTR of task'

    def test_activate(self):
        self.task.state = TaskState.SUSPENDED
        self.task.activate()
        assert self.task.state == TaskState.READY

    def test_start(self):
        self.task.state = TaskState.READY
        self.task.start()
        assert self.task.state == TaskState.RUNNING

    def test_preempt(self):
        self.task.state = TaskState.RUNNING
        self.task.preempt()
        assert self.task.state == TaskState.READY

    def test_terminate(self):
        self.task.state = TaskState.RUNNING
        self.task.terminate()
        assert self.task.state == TaskState.SUSPENDED


class TestExtendedTask:

    task = ExtendedTask(Priority.HIGH, 1, 1, 0)

    def test_wait(self):
        self.task.state = TaskState.RUNNING
        self.task.wait()
        assert self.task.state == TaskState.WAITING

    def test_release(self):
        self.task.state = TaskState.WAITING
        self.task.release()
        assert self.task.state == TaskState.READY
