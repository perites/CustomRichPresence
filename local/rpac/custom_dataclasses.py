from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateInfo:
    details: str
    state: str

    start: int = None  # delete start
    party_size: list[int] = None
    large_image: str = None
    large_text: str = None
    buttons: list[dict[str, str]] = None


@dataclass(frozen=True)
class ActivityInfo:
    method: str

    name: str
    priority: int
    delay: int
    app_name: str

    # start_time
    data: UpdateInfo = None
