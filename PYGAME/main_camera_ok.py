# Imports
import pygame
import cv2
import numpy
import imutils
from datetime import timedelta, datetime as dt
from utilities import *


class Init:
    def __init__(self):
        self.utility = Services()
        pygame.init()
        myDisplayInfo = pygame.display.Info()
        print("Current Resolution: %s x %s\n" %
              (myDisplayInfo.current_w, myDisplayInfo.current_h))
        self.minX = 0
        # self.maxX = myDisplayInfo.current_w
        self.maxX = 640
        self.minY = 0
        # self.maxY = myDisplayInfo.current_h
        self.maxY = 480
        self.FPS = 60
        self.GS = pygame.display.set_mode((self.maxX, self.maxY))
        pygame.display.set_caption("FACE")
        self.clock = pygame.time.Clock()

        self.IP = ""
        self.PORT = "5005"
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255,   0,   0)
        self.GREEN = (0, 255,   0)
        self.BLUE = (0,   0, 255)
        self.CYAN = (0, 255, 255)
        self.SceneHome = self.HomeScene(self)
        self.SceneCamera = self.CameraScene(self)
        self.SceneClock = self.ClockScene(self)
        self.SceneWeather = self.WeatherScene(self)
        self.SceneLoading = self.LoadingScene(self)
        self.active_scene = self.SceneCamera

    def start(self):
        self.timer = dt.now()
        self.old_scene = None
        self.run()

    def is_quit_event(self, event, pressed_keys):
        x_out = event.type == pygame.QUIT
        ctrl = pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL]
        q = pressed_keys[pygame.K_q]

        return x_out or (ctrl and q)

    def run(self):
        while self.active_scene is not None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()

            # render current page
            if self.active_scene:
                self.active_scene.update()
                self.active_scene.render()

            # şu anki sahne ile bir önceki farklı ise
            delay = timedelta(seconds=100)
            if self.active_scene != self.old_scene:
                print("changing screen")
                self.old_scene = self.active_scene
                self.timer = dt.now()
            if self.active_scene.name not in ['home', 'loading']:
                if (dt.now() - self.timer) > delay:
                    print("delayed")
                    self.active_scene = self.active_scene.next_scene

            # if loading screen loaded than go to next
            if hasattr(self.active_scene, 'loading_complete'):
                if self.active_scene.loading_complete:
                    self.active_scene = self.active_scene.next_scene

            # set data to send the clients
            new_page = self.utility.page_selector(self.active_scene)
            if new_page:
                if hasattr(self, new_page):
                    self.active_scene = getattr(self, new_page)
            # Update and tick
            pygame.display.update()
            self.clock.tick(self.FPS)

        pygame.quit()
    #  Scenes

    class LoadingScene:
        def __init__(self, outer_instance):
            super().__init__()
            self.name = 'loading'
            self.MAIN = outer_instance
            self.MAIN.FPS = 60
            self.next_scene = self.MAIN.SceneHome
            self.BORDER_RECT = [self.MAIN.maxX * .29,
                                self.MAIN.maxY * .45, self.MAIN.maxY * .60, self.MAIN.maxY * .1]
            self.INNER_RECT = [self.MAIN.maxX * .30,
                               self.MAIN.maxY * .46, 0, self.MAIN.maxY * .085]
            self.text = self.MAIN.utility.get_font('digi', 16).render(
                "Loading", 1, self.MAIN.WHITE)

            self.loading_step = 0
            self.loading_complete = False

        def update(self):
            # Loading Bar and variables
            if self.INNER_RECT[2] < self.MAIN.maxY * .58:
                self.loading_step += 1
                self.INNER_RECT[2] = self.loading_step
            else:
                self.loading_complete = True
                # for demo puposes
                # self.loading_step = 0
                # self.INNER_RECT[2] = 0

        def render(self):
            self.MAIN.GS.fill(self.MAIN.BLACK)
            self.MAIN.GS.blit(
                self.text, (self.MAIN.maxY * .35, self.MAIN.maxX * .20))
            pygame.draw.rect(self.MAIN.GS, self.MAIN.GREEN, self.BORDER_RECT)
            pygame.draw.rect(self.MAIN.GS, self.MAIN.BLACK, (self.INNER_RECT[0], self.INNER_RECT[1], int(
                self.INNER_RECT[2]), self.INNER_RECT[3]))

        def terminate(self):
            # self.server_thread.join()
            # self.client_thread.join()
            # self.server.close()
            self.MAIN.activeScene = None

    class HomeScene:
        def __init__(self, outer_instance):
            super().__init__()
            self.name = 'home'
            self.MAIN = outer_instance
            self.MAIN.FPS = 30
            self.cap = cv2.VideoCapture('assets/vector.mp4')
            self.cap.set(3, 640)  # width
            self.cap.set(4, 480)  # height

        def update(self):
            success, img = self.cap.read()
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            imgRGB = numpy.rot90(imgRGB)
            frame = pygame.surfarray.make_surface(imgRGB).convert()
            self.frame = pygame.transform.flip(frame, True, False)

        def render(self):
            self.MAIN.GS.blit(self.frame, (0, 0))

    class CameraScene:
        def __init__(self, outer_instance):
            super().__init__()
            self.name = 'home'
            self.MAIN = outer_instance
            self.MAIN.FPS = 30
            self.cap = cv2.VideoCapture(0)
            self.cap.set(3, 640)  # width
            self.cap.set(4, 480)  # height

        def update(self):
            success, img = self.cap.read()
            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            imgRGB = numpy.rot90(imgRGB)
            self.frame = pygame.surfarray.make_surface(imgRGB).convert()
            # self.frame = pygame.transform.flip(frame, True, False) #if needed flip horizontal

        def render(self):
            self.MAIN.GS.blit(self.frame, (0, 0))

    class ClockScene():
        def __init__(self, outer_instance):
            super().__init__()
            self.name = 'clock'
            self.MAIN = outer_instance
            self.MAIN.FPS = 60
            self.next_scene = self.MAIN.SceneHome
            self.alarm_data = self.MAIN.utility.get_current_alarm()
            if self.alarm_data['status'] == 'on':
                self.alarm_img = pygame.image.load('assets/img/on.png')
            else:
                self.alarm_img = pygame.image.load('assets/img/off.png')

        def create_text(self, text, font, color, x, y):
            text = font.render(text, True, color)
            rect = text.get_rect()
            rect.topleft = (x, y)
            self.screen.blit(text, rect)

        def update(self):
            self.current_time = self.MAIN.utility.get_font(
                'digi', 30).render(self.MAIN.utility.get_current_time(), True, self.MAIN.WHITE)
            self.seconds = self.MAIN.utility.get_font('lux', 7).render(
                self.MAIN.utility.get_current_seconds(), True, self.MAIN.WHITE)
            self.alarm_img = pygame.transform.smoothscale(
                self.alarm_img, (self.MAIN.maxX * .10, self.MAIN.maxY * .12))
            self.alarm = self.MAIN.utility.get_font('lux', 10).render(
                self.alarm_data['alarm'], True, self.MAIN.WHITE)
            self.current_date = self.MAIN.utility.get_font('lux', 6).render(
                self.MAIN.utility.get_current_date(), True, self.MAIN.WHITE)
            # for multiple alarm
            # for item in alarms:
            #     text = self.MAIN.utility.get_font(
            #         'lux', 6).render(item, True, self.MAIN.CYAN)
            #     self.MAIN.GS.blit(text, text.get_rect(
            #         center=(self.MAIN.maxX * .5, self.MAIN.maxY * .6)))

        def render(self):
            self.MAIN.GS.fill(self.MAIN.BLACK)
            self.MAIN.GS.blit(self.current_time, (self.MAIN.maxX * .12, self.MAIN.maxY * .15))
            self.MAIN.GS.blit(self.seconds, (self.MAIN.maxX * .80, self.MAIN.maxY * .35))
            self.MAIN.GS.blit(self.alarm, (self.MAIN.maxX * .31, self.MAIN.maxY * .55))
            self.MAIN.GS.blit(self.alarm_img, (self.MAIN.maxX * .68, self.MAIN.maxY * .57))
            self.MAIN.GS.blit(self.current_date, (self.MAIN.maxX * .29, self.MAIN.maxY * .8))

    class WeatherScene():
        def __init__(self, outer_instance):
            super().__init__()
            self.name = 'weather'
            self.MAIN = outer_instance
            self.MAIN.FPS = 60
            self.next_scene = self.MAIN.SceneHome
            # Poll temperature date from splunk as CSV and parse it
            self.values = ["11.1", "Sağanak Yağışlı", "22 Ağustos", "22.1",
                           "33.1", "44.2", "55.1", "66.1", "77.1"]
            # Upper Deck
            self.today_date = self.MAIN.utility.get_font('lux', 4).render(
                self.MAIN.utility.get_current_date() + '/' + self.MAIN.utility.get_current_time(), 1, self.MAIN.CYAN)

            self.today_img = pygame.image.load('assets/img/01d.png')

            self.today_temp = self.MAIN.utility.get_font('digi', 15).render(
                self.values[0], 1, self.MAIN.RED)

            self.today_desc = self.MAIN.utility.get_font('lux', 4.5).render(
                self.values[1], 1, self.MAIN.WHITE)

            # Lower Deck
            self.day1_img = pygame.image.load('assets/img/01d.png')
            self.day1_temp = self.MAIN.utility.get_font('digi', 10).render(
                self.values[0], 1, self.MAIN.WHITE)

            self.day2_img = pygame.image.load('assets/img/01d.png')
            self.day2_temp = self.MAIN.utility.get_font('digi', 10).render(
                self.values[0], 1, self.MAIN.WHITE)

            self.day3_img = pygame.image.load('assets/img/01d.png')
            self.day3_temp = self.MAIN.utility.get_font('digi', 10).render(
                self.values[0], 1, self.MAIN.WHITE)

            self.day4_img = pygame.image.load('assets/img/01d.png')
            self.day4_temp = self.MAIN.utility.get_font('digi', 10).render(
                self.values[0], 1, self.MAIN.WHITE)

        def update(self):
            self.today_img = pygame.transform.smoothscale(
                self.today_img, (self.MAIN.maxX * .22, self.MAIN.maxY * .27))

            self.day1_img = pygame.transform.smoothscale(
                self.day1_img, (self.MAIN.maxX * .13, self.MAIN.maxY * .17))

            self.day2_img = pygame.transform.smoothscale(
                self.day2_img, (self.MAIN.maxX * .13, self.MAIN.maxY * .17))

            self.day3_img = pygame.transform.smoothscale(
                self.day3_img, (self.MAIN.maxX * .13, self.MAIN.maxY * .17))

            self.day4_img = pygame.transform.smoothscale(
                self.day4_img, (self.MAIN.maxX * .13, self.MAIN.maxY * .17))

        def render(self):
            self.MAIN.GS.fill(self.MAIN.BLACK)

            # Draw Lines
            # yatay 1
            pygame.draw.line(self.MAIN.GS, self.MAIN.GREEN, (0, self.MAIN.maxY * .13),
                             (self.MAIN.maxX, self.MAIN.maxY * .13), 1)
            # yatay 2
            pygame.draw.line(self.MAIN.GS, self.MAIN.GREEN, (0, self.MAIN.maxY * .55),
                             (self.MAIN.maxX, self.MAIN.maxY * .55), 1)
            # dikey üst
            pygame.draw.line(self.MAIN.GS, self.MAIN.GREEN, (self.MAIN.maxX/2, self.MAIN.maxY * .17),
                             (self.MAIN.maxX/2, self.MAIN.maxY * .50), 1)
            # dikey alt 1
            pygame.draw.line(self.MAIN.GS, self.MAIN.GREEN, (self.MAIN.maxX * .25, self.MAIN.maxY * .55),
                             (self.MAIN.maxX/4, self.MAIN.maxY), 1)
            # dikey alt 2
            pygame.draw.line(self.MAIN.GS, self.MAIN.GREEN, (self.MAIN.maxX * .5, self.MAIN.maxY * .55),
                             (self.MAIN.maxX/2, self.MAIN.maxY), 1)
            # dikey alt 3
            pygame.draw.line(self.MAIN.GS, self.MAIN.GREEN, (self.MAIN.maxX * .75, self.MAIN.maxY * .55),
                             (self.MAIN.maxX*0.75, self.MAIN.maxY), 1)

            # Images
            self.MAIN.GS.blit(self.today_img, (self.MAIN.maxX * .13, self.MAIN.maxY * .18))
            self.MAIN.GS.blit(self.day1_img, (self.MAIN.maxX * .07, self.MAIN.maxY * .75))
            self.MAIN.GS.blit(self.day2_img, (self.MAIN.maxX * .32, self.MAIN.maxY * .75))
            self.MAIN.GS.blit(self.day3_img, (self.MAIN.maxX * .57, self.MAIN.maxY * .75))
            self.MAIN.GS.blit(self.day4_img, (self.MAIN.maxX * .82, self.MAIN.maxY * .75))
            # Temperatures
            self.MAIN.GS.blit(self.today_temp, (self.MAIN.maxX * .60, self.MAIN.maxY * .22))
            self.MAIN.GS.blit(self.day1_temp, (self.MAIN.maxX * .03, self.MAIN.maxY * .60))
            self.MAIN.GS.blit(self.day2_temp, (self.MAIN.maxX * .28, self.MAIN.maxY * .60))
            self.MAIN.GS.blit(self.day3_temp, (self.MAIN.maxX * .53, self.MAIN.maxY * .60))
            self.MAIN.GS.blit(self.day4_temp, (self.MAIN.maxX * .78, self.MAIN.maxY * .60))

            # Today Date & Desc
            self.MAIN.GS.blit(self.today_date, (self.MAIN.maxX * .25, self.MAIN.maxY * .03))
            self.MAIN.GS.blit(self.today_desc, (self.MAIN.maxX * .55, self.MAIN.maxY * .40))


# Let's do this!
if __name__ == "__main__":

    g = Init()
    g.start()
    pygame.quit()
