from threading import Event, Thread
from src.processor import Processor
from src.scheduler import Scheduler
from src.task import Task, TaskState, ExtendedTask, Priority


def patch():
    pass


class TestScheduler:

    def setup_method(self):
        self.processor = Processor()
        self.taskGeneratorEvent = Event()
        self.eventHappenEvent = Event()
        self.scheduler = Scheduler(self.processor, self.taskGeneratorEvent, self.eventHappenEvent)
        Thread(target=self.scheduler.waitForEvents).start()

    def teardown_method(self):
        self.scheduler.waitForEvents = patch
        self.eventHappenEvent.set()
        self.processor.stop()

    def test_addTask(self):

        task = Task(Priority.HIGHEST, 1, 1)
        self.scheduler.generatedTask = task

        self.taskGeneratorEvent.set()

        self.scheduler.processorEvent.wait()  # wait when task will be done
        while self.scheduler.processorEvent.is_set():  # wait when scheduler will process event and clear it
            pass

        assert task.state == TaskState.SUSPENDED
        assert task.leftTimeToRun <= 0
        assert self.scheduler.currentTask is None

    def test_addMorePriorTask(self):
        task = Task(Priority.LOWEST, 100, 1)
        self.scheduler.generatedTask = task

        self.taskGeneratorEvent.set()  # notify about new task
        while self.taskGeneratorEvent.is_set():  # wait when scheduler will process event and clear it
            pass

        morePriorTask = Task(Priority.HIGHEST, 100, 2)

        self.scheduler.generatedTask = morePriorTask

        self.taskGeneratorEvent.set()  # notify about new task
        while self.taskGeneratorEvent.is_set():  # wait until new task processed
            pass

        self.scheduler.waitForEvents = patch

        self.processor.stop()
        self.scheduler.processorEvent.wait()

        assert self.scheduler.currentTask == morePriorTask
        assert task.state == TaskState.READY

    def test_maxQueueLen(self):
        tasksPriority = Priority.LOWEST

        for i in range(0, 11):
            task = Task(tasksPriority, 100, i)
            self.scheduler.generatedTask = task
            self.taskGeneratorEvent.set()
            while self.taskGeneratorEvent.is_set():
                pass

        assert len(self.scheduler.queues[Priority.LOWEST.value]) == self.scheduler.QUEUE_LIMIT

        oneMoreTask = Task(tasksPriority, 100, 7)
        self.scheduler.generatedTask = oneMoreTask
        self.taskGeneratorEvent.set()
        while self.taskGeneratorEvent.is_set():
            pass

        assert len(self.scheduler.queues[Priority.LOWEST.value]) == self.scheduler.QUEUE_LIMIT

    def test_taskSwitchDueToExtendedTaskWait(self):

        extendedTask = ExtendedTask(Priority.LOWEST, 10, 1, 0)
        extendedTask.eventRequestTime = 5
        self.scheduler.generatedTask = extendedTask
        self.taskGeneratorEvent.set()
        while self.taskGeneratorEvent.is_set():  # wait when scheduler will process event and clear it
            pass

        otherTask = Task(Priority.LOWEST, 1, 2)
        self.scheduler.generatedTask = otherTask
        self.taskGeneratorEvent.set()
        while self.taskGeneratorEvent.is_set():  # wait when scheduler will process event and clear it
            pass

        self.scheduler.processorEvent.wait()
        while self.scheduler.processorEvent.is_set():  # wait when scheduler will process event and clear it
            pass
        assert len(self.scheduler.tasksWaitingForEvent) == 1

        self.scheduler.event = 0
        self.eventHappenEvent.set()
        while self.eventHappenEvent.is_set():  # wait when scheduler will process event and clear it
            pass

        self.scheduler.processorEvent.wait()
        while self.scheduler.processorEvent.is_set():  # wait when scheduler will process event and clear it
            pass
        assert otherTask.state == TaskState.SUSPENDED

        self.scheduler.processorEvent.wait()
        while self.scheduler.processorEvent.is_set():  # wait when scheduler will process event and clear it
            pass

        assert extendedTask.state == TaskState.SUSPENDED
        assert self.scheduler.currentTask is None
