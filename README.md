# Picopex

An Ozpex 64 emulator that runs on the Pi Pico. As with my other Pi Pico projects, a keypad and display should be connected as in [Picograph](https://github.com/BeauConstrictor/Picograph).

Picopex can run any Ozpex 64 software, albeit quite slowly. The main limitation is the keypad, which only has 16 keys, despite the standard expecting a full ASCII keyboard.

## ROM Monitor

Because of the limited keypad, the standard ROM monitor had to be patched to use different keys. When inputtng hex, the digits and `A-D` all work as expected. To type an `E` or `F`, first press `#` (shift) and then `A` or `D`, respectively.

To move to a new address, press `*` and enter the address.

To perform other functions, press `#` followed by another key:

- To read memory, press `#C` followed by a memory address, and the contents between your current address and the one you typed will be echoed to the screen.
- To execute a program, starting at the current address, hit `#D`
- To check your current address after entering some hex, hit `#*`.

## Cartridges

There is no (officially supported) way to wire physical cartridge slots to the Pi Pico, but cartridges can be swapped when the Picopex is connected to a computer using `cswap.py`.