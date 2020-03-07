from hg.physics.body import Body


class BodyComponent:

    def __init__(self):
        self.__body = Body()

    @property
    def mass(self) -> float:
        return self.__body.mass

    @mass.setter
    def mass(self, value: float):
        self.__body.mass = value

    def get_body(self) -> Body:
        return self.__body
