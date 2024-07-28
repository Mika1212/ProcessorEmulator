from __future__ import annotations

from datetime import datetime
from threading import Event
from loguru import logger
from src.task import Task, ExtendedTask


class Processor:

    def __init__(self):
        self.isStopped: bool = False
        self.runningTask: Task | None = None

    def executeTask(self, task: Task, eventToNotify: Event):
        logger.debug(f'Начало работы процессора над заданием | {task}')
        self.isStopped = False
        if isinstance(task, ExtendedTask) and task.eventRequestTime > 0 and task.events != '':
            executionDuration = task.eventRequestTime
        else:
            executionDuration = task.leftTimeToRun

        task.start()
        logger.debug(f'Процессор работает над заданием | {task}')
        taskStartTime = datetime.now()
        self.runningTask = task

        elapsedTime = (datetime.now() - taskStartTime).seconds
        lastElapsedTime = elapsedTime
        while elapsedTime <= executionDuration and not self.isStopped:
            if elapsedTime > lastElapsedTime:
                task.leftTimeToRun -= elapsedTime - lastElapsedTime
                lastElapsedTime = elapsedTime
            elapsedTime = (datetime.now() - taskStartTime).seconds

        if not self.isStopped:
            if isinstance(task, ExtendedTask) and task.events != '':
                task.wait()
            else:
                task.terminate()
        else:
            if isinstance(task, ExtendedTask):
                task.eventRequestTime -= elapsedTime
        logger.debug(f'Конец работы процессора над заданием | {task}')
        eventToNotify.set()

    def stop(self):
        self.isStopped = True
