from dataclasses import dataclass


@dataclass
class AccessCodeInfo:
    status: bool
    is_use: bool
    date_of_expiry: str = None
