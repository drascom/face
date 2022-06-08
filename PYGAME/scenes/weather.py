import pygame
from talents.ApiWeather import WeatherApi


class WeatherScene():
    def __init__(self, outer_instance):
        super().__init__()
        self.name = 'weather'
        self.helper = WeatherApi()
        self.data = self.helper.response
        self.M = outer_instance
        self.M.FPS = 60
        self.next_scene = self.M.SceneHome
        # Poll temperature date from splunk as CSV and parse it

        # Upper Deck
        self.today_date = self.M.helper.get_font('lux', 4).render(
            self.M.helper.get_current_date() + '/' + self.M.helper.get_current_time(), 1, self.M.CYAN)

        self.today_img = pygame.image.load(f'assets/img/icons/{self.data["today_icon"]}')

        self.celc_symb = self.M.helper.get_font('lux', 8).render('°', 1, self.M.WHITE)

        self.today_temp = self.M.helper.get_font('digi', 15).render(
            self.data["today_temp"], 1, self.M.RED)

        self.today_desc = self.M.helper.get_font('lux', 4.5).render(
            self.data["today_desc"], 1, self.M.WHITE)

        # Lower Deck
        self.day1_img = pygame.image.load(f'assets/img/icons/{self.data["day1_icon"]}')
        self.day1_temp = self.M.helper.get_font('digi', 10).render(
            self.data["day1_temp"], 1, self.M.WHITE)
        self.day1_date = self.M.helper.get_font('', 4).render(
            self.data["day1_date"], 1, self.M.WHITE)

        self.day2_img = pygame.image.load(f'assets/img/icons/{self.data["day2_icon"]}')
        self.day2_temp = self.M.helper.get_font('digi', 10).render(
            self.data["day2_temp"], 1, self.M.WHITE)
        self.day2_date = self.M.helper.get_font('', 4).render(
            self.data["day2_date"], 1, self.M.WHITE)

        self.day3_img = pygame.image.load(f'assets/img/icons/{self.data["day3_icon"]}')
        self.day3_temp = self.M.helper.get_font('digi', 10).render(
            self.data["day3_temp"], 1, self.M.WHITE)
        self.day3_date = self.M.helper.get_font('', 4).render(
            self.data["day3_date"], 1, self.M.WHITE)

        self.day4_img = pygame.image.load(f'assets/img/icons/{self.data["day4_icon"]}')
        self.day4_temp = self.M.helper.get_font('digi', 10).render(
            self.data["day4_temp"], 1, self.M.WHITE)
        self.day4_date = self.M.helper.get_font('', 4).render(
            self.data["day4_date"], 1, self.M.WHITE)

    def update(self):
        self.today_img = pygame.transform.smoothscale(
            self.today_img, (self.M.maxX * .22, self.M.maxY * .27))

        self.day1_img = pygame.transform.smoothscale(
            self.day1_img, (self.M.maxX * .13, self.M.maxY * .17))

        self.day2_img = pygame.transform.smoothscale(
            self.day2_img, (self.M.maxX * .13, self.M.maxY * .17))

        self.day3_img = pygame.transform.smoothscale(
            self.day3_img, (self.M.maxX * .13, self.M.maxY * .17))

        self.day4_img = pygame.transform.smoothscale(
            self.day4_img, (self.M.maxX * .13, self.M.maxY * .17))

    def render(self):
        self.M.GS.fill(self.M.BLACK)

        # Draw Lines
        # yatay 1
        pygame.draw.line(self.M.GS, self.M.GREEN, (0, self.M.maxY * .13),
                         (self.M.maxX, self.M.maxY * .13), 1)
        # yatay 2
        pygame.draw.line(self.M.GS, self.M.GREEN, (0, self.M.maxY * .55),
                         (self.M.maxX, self.M.maxY * .55), 1)
        # dikey üst
        pygame.draw.line(self.M.GS, self.M.GREEN, (self.M.maxX/2, self.M.maxY * .17),
                         (self.M.maxX/2, self.M.maxY * .50), 1)
        # dikey alt 1
        pygame.draw.line(self.M.GS, self.M.GREEN, (self.M.maxX * .25, self.M.maxY * .55),
                         (self.M.maxX/4, self.M.maxY), 1)
        # dikey alt 2
        pygame.draw.line(self.M.GS, self.M.GREEN, (self.M.maxX * .5, self.M.maxY * .55),
                         (self.M.maxX/2, self.M.maxY), 1)
        # dikey alt 3
        pygame.draw.line(self.M.GS, self.M.GREEN, (self.M.maxX * .75, self.M.maxY * .55),
                         (self.M.maxX*0.75, self.M.maxY), 1)

        # Images
        self.M.GS.blit(self.today_img, (self.M.maxX * .13, self.M.maxY * .18))
        self.M.GS.blit(self.day1_img, (self.M.maxX * .07, self.M.maxY * .75))
        self.M.GS.blit(self.day2_img, (self.M.maxX * .32, self.M.maxY * .75))
        self.M.GS.blit(self.day3_img, (self.M.maxX * .57, self.M.maxY * .75))
        self.M.GS.blit(self.day4_img, (self.M.maxX * .82, self.M.maxY * .75))
        # Temperatures
        self.M.GS.blit(self.today_temp, (self.M.maxX * .66, self.M.maxY * .22))
        self.M.GS.blit(self.celc_symb, (self.M.maxX * .78, self.M.maxY * .22))
        self.M.GS.blit(self.day1_temp, (self.M.maxX * .08, self.M.maxY * .60))
        self.M.GS.blit(self.celc_symb, (self.M.maxX * .17, self.M.maxY * .58))
        self.M.GS.blit(self.day1_date, (self.M.maxX * .11, self.M.maxY * .92))
        self.M.GS.blit(self.day2_temp, (self.M.maxX * .33, self.M.maxY * .60))
        self.M.GS.blit(self.celc_symb, (self.M.maxX * .41, self.M.maxY * .58))
        self.M.GS.blit(self.day2_date, (self.M.maxX * .35, self.M.maxY * .92))
        self.M.GS.blit(self.day3_temp, (self.M.maxX * .58, self.M.maxY * .60))
        self.M.GS.blit(self.celc_symb, (self.M.maxX * .67, self.M.maxY * .58))
        self.M.GS.blit(self.day3_date, (self.M.maxX * .60, self.M.maxY * .92))
        self.M.GS.blit(self.day4_temp, (self.M.maxX * .83, self.M.maxY * .60))
        self.M.GS.blit(self.celc_symb, (self.M.maxX * .91, self.M.maxY * .58))
        self.M.GS.blit(self.day4_date, (self.M.maxX * .86, self.M.maxY * .92))

        # Today Date & Desc
        self.M.GS.blit(self.today_date, (self.M.maxX * .25, self.M.maxY * .03))
        self.M.GS.blit(self.today_desc, (self.M.maxX * .60, self.M.maxY * .45))

    def terminate(self):
        pass
