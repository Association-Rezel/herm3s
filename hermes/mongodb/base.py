from datetime import datetime
from typing import Annotated, Any

import pytz
from netaddr import EUI, mac_unix_expanded
from pydantic import BaseModel, BeforeValidator


def parse_datetime(v: Any) -> datetime:
    """Parse datetime from iso string or datetime."""
    if isinstance(v, datetime):
        return v.astimezone(pytz.timezone("Europe/Paris"))
    if isinstance(v, float) or isinstance(v, int):
        # We use Europe/Paris timezone so that when it is formatted to string
        # (e.g. in emails or matrix messages) it is displayed in the correct timezone
        # It does NOT change the value of the datetime object, just the way it is displayed
        # when using python.
        # The front-end is being communicated the datetime as a timestamp, so it will
        # display it in the timezone of the browser.
        return datetime.fromtimestamp(v, tz=pytz.timezone("Europe/Paris"))

    if isinstance(v, str):
        # Also parse isoformat with Europe/Paris timezone
        return datetime.fromisoformat(v).astimezone(pytz.timezone("Europe/Paris"))

    raise ValueError("Invalid datetime format")


def parse_mac(v):
    if isinstance(v, EUI):
        return EUI(v, dialect=mac_unix_expanded)

    if isinstance(v, str):
        mac_obj = EUI(v, dialect=mac_unix_expanded)
        if mac_obj is None:
            raise ValueError("Invalid MAC address")
        return mac_obj

    else:
        raise ValueError("Invalid MAC address")


type PortableDatetime = Annotated[datetime, BeforeValidator(parse_datetime)]
type PortableMac = Annotated[EUI, BeforeValidator(parse_mac)]


class RezelBaseModel(BaseModel):
    class Config:
        json_encoders = {
            datetime: lambda d: d.timestamp(),
            EUI: lambda mac: str(EUI(mac, dialect=mac_unix_expanded)),
        }
        arbitrary_types_allowed = True
        validate_assignment = True
