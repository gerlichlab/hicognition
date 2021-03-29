"""Start hicognition server."""
import os
from app import create_app, db
from app.models import User, Dataset, Intervals, Task, AverageIntervalData, BedFileMetadata
from flask_migrate import Migrate

app = create_app(os.getenv("FLASK_CONFIG") or "default")
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    """Make shell context for app."""
    return {
        "db": db,
        "User": User,
        "Dataset": Dataset,
        "Intervals": Intervals,
        "Task": Task,
        "AverageIntervalData": AverageIntervalData,
        "BedFileMetadata": BedFileMetadata
    }
