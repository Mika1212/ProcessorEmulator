from __future__ import annotations

from threading import Event, Thread

from loguru import logger

from src.processor import Processor
from src.scheduler import Scheduler
from src.task_generator import TaskGenerator

THREAD_LOGGER_FORMAT = '{time: HH:mm:ss} | {message}'


class Program:
    def __init__(self):
        self.processor = Processor()
        self.taskGeneratorEvent = Event()
        self.eventHappenEvent = Event()
        self.scheduler = Scheduler(self.processor, self.taskGeneratorEvent, self.eventHappenEvent)
        self.taskNum = 10

        t = Thread(target=self.scheduler.waitForEvents)
        t.daemon = True
        t.start()

        self.taskGenerator = TaskGenerator(self.scheduler, self.taskNum)
        t2 = Thread(target=self.taskGenerator.startGenerate)
        t2.daemon = True
        t2.start()

        self.counter = 0
        self.pidCounter = 1

    def start(self):
        while True:
            self.counter = self.counter + 1
            if self.counter == 30000000:
                self.counter = 0
                self.eventHappenEvent.set()
                logger.debug("Произошло событие")


if __name__ == '__main__':
    import sys

    logger.remove()
    logger.add(sys.stdout, format=THREAD_LOGGER_FORMAT)
    logger.debug("Получено фото, ID = 10002")
    logger.debug("Фото ID = 10002 обработано, C = 4.56")
    logger.debug("Результат доставлен клиенту, 1_Pixel_8_pro")

    logger.debug("Отправлено фото на сервер, ID = 10002, клиент = Pixel_8_pro")
    logger.debug("Получен ответ, ID = 10002, C = 4.56")


    program = Program()
    program.taskNum = 0
    program.start()
