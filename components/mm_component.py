class MemoryMappedComponent:
    def contains(self, addr: int) -> bool: return False
    def fetch(self, addr: int) -> int: return 0
    def write(self, addr: int, val: int) -> None: pass