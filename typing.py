class Iterator:
    def __class_getitem__(cls, item):
        return cls

class Optional:
    def __class_getitem__(cls, item):
        return cls

class Callable:
    def __class_getitem__(cls, item):
        return cls

class Generic:
    def __class_getitem__(cls, item):
        return cls

class TypeVar:
    def __init__(self, *args):
        pass
    def __class_getitem__(cls, item):
        return cls