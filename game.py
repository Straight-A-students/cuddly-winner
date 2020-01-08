import random
import time
import pygame
import os
import math
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)


def to_real_path(path):
    if not isinstance(path, list):
        path = [path]
    return os.path.realpath(os.path.join(*([os.path.dirname(__file__)] + path)))


class Weapon(pygame.sprite.Sprite):
    def __init__(self, master, pos=(0, 0), name='grenade'):
        pygame.sprite.Sprite.__init__(self)

        self.master = master
        self.pos = pos
        self.name = name
        self.speed = [0, 0]
        self.is_explosion = False
        self.is_fire = False

    def set_pos(self, pos):
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def set_weapon(self, name):
        self.name = name
        self.image = pygame.image.load(to_real_path('images/{}.png'.format(self.name))).convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()

    def set_speed(self, angle, power):
        self.speed = [
            power * 35 * math.cos(angle / 180 * math.pi),
            -power * 35 * math.sin(angle / 180 * math.pi),
        ]

    def update(self):
        if self.is_fire and not self.is_explosion:
            self.speed[1] += 0.7
            logging.info('weapon speed %s', self.speed)
            self.rect.x += self.speed[0]
            self.rect.y += self.speed[1]

    def explosion(self):
        self.image = pygame.image.load(to_real_path('images/{}_explosion.png'.format(self.name))).convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.is_explosion = True


class Person(pygame.sprite.Sprite):
    def __init__(self, pos, id):
        pygame.sprite.Sprite.__init__(self)

        self.id = id
        self.hp = 100
        self.weapon = Weapon(self.id)

        self.image = pygame.image.load(to_real_path('images/player{}.png'.format(id))).convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 50))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.speed = [0, 0]

        self.angle = 0
        self.power = 0.5
        self.angle_d = 0
        self.power_d = 0

    def update(self):
        self.rect.x += self.speed[0]
        self.rect.y += self.speed[1]

        self.angle += self.angle_d
        self.power += self.power_d

        self.rect.x = max(self.rect.x, 15)
        self.rect.x = min(self.rect.x, 1245)  # 1280-15-20

        self.angle = (self.angle + 180) % 360 - 180
        self.power = max(self.power, 0)
        self.power = min(self.power, 1)

    def drop(self):
        self.speed[1] += 0.7

    def stopdrop(self):
        self.speed[1] = 0

    def jump(self):
        self.speed[1] = -10

    def fire(self, groups, name, speed):
        self.weapon.set_weapon(name)
        self.weapon.set_pos((self.rect.x, self.rect.y))
        self.weapon.speed[0] = speed[0]
        self.weapon.speed[1] = speed[1]
        self.weapon.is_fire = True
        groups.add(self.weapon)

    def aim(self, groups, weapon_name):
        self.weapon.is_fire = False
        self.weapon.set_weapon(weapon_name)
        self.weapon.set_pos((self.rect.center[0] - self.weapon.rect.width // 2, self.rect.center[1]))
        self.weapon.speed[0] = 0
        self.weapon.speed[1] = 0
        groups.add(self.weapon)


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
    STATUS_INGAME_WORKING = 5
    STATUS_INGAME_DONE = 6
    STATUS_INGAME_ACTION = 7

    TURN_TYPE_NONE = 0
    TURN_TYPE_MOVE = 1
    TURN_TYPE_ATTACK = 2

    def __init__(self, userinfo, linker):
        self.userinfo = userinfo
        self.linker = linker
        self.status = self.STATUS_WAIT
        self.turn_type = self.TURN_TYPE_NONE

        pygame.init()

        size = [self.SCREEN_WIDTH, self.SCREEN_HEIGHT]
        self.screen = pygame.display.set_mode(size)

        pygame.display.set_caption("cuddly-winner - User: {} Name: {}".format(self.userinfo[0], self.userinfo[1]))
        # pygame.mouse.set_visible(False)

        self.clock = pygame.time.Clock()
        self.items = pygame.sprite.Group()
        self.all_sprites_list = pygame.sprite.Group()
        self.floor_list = pygame.sprite.Group()
        self.weapon_list = pygame.sprite.Group()

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

    def scale_distance(self, pos1, pos2):
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

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
                elif self.status == self.STATUS_INGAME_DONE:
                    if message['status'] == 'action':
                        if message['type'] == self.TURN_TYPE_MOVE:
                            self.enemy.rect.x = message['context'][0]
                            self.enemy.rect.y = message['context'][1]
                        elif message['type'] == self.TURN_TYPE_ATTACK:
                            self.enemy.fire(self.weapon_list, message['context']['weapon_name'], message['context']['speed'])

                        if self.turn_type == self.TURN_TYPE_ATTACK:
                            self.me.fire(self.weapon_list, self.me.weapon.name, self.me.weapon.speed)
                        self.status = self.STATUS_INGAME_ACTION
                elif self.status == self.STATUS_INGAME_ACTION:
                    if message['status'] == 'action_done':
                        self.weapon_list.empty()
                        self.status = self.STATUS_INGAME

    def process_events(self):
        """ Process all of the events. Return a "True" if we need
            to close the window. """

        for event in pygame.event.get():
            # print(event)
            if event.type == pygame.QUIT:
                self.status = self.STATUS_QUIT
            if self.status == self.STATUS_READY:
                self.process_events_ready(event)
            elif self.status == self.STATUS_INGAME:
                self.process_events_ingame(event)
            elif self.status == self.STATUS_INGAME_WORKING:
                self.process_events_ingame_working(event)
            elif self.status == self.STATUS_INGAME_DONE:
                self.process_events_ingame_done(event)
            elif self.status == self.STATUS_INGAME_ACTION:
                self.process_events_ingame_action(event)

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
        elif self.status == self.STATUS_INGAME_WORKING:
            self.display_frame_ingame_working()
        elif self.status == self.STATUS_INGAME_DONE:
            self.display_frame_ingame_done()
        elif self.status == self.STATUS_INGAME_ACTION:
            self.display_frame_ingame_action()

        for i in range(100, self.SCREEN_HEIGHT, 100):
            pygame.draw.line(self.screen, (255, 0, 0), (0, i), (self.SCREEN_WIDTH, i))
        for i in range(100, self.SCREEN_WIDTH, 100):
            pygame.draw.line(self.screen, (255, 0, 0), (i, 0), (i, self.SCREEN_HEIGHT))

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

    def display_items(self):
        self.screen.blit(self.background, (0, 0))
        self.all_sprites_list.update()
        self.floor_list.update()
        self.weapon_list.update()

        collids = pygame.sprite.spritecollide(self.me, self.floor_list, False)
        if collids:
            for collid in collids:
                collid_side = self.get_collide_side(self.me, collid)

                if collid_side[0]:
                    logging.debug('Top collide')
                    self.me.rect.y = collid.rect.y + self.me.rect.height + 1
                    self.me.speed[1] = 0
                    self.me.drop()
                if collid_side[1]:
                    logging.debug('Down collide')
                    self.me.rect.y = collid.rect.y - self.me.rect.height + 1
                    self.me.stopdrop()
                if collid_side[2]:
                    logging.debug('Left collide')
                    self.me.rect.x = collid.rect.x + collid.rect.width - 1
                    self.me.speed[0] = 0
                    self.me.drop()
                if collid_side[3]:
                    logging.debug('Right collide')
                    self.me.rect.x = collid.rect.x - self.me.rect.width + 1
                    self.me.speed[0] = 0
                    self.me.drop()
        else:
            logging.debug('Dropping')
            self.me.drop()

        for wp in self.weapon_list:
            if not wp.is_explosion:
                weapon_collide_1 = pygame.sprite.spritecollide(wp, self.all_sprites_list, False)
                weapon_collide_2 = pygame.sprite.spritecollide(wp, self.items, False)
                weapon_collide_3 = pygame.sprite.spritecollide(wp, self.floor_list, False)
                if weapon_collide_2 or weapon_collide_3:
                    wp.explosion()

                for p in weapon_collide_1:
                    if p.id != wp.master:
                        wp.explosion()

                for p in self.all_sprites_list:
                    if p.id != wp.master:
                        if wp.is_explosion:
                            d = self.scale_distance((p.rect.x, p.rect.y), (wp.rect.x, wp.rect.y))
                            hp_d = int(-0.5 * d + 100)
                            if hp_d < 0:
                                hp_d = 0
                            p.hp -= hp_d
                            logging.info('user %s dis=%s hp -%s new_hp=%s', p.id, d, hp_d, p.hp)

        self.me.update()
        # self.linker.update_pos((self.me.rect.x, self.me.rect.y))

        self.all_sprites_list.draw(self.screen)
        self.floor_list.draw(self.screen)
        self.weapon_list.draw(self.screen)

        if self.status == self.STATUS_INGAME_WORKING:
            if self.turn_type == self.TURN_TYPE_ATTACK:
                # arrow
                pygame.draw.line(
                    self.screen,
                    (0, 0, 0),
                    self.me.rect.center,
                    (
                        self.me.rect.center[0] + self.me.power * 100 * math.cos(self.me.angle / 180 * math.pi),
                        self.me.rect.center[1] - self.me.power * 100 * math.sin(self.me.angle / 180 * math.pi),
                    ),
                    5
                )

    def display_frame_ingame(self):
        self.display_items()
        if self.status == self.STATUS_INGAME:
            self.show_text(
                '回合開始。按1選擇角色移動，按2選擇武器攻擊',
                'NotoSansTC-Regular.otf',
                25,
                (255, 0, 0),
                200, 600,
                center=False
            )

    def process_events_ingame(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                self.turn_type = self.TURN_TYPE_MOVE
                self.status = self.STATUS_INGAME_WORKING
            elif event.key == pygame.K_2:
                self.turn_type = self.TURN_TYPE_ATTACK
                self.status = self.STATUS_INGAME_WORKING
                self.me.aim(self.weapon_list, 'grenade')

    def display_frame_ingame_working(self):
        self.display_items()
        if self.status == self.STATUS_INGAME_WORKING:
            if self.turn_type == self.TURN_TYPE_MOVE:
                self.show_text(
                    '請使用左右控制角色位置、空白鍵跳躍，Enter鍵鎖定動作',
                    'NotoSansTC-Regular.otf',
                    25,
                    (255, 0, 0),
                    200, 600,
                    center=False
                )
            elif self.turn_type == self.TURN_TYPE_ATTACK:
                self.show_text(
                    '請使用左右控制攻擊角度、上下控制攻擊力道，Enter鍵鎖定動作',
                    'NotoSansTC-Regular.otf',
                    25,
                    (255, 0, 0),
                    200, 600,
                    center=False
                )

    def process_events_ingame_working(self, event):
        if self.turn_type == self.TURN_TYPE_MOVE:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.me.speed[0] = -2
                elif event.key == pygame.K_RIGHT:
                    self.me.speed[0] = 2
                elif event.key == pygame.K_SPACE:
                    if self.me.speed[1] == 0:
                        self.me.jump()
                elif event.key == pygame.K_RETURN:
                    self.linker.turn_done(self.turn_type, (self.me.rect.x, self.me.rect.y))
                    self.status = self.STATUS_INGAME_DONE

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.me.speed[0] = 0
                elif event.key == pygame.K_RIGHT:
                    self.me.speed[0] = 0

        elif self.turn_type == self.TURN_TYPE_ATTACK:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.me.angle_d = 1
                elif event.key == pygame.K_RIGHT:
                    self.me.angle_d = -1
                elif event.key == pygame.K_UP:
                    self.me.power_d = 0.005
                elif event.key == pygame.K_DOWN:
                    self.me.power_d = -0.005
                elif event.key == pygame.K_RETURN:
                    self.me.weapon.set_speed(self.me.angle, self.me.power)
                    self.me.angle_d = 0
                    self.me.power_d = 0
                    self.linker.turn_done(self.turn_type, {'weapon_name': self.me.weapon.name, 'speed': self.me.weapon.speed})
                    self.status = self.STATUS_INGAME_DONE
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.me.angle_d = 0
                elif event.key == pygame.K_RIGHT:
                    self.me.angle_d = 0
                elif event.key == pygame.K_UP:
                    self.me.power_d = 0
                elif event.key == pygame.K_DOWN:
                    self.me.power_d = 0

    def display_frame_ingame_done(self):
        self.me.speed[0] = 0
        self.display_items()
        self.show_text(
            '等待另一位玩家的動作',
            'NotoSansTC-Regular.otf',
            25,
            (255, 0, 0),
            200, 600,
            center=False
        )

    def process_events_ingame_done(self, event):
        pass

    def display_frame_ingame_action(self):
        self.show_text(
            '等待另一位玩家的動作',
            'NotoSansTC-Regular.otf',
            25,
            (255, 0, 0),
            200, 600,
            center=False
        )
        self.display_items()

        action_done = True
        if len(self.weapon_list) > 0:
            for wp in self.weapon_list:
                if not wp.is_explosion:
                    action_done = False

        if action_done:
            self.linker.action_done()

    def process_events_ingame_action(self, event):
        pass
