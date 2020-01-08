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

        self.id = id

        self.image = pygame.image.load(to_real_path('images/player{}.png'.format(id))).convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 50))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.speed = [0, 0]

    def update(self):
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]

        self.rect.x = max(self.rect.x, 15)
        self.rect.x = min(self.rect.x, 1245)  # 1280-15-20
        # self.rect.y = max(self.rect.y, 10)
        # self.rect.y = min(self.rect.y, 1280)

    def drop(self):
        self.speed[1] += 0.7

    def stopdrop(self):
        self.speed[1] = 0

    def jump(self):
        self.speed[1] = -10


class Box(pygame.sprite.Sprite):
    def __init__(self, pos, size, color):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([size[0], size[1]])
        self.image.fill(color)
        self.rect = self.image.get_rect()


class Floor(pygame.sprite.Sprite):
    def __init__(self, pos, size, color):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([size[0], size[1]])
        self.image.fill(color)

        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]


class Game:
    FPS = 30
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 700
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
        self.floor_list = pygame.sprite.Group()

    def create_peron(self, pos, id):
        person = Person(pos, id)
        self.all_sprites_list.add(person)
        return person

    def create_floor(self, pos, size, color):
        floor = Floor(pos, size, color)
        self.floor_list.add(floor)
        return floor

    def get_collide_side(self, main, other):
        '''回傳 main 的碰撞位置，上下左右'''
        bias = 3
        answer = [False, False, False, False]  # 上下左右

        # 上
        if (
            main.rect.top < other.rect.bottom  # 角色上端在物件下端之上
            and main.rect.bottom > other.rect.bottom  # 角色下端在物件下端之下
            and not (
                main.rect.right < other.rect.left + bias
                or main.rect.left > other.rect.right - bias
            )
        ):
            answer[0] = True

        # 下
        if (
            main.rect.bottom > other.rect.top  # 角色下端在物件上端之下
            and main.rect.top < other.rect.top  # 角色上端在物件上端之上
            and not (
                main.rect.right < other.rect.left + bias
                or main.rect.left > other.rect.right - bias
            )
        ):
            answer[1] = True

        # 左
        if (
            main.rect.left < other.rect.right  # 角色左端在物件右端之左
            and main.rect.right > other.rect.right  # 角色右端在物件左端之右
            and not (
                main.rect.bottom < other.rect.top + bias
                or main.rect.top > other.rect.bottom - bias
            )
        ):
            answer[2] = True

        # 右
        if (
            main.rect.right > other.rect.left  # 角色右端在物件左端之右
            and main.rect.left < other.rect.left  # 角色左端在物件左端之左
            and not (
                main.rect.bottom < other.rect.top + bias
                or main.rect.top > other.rect.bottom - bias
            )
        ):
            answer[3] = True
        return answer

    def run(self):
        while self.status != self.STATUS_QUIT:
            self.display_frame(self.screen)
            self.clock.tick(self.FPS)
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
                        self.initingame(me=message['me']['pos'], enemy=message['enemy']['pos'])
                elif self.status == self.STATUS_INGAME:
                    if message['status'] == 'update':
                        self.enemy.rect.x = message['enemy']['pos'][0]
                        self.enemy.rect.y = message['enemy']['pos'][1]

    def process_events(self):
        """ Process all of the events. Return a "True" if we need
            to close the window. """

        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT:
                self.status = self.STATUS_QUIT
            if self.status == self.STATUS_READY:
                self.process_events_ready(event)
            if self.status == self.STATUS_INGAME:
                self.process_events_ingame(event)

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

    def initingame(self, me, enemy):
        self.me = self.create_peron(me, 1)
        self.enemy = self.create_peron(enemy, 2)

        self.create_floor((600, 250), (300, 50), (144, 95, 0))
        self.create_floor((15, 400), (self.SCREEN_WIDTH - 30, 50), (144, 95, 0))

        self.background = pygame.image.load(to_real_path(['images', 'background.png'])).convert()
        self.background = pygame.transform.scale(self.background, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

    def display_frame_ingame(self):
        self.screen.blit(self.background, (0, 0))

        self.all_sprites_list.update()
        self.floor_list.update()

        collids = pygame.sprite.spritecollide(self.me, self.floor_list, False)
        if collids:
            for collid in collids:
                collid_side = self.get_collide_side(self.me, collid)

                if collid_side[0]:
                    print('{:.3f}'.format(time.time()), 'Top collide')
                    self.me.rect.y = collid.rect.y + self.me.rect.height + 1
                    self.me.speed[1] = 0
                    self.me.drop()
                if collid_side[1]:
                    print('{:.3f}'.format(time.time()), 'Down collide')
                    self.me.rect.y = collid.rect.y - self.me.rect.height + 1
                    self.me.stopdrop()
                if collid_side[2]:
                    print('{:.3f}'.format(time.time()), 'Left collide')
                    self.me.rect.x = collid.rect.x + collid.rect.width - 1
                    self.me.speed[0] = 0
                    self.me.drop()
                if collid_side[3]:
                    print('{:.3f}'.format(time.time()), 'Right collide')
                    self.me.rect.x = collid.rect.x - self.me.rect.width + 1
                    self.me.speed[0] = 0
                    self.me.drop()
        else:
            print('{:.3f}'.format(time.time()), 'Dropping')
            self.me.drop()

        self.me.update()
        self.linker.update_pos((self.me.rect.x, self.me.rect.y))

        self.all_sprites_list.draw(self.screen)
        self.floor_list.draw(self.screen)

    def process_events_ingame(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.me.speed[0] = -2
            elif event.key == pygame.K_RIGHT:
                self.me.speed[0] = 2
            elif event.key == pygame.K_SPACE:
                if self.me.speed[1] == 0:
                    self.me.jump()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.me.speed[0] = 0
            elif event.key == pygame.K_RIGHT:
                self.me.speed[0] = 0
