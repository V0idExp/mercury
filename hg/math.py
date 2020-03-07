from gem.vector import Vector


class Vector2(Vector):

    def __init__(self, x: float = 0.0, y: float = 0.0):
        super().__init__(2)
        self.x = x
        self.y = y

    @property
    def x(self) -> float:
        return self.vector[0]

    @x.setter
    def x(self, value: float):
        self.vector[0] = value

    @property
    def y(self) -> float:
        return self.vector[1]

    @y.setter
    def y(self, value: float):
        self.vector[1] = value
