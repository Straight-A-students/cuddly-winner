import random
import time
import pygame
import os


def to_real_path(path):
    if not isinstance(path, list):
        path = [path]
    return os.path.realpath(os.path.join(*([os.path.dirname(__file__)] + path)))


class Person(pygame.sprite.Sprite):
    def __init__(self, pos, id):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load(to_real_path('images/player{}.png'.format(id))).convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 50))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]


class Box(pygame.sprite.Sprite):
    def __init__(self, pos):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([width, height])
        self.image.fill(color)

        self.rect = self.image.get_rect()


class Game:
    SCREEN_WIDTH = 700
    SCREEN_HEIGHT = 500
    STATUS_WAIT = 0
    STATUS_QUIT = 1
    STATUS_READY = 2
    STATUS_READY_WAIT = 3
    STATUS_INGAME = 4

    def __init__(self, userinfo, linker):
        self.userinfo = userinfo
        self.linker = linker
        self.status = self.STATUS_WAIT

        pygame.init()

        size = [self.SCREEN_WIDTH, self.SCREEN_HEIGHT]
        self.screen = pygame.display.set_mode(size)

        pygame.display.set_caption("cuddly-winner - User: {} Name: {}".format(self.userinfo[0], self.userinfo[1]))
        pygame.mouse.set_visible(False)

        self.clock = pygame.time.Clock()
        self.items = pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()

    def run(self):
        while self.status != self.STATUS_QUIT:
            self.display_frame(self.screen)
            self.clock.tick(60)
            self.process_events()

            #
            message = self.linker.wait_server_message()
            if message:
                if self.status == self.STATUS_WAIT:
                    if message['status'] == 'ready':
                        self.status = self.STATUS_READY
                elif self.status == self.STATUS_READY_WAIT:
                    if message['status'] == 'start':
                        self.status = self.STATUS_INGAME
                        self.initingame()

    def process_events(self):
        """ Process all of the events. Return a "True" if we need
            to close the window. """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.status = self.STATUS_QUIT
            if self.status == self.STATUS_READY:
                self.process_events_ready(event)

    def show_text(self, text, font, size, color, posX, posY, center=False):
        if font is not None:
            font = to_real_path(['fonts', font])
        myfont = pygame.font.Font(font, size)
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
                self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2,
                center=True
            )
        elif self.status in [self.STATUS_READY, self.STATUS_READY_WAIT]:
            self.display_frame_ready()
        elif self.status == self.STATUS_INGAME:
            self.display_frame_ingame()
        pygame.display.flip()

    def display_frame_ready(self):
        messages = [
            '準備開始',
            '每一回合雙方同時移動，並選擇攻擊',
            '移動時使用方向鍵移動，空白鍵跳躍',
            '攻擊時使用上下調整力道，左右調整角度',
        ]
        if self.status == self.STATUS_READY:
            messages.append('按下Enter後開始遊戲')
        elif self.status == self.STATUS_READY_WAIT:
            messages.append('你已準備開始遊戲，等待另一個玩家')
        for i, message in enumerate(messages):
            self.show_text(
                message,
                'NotoSansTC-Regular.otf',
                25,
                (255, 0, 0),
                self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2 + 50 * (i - 2),
                center=True
            )

    def process_events_ready(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.status = self.STATUS_READY_WAIT
                self.linker.ready_done()

    def initingame(self):
        person1 = Person((200, 200), 1)
        self.all_sprites_list.add(person1)
        person2 = Person((500, 200), 2)
        self.all_sprites_list.add(person2)

    def display_frame_ingame(self):
        background = pygame.image.load(to_real_path(['images', 'background.png'])).convert()
        self.screen.blit(background, (0, 0))
        self.all_sprites_list.draw(self.screen)

    def process_events_ingame(self):
        pass
