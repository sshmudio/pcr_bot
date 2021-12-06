from dataclasses import dataclass


@dataclass(frozen=True)
class Messages:
    hello_message: str = "Привет {name}, выбери действие"


msg = Messages()