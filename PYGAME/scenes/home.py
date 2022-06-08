import pygame
from get_project_root import root_path  # it is important to call root of project

from utilities import SensorData


class HomeScene:
    def __init__(self, outer_instance):
        super().__init__()
        self.name = 'home'
        self.next_scene = self
        self.PATH = root_path(ignore_cwd=False)
        self.M = outer_instance
        self.Sensors = SensorData()
        self.M.FPS = 30
        self.isCameraOn = True
        self.isCharging = True
        self.render_count = 0
        # ============= main frame =====================
        self.img_frame_rect = [1, self.M.maxY * .14, self.M.maxX * .85, self.M.maxY*.99]
        # ============= battery =====================
        self.battery_outer = [self.M.maxX * .70,
                              self.M.maxY * .03, self.M.maxX * .25, self.M.maxY * .07]
        self.battery_inner = [self.M.maxX * .70,
                              self.M.maxY * .03, 0, self.M.maxY * .07]

        # =================  charge icon ===================
        self.charge_icon = ""
        self.charge_on_icon = pygame.image.load('assets/img/icons/charging_on.png').convert_alpha()
        self.charge_off_icon = pygame.image.load('assets/img/icons/charging.png').convert_alpha()

        # =================  camera icon ===================
        self.camera_icon = ""
        self.camera_on_icon = pygame.image.load('assets/img/icons/camera_on.png').convert_alpha()
        self.camera_off_icon = pygame.image.load('assets/img/icons/camera.png').convert_alpha()

        # ================ moving icons ====================
        self.forward = ((self.M.maxX * .895, self.M.maxY * .38), (self.M.maxX * .935, self.M.maxY * .20), (self.M.maxX * .975, self.M.maxY * .38))
        self.reverse = ((self.M.maxX * .895, self.M.maxY * .50), (self.M.maxX * .935, self.M.maxY * .65), (self.M.maxX * .975, self.M.maxY * .50))
        self.stop = (self.M.maxX * .896, self.M.maxY * .40, self.M.maxX * .08, self.M.maxY * .08)
        self.speed = [self.M.maxX * .88, self.M.maxY * .80, self.M.maxX * .1, self.M.maxY * .12]

        # expressions icons
        self.img = 'sleeping'

    def update(self, img=""):
        self.battery_percentage = self.Sensors.data['BATTERY_PERCENTAGE']
        self.battery_percentage_text = self.M.helper.get_font('digi', 4).render(
            str(self.battery_percentage)+' %', 1, self.M.WHITE)
        self.battery_max = self.M.maxX * .25
        self.battery_level = float(self.battery_max) * float(self.battery_percentage)/100
        self.battery_color = self.M.GREEN
        self.battery_inner[2] = self.battery_level
        if self.battery_percentage < 20:
            self.battery_color = self.M.RED
        elif 21 < self.battery_percentage < 80:
            self.battery_color = self.M.GREEN
        else:
            self.battery_color = self.M.MIDGREEN
        self.isCharging = self.Sensors.data['PLUGGEDIN']
# camera icon changing  by status
        if self.isCameraOn:
            self.camera_icon = pygame.transform.smoothscale(
                self.camera_on_icon, (self.M.maxX * .10, self.M.maxY * .10))
        else:
            self.camera_icon = pygame.transform.smoothscale(
                self.camera_off_icon, (self.M.maxX * .10, self.M.maxY * .10))
        # camera icon changing  by status
        if self.isCharging:
            self.charge_icon = pygame.transform.smoothscale(
                self.charge_on_icon, (self.M.maxX * .13, self.M.maxY * .07))
        else:
            self.charge_icon = pygame.transform.smoothscale(
                self.charge_off_icon, (self.M.maxX * .13, self.M.maxY * .07))

         # speed text will be updated from arduino showing battery for demo
        self.speed_text = self.M.helper.get_font('digi', 4).render(
            str(self.battery_percentage/2), 1, self.M.WHITE)
        # expression frame
        self.frame = pygame.image.load(self.PATH + '/assets/img/icons/'+self.img+'.png').convert_alpha()
        self.frame_rect = self.frame.get_rect(center=(self.M.maxX*.4, self.M.maxY*.6))

    def render(self):
        self.M.GS.fill(self.M.BLACK)
        #  =================  lines  ===================
        pygame.draw.line(self.M.GS, self.M.GREEN, (0, self.M.maxY * .13), (self.M.maxX, self.M.maxY * .13), 1)
        pygame.draw.line(self.M.GS, self.M.GREEN, (self.M.maxX * .86, self.M.maxY * .13), (self.M.maxX * .86, self.M.maxY), 1)
        #  =================  battery icons ===================
        self.M.GS.blit(self.camera_icon, (self.M.maxX * .20, self.M.maxY * .01))
        self.M.GS.blit(self.charge_icon, (self.M.maxX * .45, self.M.maxY * .03))
        pygame.draw.rect(self.M.GS, self.battery_color, self.battery_inner, border_radius=5)
        pygame.draw.rect(self.M.GS, self.M.GRAY, self.battery_outer, 2, border_radius=2)
        self.M.GS.blit(
            self.battery_percentage_text, (self.M.maxX * .80, self.M.maxY * .04))
        # =================  moving icons ===================
        pygame.draw.polygon(self.M.GS, self.M.GREEN, (self.forward))
        pygame.draw.rect(self.M.GS, self.M.GRAY, self.stop, border_radius=5)
        pygame.draw.polygon(self.M.GS, self.M.MIDGREEN, self.reverse)
        pygame.draw.rect(self.M.GS, self.M.MIDGREEN, self.speed, 2, border_radius=1)
        self.M.GS.blit(self.speed_text, (self.M.maxX * .895, self.M.maxY * .83))
        # =================  main icon ===================
        pygame.draw.rect(self.M.GS, self.M.GRAY, self.img_frame_rect)
        self.M.GS.blit(self.frame, self.frame_rect)

    def terminate(self):
        pass
