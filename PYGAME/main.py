# Imports
import os
import pygame

import imutils
from datetime import timedelta, datetime as dt
from utilities import Services, Helper
from scenes import LoadingScene
from scenes import HomeScene
from scenes import CameraScene
from scenes import ClockScene
from scenes import WeatherScene
x = 0
y = 0
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


# now, to clear the screen
cls()


class Init:
    def __init__(self):
        self.services = Services()
        self.helper = Helper()
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
        self.GRAY = (200, 200, 200)
        self.MIDGREEN = (0, 128,   0)
        self.DARKGREEN = (0, 55,   0)
        self.BLUE = (0,   0, 255)
        self.CYAN = (0, 255, 255)
        self.SceneHome = HomeScene(self)
        self.SceneCamera = CameraScene(self)
        self.SceneClock = ClockScene(self)
        self.SceneWeather = WeatherScene(self)
        self.SceneLoading = LoadingScene(self)

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

    def scene_changer(self):
        # if new scene is different than current screne
        if self.active_scene != self.old_scene:
            print("changing screen")
            self.old_scene = self.active_scene
            self.timer = dt.now()
        # check delay and return to home scene
        delay = timedelta(seconds=100)
        if self.active_scene.name not in ['home', 'loading']:
            if (dt.now() - self.timer) > delay:
                print("delayed")
                self.active_scene.terminate()
                self.active_scene = self.active_scene.next_scene
         # if loading screen loaded than go to next
        if hasattr(self.active_scene, 'loading_complete'):
            if self.active_scene.loading_complete:
                self.active_scene = self.active_scene.next_scene
         # if scene changed send new scene name to clients
        new_page = self.services.page_selector(self.active_scene)
        if new_page:
            if hasattr(self, new_page):
                self.active_scene.terminate()
                self.active_scene = getattr(self, new_page)

    def run(self):
        while self.active_scene is not None:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.active_scene.terminate()
                    pygame.quit()
                    quit()

            # all scene change conditions handled by this function
            self.scene_changer()  # <-- important
            # render current page
            if self.active_scene:
                self.active_scene.update()
                self.active_scene.render()

            # Update and tick
            pygame.display.update()

        pygame.quit()
        quit()


# Let's do this!
if __name__ == "__main__":

    g = Init()
    g.start()
    pygame.quit()
