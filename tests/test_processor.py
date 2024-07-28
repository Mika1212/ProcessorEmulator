import time
from threading import Event, Thread
from src.processor import Processor
from src.task import Task, TaskState, ExtendedTask, Priority


class TestProcessor:

    processor = Processor()

    def test_init(self):
        assert not self.processor.isStopped

    def test_executeTask(self):
        task = Task(Priority.HIGHEST, 1, 1)
        task.activate()
        event = Event()
        self.processor.executeTask(task, event)
        event.wait()
        assert task.state == TaskState.SUSPENDED
        assert task.leftTimeToRun == 0

    def test_executeExtendedTask(self):
        task = ExtendedTask(Priority.HIGHEST, 2, 2, 0)
        task.activate()
        event = Event()
        self.processor.executeTask(task, event)
        event.wait()
        assert task.state == TaskState.WAITING
        assert task.eventRequestTime == 1

    def test_interruptTaskExecution(self):
        initLeftTimeToRun = 10
        task = Task(Priority.HIGHEST, 3, initLeftTimeToRun)
        task.activate()
        event = Event()
        Thread(target=self.processor.executeTask, args=[task, event]).start()
        time.sleep(3)
        self.processor.stop()
        event.wait()
        assert task.state == TaskState.RUNNING  # since preempt is called by scheduler
        assert task.leftTimeToRun != initLeftTimeToRun

    def test_interruptExtendedTaskExecution(self):
        initEventRequestTime = 7
        initLeftTimeToRun = 10
        task = ExtendedTask(Priority.HIGHEST, 3, initLeftTimeToRun, 0)
        task.eventRequestTime = initEventRequestTime
        task.activate()
        event = Event()
        Thread(target=self.processor.executeTask, args=[task, event]).start()
        time.sleep(initLeftTimeToRun - initEventRequestTime)
        self.processor.stop()
        event.wait()
        assert task.state == TaskState.RUNNING  # since preempt is called by scheduler
        assert task.eventRequestTime < initEventRequestTime
        assert task.leftTimeToRun < initLeftTimeToRun

    def test_stop(self):
        self.processor.stop()
        assert self.processor.isStopped
