from database import Error
from datetime import datetime


def error_log(error, description, source):
    Error.create(
        error=str(error),
        description=str(description),
        source=str(source),
        date=datetime.now()
    )
