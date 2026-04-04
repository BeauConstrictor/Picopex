class Iterator:
    def __class_getitem__(cls, item):
        return cls

class Optional:
    def __class_getitem__(cls, item):
        return cls

class Callable:
    def __class_getitem__(cls, item):
        return cls