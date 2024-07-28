from src.scheduler import Scheduler
from src.task import ExtendedTask, Task, Priority
import random
from time import sleep


class TaskGenerator:
    def __init__(self, scheduler: Scheduler, tasksNum: int):
        self.scheduler = scheduler
        self.isStopped = False
        self.pid = 0
        self.averageTimeSleep = 2
        self.timeSleepRangeWidth = 0.5
        self.tasksNum = tasksNum

    def startGenerate(self):
        self.isStopped = False
        while self.tasksNum > 0:
            self.generate()
            self.tasksNum -= 1

    def stop(self):
        self.isStopped = True

    def generate(self):
        sleepTime = random.randint(int(self.averageTimeSleep * (1 - self.timeSleepRangeWidth)),
                                   int(self.averageTimeSleep * (1 + self.timeSleepRangeWidth)))
        sleep(sleepTime)
        self.pid += 1
        rand = random.randint(0, 100)
        priority = Priority[Priority(random.randint(0, 3)).name]
        timeToRun = random.randint(3, 5)
        if rand > 50:
            newTask = Task(priority, timeToRun, self.pid)
        else:
            event = 0
            newTask = ExtendedTask(priority, timeToRun, self.pid, event)
        self.scheduler.generatedTask = newTask
        self.scheduler.taskGeneratorEvent.set()
