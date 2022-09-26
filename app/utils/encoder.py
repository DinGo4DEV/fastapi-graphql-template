
# Return a dict for jsonable_encoder custom_encoder
from datetime import datetime

import pytz

tz = pytz.timezone("Asia/Hong_Kong")


def custom_encoder():
    encoder = {
        datetime:  lambda dt: dt.isoformat(timespec="milliseconds").replace("+00:00","").__add__("Z")
    }
    return encoder

