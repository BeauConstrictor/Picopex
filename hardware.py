from machine import Pin, SPI
import framebuf
import time

from font import font
from utils import *

BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9

PAD_X = 2
PAD_Y = 2
CHR_WIDTH = 4
CHR_HEIGHT = 5

class LCD_1inch8(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 160
        self.height = 128
        
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)
        
        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,10000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()
        
        self.WHITE = 0xFFFF
        self.BLACK = 0x0000
        self.GREEN = 0x001F
        self.BLUE  = 0xF800
        self.RED   = 0x07E0
        
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize display"""  
        self.rst(1)
        self.rst(0)
        self.rst(1)
        
        self.write_cmd(0x36);
        self.write_data(0x70);
        
        self.write_cmd(0x3A);
        self.write_data(0x05);

         #ST7735R Frame Rate
        self.write_cmd(0xB1);
        self.write_data(0x01);
        self.write_data(0x2C);
        self.write_data(0x2D);

        self.write_cmd(0xB2);
        self.write_data(0x01);
        self.write_data(0x2C);
        self.write_data(0x2D);

        self.write_cmd(0xB3);
        self.write_data(0x01);
        self.write_data(0x2C);
        self.write_data(0x2D);
        self.write_data(0x01);
        self.write_data(0x2C);
        self.write_data(0x2D);

        self.write_cmd(0xB4); # Column inversion
        self.write_data(0x07);

        # ST7735R Power Sequence
        self.write_cmd(0xC0);
        self.write_data(0xA2);
        self.write_data(0x02);
        self.write_data(0x84);
        self.write_cmd(0xC1);
        self.write_data(0xC5);

        self.write_cmd(0xC2);
        self.write_data(0x0A);
        self.write_data(0x00);

        self.write_cmd(0xC3);
        self.write_data(0x8A);
        self.write_data(0x2A);
        self.write_cmd(0xC4);
        self.write_data(0x8A);
        self.write_data(0xEE);

        self.write_cmd(0xC5); # vVCOM
        self.write_data(0x0E);

        # ST7735R Gamma Sequence
        self.write_cmd(0xe0);
        self.write_data(0x0f);
        self.write_data(0x1a);
        self.write_data(0x0f);
        self.write_data(0x18);
        self.write_data(0x2f);
        self.write_data(0x28);
        self.write_data(0x20);
        self.write_data(0x22);
        self.write_data(0x1f);
        self.write_data(0x1b);
        self.write_data(0x23);
        self.write_data(0x37);
        self.write_data(0x00);
        self.write_data(0x07);
        self.write_data(0x02);
        self.write_data(0x10);

        self.write_cmd(0xe1);
        self.write_data(0x0f);
        self.write_data(0x1b);
        self.write_data(0x0f);
        self.write_data(0x17);
        self.write_data(0x33);
        self.write_data(0x2c);
        self.write_data(0x29);
        self.write_data(0x2e);
        self.write_data(0x30);
        self.write_data(0x30);
        self.write_data(0x39);
        self.write_data(0x3f);
        self.write_data(0x00);
        self.write_data(0x07);
        self.write_data(0x03);
        self.write_data(0x10);

        self.write_cmd(0xF0); # Enable test command
        self.write_data(0x01);

        self.write_cmd(0xF6); # Disable ram power save mode
        self.write_data(0x00);

        # sleep out
        self.write_cmd(0x11);
        # DEV_Delay_ms(120);

        # Turn on the LCD display
        self.write_cmd(0x29);

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0x00)
        self.write_data(0xA0)
        
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x02)
        self.write_data(0x00)
        self.write_data(0x81)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)    

class HardwareTerminal:
    def __init__(self, keypad: "Keypad") -> None:
        self.font = font
        self.keypad = keypad
        self.oled = LCD_1inch8()
        self.oled.fill(0x0000)
        self.oled.show()

        self.cursor = [PAD_X, PAD_Y]
        self.pixel_changes = []

    def set_pixel(self, x: int, y: int, val: bool|str) -> None:
        col = 0xffff if val else 0x0000
        self.oled.pixel(x, y, col)

    def refresh(self) -> None:
        self.oled.show()

    def clear(self) -> None:
        self.cursor = [PAD_X, PAD_Y]
        self.pixel_changes.clear()
        self.oled.fill(0x0000)
        self.oled.show()

    def write(self, text: str, char_spacing: int=1, line_height: int=7) -> None:
        will_wrap = self.cursor[0] > self.oled.width - PAD_X - line_height
        for ch in text:
            if ch == "\n":
                if not will_wrap: self.write(" ")
                self.cursor[0] = PAD_X
                if self.cursor[1] + line_height > self.oled.height-PAD_Y:
                    self.clear()
                else:
                    self.cursor[1] += line_height
                continue
            elif will_wrap:
                self.write("\n")
            pixels = self.font.get(ch, self.font["?"])
            for yo, row in enumerate(pixels):
                for xo, on in enumerate(row):
                    self.set_pixel(self.cursor[0]+xo, self.cursor[1]+yo, on)
            self.cursor[0] += len(pixels[0]) + char_spacing

    def frame(self, output: str|None = None) -> str|None:
        if output == chr(0x11):
            self.clear()
        elif output == "\r":
            self.cursor[0] = PAD_X
        elif output == "\b":
            self.write(" ") # remove cursor
            self.cursor[0] = max(PAD_X, self.cursor[0]-CHR_WIDTH*2)
        elif output:
            self.write(output)
        if output:
            self.write("_")
            self.cursor[0] -= CHR_WIDTH
            self.oled.show()

        key = self.keypad.get_key()
        return key