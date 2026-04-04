import sys

from components.mm_component import MemoryMappedComponent

class SerialOutput(MemoryMappedComponent):
    def __init__(self, addr: int) -> None:
        self.addr = addr

        self.input = None
        self.output = None
        
    def contains(self, addr: int) -> bool:
        return addr == self.addr
    
    def fetch(self, addr: int) -> int:
        key = ord(self.input) if self.input is not None else 0
        self.input = None
        return key & 0xff
    
    def write(self, addr: int, val: int) -> None:
        self.output = chr(val)