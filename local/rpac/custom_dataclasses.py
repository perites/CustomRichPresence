from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateInfo:
    details: str = None
    state: str = None

    start: int = None
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

    data: UpdateInfo = None
