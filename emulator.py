import pygame
import sys

from font import font

PAD_X = 2
PAD_Y = 2
CHR_WIDTH = 4
CHR_HEIGHT = 5

class SoftwareTerminal:
    def __init__(self, width: int, height: int, scale: int) -> None:
        self.width = width
        self.height = height
        self.scale = scale
        self.font = font

        pygame.init()
        self.screen = pygame.display.set_mode((width * scale, height * scale))
        self.surface = pygame.Surface((width, height))

        self.pixel_changes = []

        self.surface.fill((0, 0, 0))

        self.clear()

    def set_pixel(self, x: int, y: int, val: bool|str) -> None:
        self.pixel_changes.append((x, y, val))
    
    def scroll(self, x: int, y: int) -> None:
        self.surface.scroll(dx=x, dy=y)
        
        if x > 0:
            rect = pygame.Rect(0, 0, x, self.height)
            self.surface.fill((0, 0, 0), rect)
        elif x < 0:
            rect = pygame.Rect(self.width + x, 0, -x, self.height)
            self.surface.fill((0, 0, 0), rect)
        
        if y > 0:
            rect = pygame.Rect(0, 0, self.width, y)
            self.surface.fill((0, 0, 0), rect)
        elif y < 0:
            rect = pygame.Rect(0, self.height + y, self.width, -y)
            self.surface.fill((0, 0, 0), rect)

    def clear(self) -> None:
        self.cursor = [PAD_X, PAD_Y]

        # this way, changes after the clear are not lost
        # as they would be if a flag was used
        self.pixel_changes.clear()
        self.pixel_changes.append((-1, -1, -1))

    def write(self, text: str,
              char_spacing: int=1, line_height: int=7) -> None:

        for i, ch in enumerate(text):
            if ch == "\n":
                self.cursor[0] = PAD_X
                if self.cursor[1] > self.height-line_height*2:
                    self.scroll(0, -line_height)
                else:
                    self.cursor[1] += line_height
                continue
            elif self.cursor[0] > self.width-PAD_X-CHR_WIDTH:
                self.write("\n")

            pixels = self.font.get(ch, self.font["?"])
            for yo, row in enumerate(pixels):
                for xo, on in enumerate(row):
                    self.set_pixel(self.cursor[0]+xo, self.cursor[1]+yo, on)
            char_width = len(pixels[0])
            self.cursor[0] += char_width+char_spacing

    def refresh(self) -> None:
        for x, y, color in self.pixel_changes:

            if (x, y, color) == (-1, -1, -1):
                self.surface.fill((0, 0, 0))
                continue

            color = (255, 255, 255) if color else (0, 0, 0)
                
            if 0 <= x < self.width and 0 <= y < self.height:
                self.surface.set_at((x, y), color)

        self.pixel_changes.clear()

    def frame(self, output: str|None) -> None:
        key = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                key = event.unicode or chr(0)
                if key == "\n": key = "\n"

        if output == chr(0x11):
            self.clear()
        elif output == "\r":
            self.cursor[0] = PAD_X
        elif output == "\b":
            self.cursor[0] = max(0, self.cursor[0]-CHR_WIDTH)
        elif output:
            self.write(output)

        self.refresh()

        with_cursor = self.surface.copy()
        pygame.draw.rect(
            with_cursor,
            (255, 255, 255),
            (self.cursor[0], self.cursor[1]+CHR_HEIGHT-1, CHR_WIDTH-1, 1)
        )

        scaled = pygame.transform.scale(
            with_cursor,
            (self.width * self.scale, self.height * self.scale)
        )
        self.screen.blit(scaled, (0, 0))
        pygame.display.flip()

        return key