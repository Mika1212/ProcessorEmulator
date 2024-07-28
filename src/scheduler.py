from __future__ import annotations

from threading import Thread, Event

from loguru import logger

from src.task import Task, TaskState, ExtendedTask


class Scheduler:
    QUEUE_LIMIT = 10

    def __init__(self, processor, taskGeneratorEvent: Event, eventHappenEvent: Event):
        self.event = ''
        self.generatedTask = None
        self.processor = processor
        self.processorEvent = Event()
        self.taskGeneratorEvent = taskGeneratorEvent
        self.eventHappenEvent = eventHappenEvent
        self.currentTask: Task | ExtendedTask | None = None
        self.queues: list = [[], [], [], []]
        self.tasksWaitingForEvent: list[ExtendedTask] = []

    def addTask(self, task: Task):
        logger.debug(f'Поступило задание | {task}')
        task.activate()
        if self.currentTask is None:
            self.startTask(task)
            self.printTasks()
        elif task.priority.value > self.currentTask.priority.value:
            logger.debug('Поступило задание с приоритетом выше: preemt |')
            self.processor.stop()
            self.processorEvent.wait()
            self.currentTask.preempt()
            if len(self.queues[self.currentTask.priority.value]) < self.QUEUE_LIMIT:
                logger.debug(f'Добавление прерванного задания в очередь | {self.currentTask}')
                self.queues[self.currentTask.priority.value].append(self.currentTask)
            self.startTask(task)
            self.printTasks()
        else:
            if len(self.queues[task.priority.value]) < self.QUEUE_LIMIT:
                logger.debug(f'Добавление задания в очередь | {task}')
                self.queues[task.priority.value].append(task)
                self.printTasks()

    def taskDone(self):
        logger.debug(f'Задание выполнено | {self.currentTask}')
        t = self.currentTask
        self.currentTask = None
        t.leftTimeToRun -= 1

        newTask = self.chooseNewTaskFromQueue()
        logger.debug(f'Следующее задание | {newTask}')
        if newTask is not None:
            self.startTask(newTask)
        self.printTasks()

    def chooseNewTaskFromQueue(self):
        for i in range(3, -1, -1):
            if len(self.queues[i]) != 0:
                newTask = self.queues[i].pop(0)
                return newTask
        return None

    def startTask(self, task: Task):
        logger.debug(f'Передача задания процессору | {task}')
        self.currentTask = task
        processorThread = Thread(target=self.processor.executeTask, args=[task, self.processorEvent])
        processorThread.daemon = True
        processorThread.start()

    def waitForEvents(self):
        # logger.debug(f'Начало работы планировщика')
        while not (self.taskGeneratorEvent.is_set() or self.processorEvent.is_set() or self.eventHappenEvent.is_set()):
            pass
        if self.taskGeneratorEvent.is_set():
            self.addTask(self.generatedTask)
            self.taskGeneratorEvent.clear()
            self.generatedTask = None
        elif self.processorEvent.is_set():
            if self.currentTask.state == TaskState.SUSPENDED:
                self.taskDone()
            elif self.currentTask.state == TaskState.WAITING:
                self.taskWaitingForEvent()

            self.processorEvent.clear()
        elif self.eventHappenEvent.is_set():
            self.eventHappen()
            self.eventHappenEvent.clear()
        self.waitForEvents()

    def taskWaitingForEvent(self):
        logger.debug(f'Задание ожидает события | {self.currentTask}')
        self.tasksWaitingForEvent.append(self.currentTask)
        self.currentTask = None
        newTask = self.chooseNewTaskFromQueue()
        if newTask is not None:
            self.startTask(newTask)
        self.printTasks()

    def eventHappen(self):
        if len(self.tasksWaitingForEvent) > 0:
            task = self.tasksWaitingForEvent[0]
            task.release()
            logger.debug(f'Задание дождалось события | {task}')
            self.tasksWaitingForEvent.remove(task)
            task.events = ''
            self.addTask(task)

    def printTasks(self):
        print("\n########################################################################################"
              "##########################################")
        print("\t\t\t\t\t\t\t\t\t\t\t\t\tТекущая задача")
        if self.currentTask is not None:
            print(self.currentTask)
        print("---------------------------------------------------------------------------------------"
              "-----------------------------------------")
        print("\t\t\t\t\t\t\t\t\t\t\t\t\tОчередь задач")

        for i in range(3, -1, -1):
            if len(self.queues[i]) > 0:
                print(F"\t\t\t\t\t\t\t\t\t\t\t\t\t Приоритет {i}")
                for task in self.queues[i]:
                    print(F"{task}")

        print("---------------------------------------------------------------------------------------"
              "-----------------------------------------")
        print(F"\t\t\t\t\t\t\t\t\t\t\t\t\tОчередь ожидания")
        for task in self.tasksWaitingForEvent:
            print(task)
        print("########################################################################################"
              "##########################################\n")
