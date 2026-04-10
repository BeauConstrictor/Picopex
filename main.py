import gc
import json
from utils import *
from time import sleep
from typing import Iterator
from sys import implementation

RESET_SEQ = "abcd369*"

emulated = implementation.name == "cpython"
if emulated:
    from emulator import SoftwareTerminal
    from components.software_timer import Timer
else:
    from components.hardware_timer import Timer
    from hardware import HardwareTerminal
    from keypad import Keypad
    import machine
    
from components.cpu import Cpu
from components.ram import Ram
from components.rom import Rom
from components.serial import SerialOutput
from components.expansion_slot import ExpansionSlot
from components.mm_component import MemoryMappedComponent
from components.expansion_slot import RomExpansion, BbRamExpansion

def load_slot(literal: str, slot: ExpansionSlot) -> None:
    parts = literal.split(":")
    expansion = parts[0]
    if len(parts) > 1: arg = ":".join(parts[1:])
    else: arg = None
    
    expansions = {
        "rom":   RomExpansion,
        "bbram": BbRamExpansion,
    }
    
    if expansions.get(expansion, None) is None:
        print("\n\n\033[31m", end="")
        print(f"6502: unknown expansion card: '{expansion}'.",
              "\033[0m", file=stderr)
        exit(1)
    
    e = expansions[expansion](arg)
    slot.mount(e.read, e.write)

def create_machine(rom: str, slot1: str|None, slot2: str|None,
                   serial: MemoryMappedComponent) -> Cpu:
    # MEMORY MAP:
    # ram:    $0000 -> $7fff  (32,768 B)
    # timer:  $8000 && $8001
    # serial: $8002
    # slot 1: $8003 -> $a002  ( 8,192 B)
    # slot 2: $a003 -> $c002  ( 8,192 B)
    # rom:    $c003 -> $ffff  (16,381 B) - an odd size, but it's just whatever
    #                                      fit in the remaining space
    
    gc.collect()
    cpu = Cpu({
        "ram": Ram(0x0000, 0x7fff),
        "timer": Timer(0x8000, 0x8001),
        "serial": serial(0x8002),
        "slot1": ExpansionSlot(0x8003, 0xa002),
        "slot2": ExpansionSlot(0xa003, 0xc002),
        "rom": Rom(0xc003, 0xffff),
    })

    gc.collect()
    with open(rom, "rb") as f:
        rom_data = bytearray(f.read())
    cpu.mm_components["rom"].load(rom_data, 0xc003)
        
    if slot1: load_slot(slot1, cpu.mm_components["slot1"])
    if slot2: load_slot(slot2, cpu.mm_components["slot2"])
    
    cpu.reset()
    
    return cpu

def simulate(cpu: Cpu) -> Iterator[None]:
    cycles_executed = 0
    
    while True:
        try:
            instr = cpu.execute()      
            yield
        except NotImplementedError as e: pass

def main() -> None:
    with open("cartridges.json", "r") as f:
        cartridge_types = json.load(f)
    carts = [f"{c}:cs{i+1}.bin" if exists(f"cs{i+1}.bin") and c is not None else None for i, c in enumerate(cartridge_types)]

    if emulated:
        terminal = SoftwareTerminal(160, 128, 10)
    else:
        keypad = Keypad(['1', '2', '3', 'a',
                    '4', '5', '6', 'b',
                    '7', '8', '9', 'c',
                    '*', '0', '#', 'd'],
                    [0, 1, 2, 3],
                    [4, 5, 6, 7],
                    4, 4)    
        keypad.set_debounce_time(400)
        terminal = HardwareTerminal(keypad)
        
    terminal.write("Booting...")
    terminal.refresh()

    print("using carts:", *carts)

    cpu = create_machine("bin/monitor", *carts, SerialOutput)
    serial = cpu.mm_components["serial"]
    terminal.clear()

    key_seq = ""

    for _ in simulate(cpu):
        key = terminal.frame(serial.output)
        if key:
            serial.input = key
            key_seq += key
            if len(key_seq) > len(RESET_SEQ):
                key_seq = key_seq[1:]
            if not emulated and key_seq == RESET_SEQ:
                terminal.clear()
                terminal.write("Reset.")
                terminal.refresh()
                machine.soft_reset()

        serial.output = None

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n\033[31m", end="")
        print(f"emu: ctrl+c exit.", end="")
        print("\033[0m")
        exit(0)
