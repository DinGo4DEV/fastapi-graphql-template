from datetime import datetime
import iso8601
from pydantic import ValidationError
import pytz
tz = pytz.timezone("Asia/Hong_Kong")

def validator_transform_zone_datetime(v)->datetime:
    if isinstance(v,str):
        parsed_date = iso8601.parse_date(v,None)
        if parsed_date.tzinfo is None:
            parsed_date = tz.localize(parsed_date)
        # print(f"origin date:{parsed_date} converted: {parsed_date.astimezone(pytz.utc)}")
        return parsed_date.astimezone(pytz.utc)
    elif isinstance(v,datetime):
        return v
    else: raise ValidationError(f"Can't parse {v} to datetime")