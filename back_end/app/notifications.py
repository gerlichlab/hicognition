"""Handling of notifications"""
from pydantic import BaseModel, validate_arguments
from datetime import datetime
from . import sse


class ProcessingFinishedNotification(BaseModel):
    """Notification that signals finished processing"""
    data_type: str
    id: int
    name: str
    processing_type: str
    submitted_by: int
    region_id: int
    region_name: str
    time: datetime
    id: str


class NotificationHandler():
    """Class that manages sending notifications
    throuth pydantic guarded notification data model"""

    @validate_arguments
    def signal_processing_completion(self, data: ProcessingFinishedNotification):
        sse.publish(data.dict(), type="processing_finished")