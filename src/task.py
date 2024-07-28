from enum import Enum


class TaskState(Enum):
    RUNNING = 1
    READY = 2
    SUSPENDED = 3
    WAITING = 4


class Priority(Enum):
    HIGHEST = 3
    HIGH = 2
    LOW = 1
    LOWEST = 0


class Task:

    def __init__(self, priority: Priority, leftTimeToRun: int, pid: int):
        self.pid: int = pid
        self._leftTimeToRun = leftTimeToRun
        self.priority: Priority = priority
        self._state: TaskState = TaskState.SUSPENDED

    @property
    def leftTimeToRun(self):
        return self._leftTimeToRun

    @leftTimeToRun.setter
    def leftTimeToRun(self, newValue):
        self._leftTimeToRun = newValue

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, newState: TaskState):
        self._state = newState

    def activate(self):
        if self._state == TaskState.SUSPENDED:
            self.state = TaskState.READY

    def start(self):
        if self._state == TaskState.READY:
            self.state = TaskState.RUNNING

    def preempt(self):
        if self._state == TaskState.RUNNING:
            self.state = TaskState.READY

    def terminate(self):
        if self._state == TaskState.RUNNING:
            self.state = TaskState.SUSPENDED

    def __hash__(self):
        return self.pid

    def __repr__(self):
        return f'Задание {self.pid}: приоритет={self.priority}, ' \
               f'состояние={self._state}, время выполнения={self._leftTimeToRun}'


class ExtendedTask(Task):

    def __init__(self, priority: Priority, leftTimeToRun: int, pid: int, events: int):
        super().__init__(priority, leftTimeToRun, pid)
        self.eventRequestTime = 1
        self.events = events

    def wait(self):
        if self._state == TaskState.RUNNING:
            self.state = TaskState.WAITING

    def release(self):
        if self._state == TaskState.WAITING:
            self.state = TaskState.READY

    def __repr__(self):
        return f'РЗ {self.pid}: приоритет={self.priority}, состояние={self._state}, ' \
               f'событие= {self.events}, время выполнения={self._leftTimeToRun}'
