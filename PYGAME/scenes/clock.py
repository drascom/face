import pygame
from get_project_root import root_path  # it is important to call root of project


class ClockScene():
    def __init__(self, outer_instance):
        super().__init__()
        self.name = 'clock'
        self.M = outer_instance
        self.PATH = root_path(ignore_cwd=False)
        self.M.FPS = 60
        self.next_scene = self.M.SceneHome
        self.alarm_data = self.M.helper.get_current_alarm()
        if self.alarm_data['status'] == 'on':
            self.alarm_img = pygame.image.load(self.PATH+'/assets/img/icons/alarm_on_dark.png')
        else:
            self.alarm_img = pygame.image.load(self.PATH+'/assets/img/icons/alarm_off_dark.png')

    def create_text(self, text, font, color, x, y):
        text = font.render(text, True, color)
        rect = text.get_rect()
        rect.topleft = (x, y)
        self.screen.blit(text, rect)

    def update(self):
        self.current_time = self.M.helper.get_font(
            'digi', 30).render(self.M.helper.get_current_time(), True, self.M.WHITE)
        self.seconds = self.M.helper.get_font('lux', 7).render(
            self.M.helper.get_current_seconds(), True, self.M.WHITE)
        self.alarm_img = pygame.transform.smoothscale(
            self.alarm_img, (self.M.maxX * .10, self.M.maxY * .12))
        self.alarm = self.M.helper.get_font('lux', 10).render(
            self.alarm_data['alarm'], True, self.M.WHITE)
        self.current_date = self.M.helper.get_font('lux', 6).render(
            self.M.helper.get_current_date(), True, self.M.WHITE)
        # for multiple alarm
        # for item in alarms:
        #     text = self.M.helper.get_font(
        #         'lux', 6).render(item, True, self.M.CYAN)
        #     self.M.GS.blit(text, text.get_rect(
        #         center=(self.M.maxX * .5, self.M.maxY * .6)))

    def render(self):
        self.M.GS.fill(self.M.BLACK)
        self.M.GS.blit(self.current_time, (self.M.maxX * .12, self.M.maxY * .15))
        self.M.GS.blit(self.seconds, (self.M.maxX * .80, self.M.maxY * .35))
        self.M.GS.blit(self.alarm, (self.M.maxX * .31, self.M.maxY * .55))
        self.M.GS.blit(self.alarm_img, (self.M.maxX * .68, self.M.maxY * .57))
        self.M.GS.blit(self.current_date, (self.M.maxX * .29, self.M.maxY * .8))

    def terminate(self):
        pass
