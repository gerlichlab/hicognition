"""Handling of notifications"""
from pydantic import BaseModel, validate_arguments
from datetime import datetime
from . import sse


class Notification(BaseModel):
    """Base model for notifications."""
    id: str
    owner: int
    time: datetime
    notification_type: str


class ProcessingFinishedNotification(Notification):
    """Notification that signals finished processing"""
    data_type: str
    name: str
    processing_type: str
    region_id: int
    region_name: str


class NotificationHandler():
    """Class that manages sending notifications
    throuth pydantic guarded notification data model"""

    @validate_arguments
    def signal_processing_completion(self, data: ProcessingFinishedNotification):
        sse.publish(data.dict(), type="notification")

    def send_keep_alive(self):
        sse.publish({"data": 42}, type="keepalive")