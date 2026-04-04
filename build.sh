#!/bin/bash

set -e

vasm -Fbin -dotdir -o rom.bin monitor.asm -esc

