class Event:

    def __init__(self, name):
        self.name = name
        self.__listeners = []

    def __iadd__(self, listener):
        if listener not in self.__listeners:
            self.__listeners.append(listener)
        return self

    def __isub__(self, listener):
        if listener in self.__listeners:
            self.__listeners.remove(listener)
        return self

    def __call__(self, *args, **kwargs):
        for listener in self.__listeners:
            listener(*args, **kwargs)
