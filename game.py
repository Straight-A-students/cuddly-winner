import random
import time
import pygame
from db import DB


database = DB()


class Game:
    SCREEN_WIDTH = 700
    SCREEN_HEIGHT = 500
    STATUS_WAIT = 0
    STATUS_QUIT = 1

    def __init__(self, userinfo):
        self.userinfo = userinfo
        self.status = self.STATUS_WAIT

        pygame.init()

        size = [self.SCREEN_WIDTH, self.SCREEN_HEIGHT]
        self.screen = pygame.display.set_mode(size)

        pygame.display.set_caption("cuddly-winner - User: {} Name: {}".format(self.userinfo[0], self.userinfo[1]))
        pygame.mouse.set_visible(False)

        self.clock = pygame.time.Clock()

    def run(self):
        while self.status != self.STATUS_QUIT:
            self.display_frame(self.screen)
            self.clock.tick(60)
            self.process_events()

    def process_events(self):
        """ Process all of the events. Return a "True" if we need
            to close the window. """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.status = self.STATUS_QUIT

    def show_text(self, text, font, size, color, posX, posY, center=False):
        myfont = pygame.font.Font(None if font is None else 'fonts/{}'.format(font), size)
        TextSurf = myfont.render(text, True, color)
        if center:
            TextRect = TextSurf.get_rect()
            TextRect.center = (posX, posY)
            self.screen.blit(TextSurf, TextRect)
        else:
            self.screen.blit(TextSurf, (posX, posY))

    def display_frame(self, screen):
        screen.fill((255, 255, 255))

        if self.status == self.STATUS_WAIT:
            self.show_text(
                '等待另一位玩家',
                'NotoSansTC-Regular.otf',
                25,
                (255, 0, 0),
                self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2
            )

        pygame.display.flip()
