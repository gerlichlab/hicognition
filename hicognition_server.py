"""Start hicognition server."""
from app import app, db
from app.models import User, Dataset

@app.shell_context_processor
def make_shell_context():
    """Make shell context for app."""
    return {'db': db, 'User': User, "Dataset": Dataset}
