from random import randint
from components.mm_component import MemoryMappedComponent

class Ram(MemoryMappedComponent):
    CHUNK_SIZE = 4 * 1024 # 4k per chunk

    def __init__(self, min_addr: int, max_addr: int) -> None:
        self.start = min_addr
        self.end = max_addr
        
        self.num_chunks = ((self.end - self.start + 1) + self.CHUNK_SIZE - 1) // self.CHUNK_SIZE
        self.chunks = []
        
        for i in range(self.num_chunks):
            chunk_len = min(self.CHUNK_SIZE, (self.end - self.start + 1) - i * self.CHUNK_SIZE)
            chunk = bytearray(randint(0, 0xff) for _ in range(chunk_len))
            self.chunks.append(chunk)
    
    def _get_chunk_index_offset(self, addr: int):
        idx = (addr - self.start) // self.CHUNK_SIZE
        offset = (addr - self.start) % self.CHUNK_SIZE
        return idx, offset
    
    def load(self, data: list[int], start_addr: int) -> None:
        addr = start_addr
        for d in data:
            self.write(addr, d)
            addr += 1
    
    def contains(self, addr: int) -> bool:
        return self.start <= addr <= self.end
    
    def fetch(self, addr: int) -> int:
        idx, offset = self._get_chunk_index_offset(addr)
        return self.chunks[idx][offset] & 0xff
    
    def write(self, addr: int, val: int) -> None:
        idx, offset = self._get_chunk_index_offset(addr)
        self.chunks[idx][offset] = val & 0xff