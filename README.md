# Picopex

An Ozpex 64 emulator that runs on the Pi Pico. As with my other Pi Pico projects, a keypad and display should be connected as in [Picograph](https://github.com/BeauConstrictor/Picograph) to make a 'Picophone'.

Picopex can run any Ozpex 64 software, albeit quite slowly. The main limitation is the keypad, which only has 16 keys, despite the standard expecting a full ASCII keyboard.

## Ports

Because of the limited keypad and lack of ANSI support in the terminal, most programs will have to be patched to work properly. You can find some ready-made patches in the `./ports` directory. You can tell these ports apart because they include `(Portable)` in their title screens.

### ROM Monitor

When inputtng hex, the digits and `A-D` all work as expected. To type an `E` or `F`, first press `#` (shift) and then `A` or `D`, respectively.

To move to a new address, press `*` and enter the address.

To perform other functions, press `#` followed by another key:

- To read memory, press `#C` followed by a memory address, and the contents between your current address and the one you typed will be echoed to the screen.
- To execute a program, starting at the current address, hit `#D`
- To check your current address after entering some hex, hit `#*`.

### Calculator

Everything you need to know to use this port is displayed at runtime.

## Cartridges

There is no (officially supported) way to wire physical cartridge slots to the Pi Pico, but cartridges can be swapped when the Picopex is connected to a computer using `make cswap`, which will start a small GUI.

## Building

To build the ports, run `make`. To flash everything to a Picophone, run `make flash`

## Emergency Reset

To force reset Picopex, press `ABCD369*`.
