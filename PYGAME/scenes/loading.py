import pygame


class LoadingScene:
    def __init__(self, outer_instance):
        super().__init__()
        self.name = 'loading'
        self.M = outer_instance
        self.M.FPS = 60
        self.next_scene = self.M.SceneHome
        self.BORDER_RECT = [self.M.maxX * .29,
                            self.M.maxY * .45, self.M.maxY * .60, self.M.maxY * .1]
        self.INNER_RECT = [self.M.maxX * .30,
                           self.M.maxY * .46, 0, self.M.maxY * .085]
        self.text = self.M.helper.get_font('digi', 16).render(
            "Loading", 1, self.M.WHITE)

        self.loading_step = 0
        self.loading_complete = False

    def update(self):
        # Loading Bar and variables
        if self.INNER_RECT[2] < self.M.maxY * .58:
            self.loading_step += 1
            self.INNER_RECT[2] = self.loading_step
        else:
            self.loading_complete = True
            # for demo puposes
            # self.loading_step = 0
            # self.INNER_RECT[2] = 0

    def render(self):
        self.M.GS.fill(self.M.BLACK)
        self.M.GS.blit(
            self.text, (self.M.maxY * .35, self.M.maxX * .20))
        pygame.draw.rect(self.M.GS, self.M.GREEN, self.BORDER_RECT)
        pygame.draw.rect(self.M.GS, self.M.BLACK, (self.INNER_RECT[0], self.INNER_RECT[1], int(
            self.INNER_RECT[2]), self.INNER_RECT[3]))

    def terminate(self):
        pass
        # self.M.activeScene = None
