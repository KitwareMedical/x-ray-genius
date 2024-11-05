from abc import ABC
from contextlib import contextmanager
import dataclasses
from enum import Enum
import time
from typing import Any

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from channels.layers import get_channel_layer


@dataclasses.dataclass
class ProgressMessage:
    description: str | None = None
    progress: float | None = None
    status: str | None = None
    custom: dict | None = None
    type: str = 'task_tracker_progress'


class TaskStatus(Enum):
    QUEUED = 'queued'
    RUNNING = 'running'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'


class TaskTracker:
    def __init__(self, state: Any, group_names: list[str], initial_description: str = ''):
        # 'state' is an opaque value used to identify what is being tracked
        self.state = state
        self.groups = group_names
        channel_layer = get_channel_layer()
        self._sync_group_send = async_to_sync(channel_layer.group_send)
        self._description = initial_description
        self._progress = -1.0
        self._status = TaskStatus.QUEUED
        self._dirty = True
        self._last_flush = 0

    def send_message(self, payload: ProgressMessage):
        for group in self.groups:
            self._sync_group_send(
                group,
                {
                    'type': 'send_notification',
                    'message': {
                        **dataclasses.asdict(payload),
                        'state': self.state,
                    },
                },
            )

    def flush(self, max_rate_seconds: float | None = None):
        if self._dirty and (
            not max_rate_seconds or time.time() - self._last_flush > max_rate_seconds
        ):
            self._last_flush = time.time()
            self.send_message(
                ProgressMessage(
                    status=self._status.value,
                    progress=self._progress,
                    description=self._description,
                )
            )
            self._dirty = False

    @contextmanager
    def running(self):
        self.status = TaskStatus.RUNNING
        self.flush()

        try:
            yield self
            self.status = TaskStatus.SUCCEEDED
        except Exception:
            self.status = TaskStatus.FAILED
            self.description = 'An error occurred'
            raise
        finally:
            self.flush()
            for group in self.groups:
                self._sync_group_send(
                    group,
                    {
                        'type': 'close_connection',
                        'message': {},
                    },
                )

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value: str):
        self._dirty = True
        self._description = value

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value: float):
        self._dirty = True
        self._progress = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value: TaskStatus):
        self._dirty = True
        self._status = value


class TaskTrackerConsumer(JsonWebsocketConsumer, ABC):
    # This must be set by subclasses during connect()
    group_name = None

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def send_notification(self, event):
        self.send_json(content=event['message'])

    def close_connection(self, event):
        self.close(reason='task complete')


class DashboardConsumer(TaskTrackerConsumer):
    def connect(self):
        self.user = self.scope['user']
        self.group_name = f'dashboard_{self.user.pk}'
        super().connect()
