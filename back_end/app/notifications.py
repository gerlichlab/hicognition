"""Handling of notifications"""
from datetime import datetime
from pydantic import BaseModel, validate_arguments
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


class NotificationHandler:
    """Class that manages sending notifications
    through pydantic guarded notification data model"""

    @validate_arguments
    def signal_processing_update(self, data: ProcessingFinishedNotification):
        """Sends the update for the preprocessing status."""
        sse.publish(data.dict(), type="notification")

    def send_notification_general(self, data: dict):
        """Sends the update for status of ."""
        sse.publish(data, type="notification")

    def send_keep_alive(self):
        """Stops Chrome from terminating the NotificationHandler"""
        sse.publish({"data": 42}, type="keepalive")
