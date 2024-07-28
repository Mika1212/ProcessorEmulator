from threading import Event, Thread
from src.processor import Processor
from src.scheduler import Scheduler
from src.task import ExtendedTask, Task
from src.task_generator import TaskGenerator


class TestGenerator:

    def setup_method(self):
        p = Processor()
        e1 = Event()
        e2 = Event()
        self.scheduler = Scheduler(p, e1, e2)
        self.taskGenerator = TaskGenerator(self.scheduler, 15)

    def test_generate(self):
        self.taskGenerator.generate()
        assert self.scheduler.taskGeneratorEvent.is_set()

    def test_generateTask(self):
        while 1:  # generation of ExtendedTask is random event, but we need to check if it really will happen
            self.taskGenerator.generate()
            generatedTask = self.scheduler.generatedTask
            if isinstance(generatedTask, Task):
                break

    def test_generateExtendedTask(self):
        while 1:  # generation of ExtendedTask is random event, but we need to check if it really will happen
            self.taskGenerator.generate()
            generatedTask = self.scheduler.generatedTask
            if isinstance(generatedTask, ExtendedTask):
                break

    def test_stop(self):
        self.taskGenerator.stop()
        assert self.taskGenerator.isStopped

    def test_startGeneration(self):
        assert self.scheduler.currentTask is None
        assert not self.scheduler.taskGeneratorEvent.is_set()
        t = Thread(target=self.taskGenerator.startGenerate)
        t.start()
        self.scheduler.taskGeneratorEvent.wait()

        assert self.scheduler.taskGeneratorEvent.is_set()
        assert self.scheduler.generatedTask is not None

        self.taskGenerator.stop()
        t.join()

