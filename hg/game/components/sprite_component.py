from dataclasses import dataclass


@dataclass
class SpriteComponent:

    x: int = 0
    y: int = 0
    resource: str = ''
