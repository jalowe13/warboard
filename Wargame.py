import pygame

SCREEN_HEIGHT = 1280
SCREEN_WIDTH = 720
TITLE_NAME = "WarGame"
MAJOR = str(0)
MINOR = str(1)
PATCH = str(0)
TITLE = TITLE_NAME + " v." + MAJOR + "." + MINOR + "." + PATCH

class Block:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.color = (255,0,0)
        self.size_x = 64 
        self.size_y = 89 
        self.x_diff = self.size_x/2
        self.y_diff = self.size_y/2
        self.x_min = self.x - self.x_diff
        self.x_max = self.x + self.x_diff
        self.y_min = self.y - self.y_diff
        self.y_max = self.y + self.y_diff
    def draw(self,screen):
        pygame.draw.rect(screen, self.color, (self.x,self.y,self.size_x,self.size_y))
    def update(self):
        self.x_min = self.x 
        self.x_max = self.x + (2*self.x_diff)
        self.y_min = self.y 
        self.y_max = self.y + (2*self.y_diff)
    def update_cords(self, x, y):
        self.x = x - self.size_x/2
        self.y = y - self.size_y/2
    def in_range(self,x,y):
        if self.x_min <= x <= self.x_max:
            if self.y_min <= y <= self.y_max:
                return True
        return False 


def setup():
    print("Start setup")
    try:
        pygame.init()
    except(e):
        print("Setup failed. Is pygame installed?")
    print("Setup complete")

def main():
    setup()
    screen = pygame.display.set_mode((SCREEN_HEIGHT ,SCREEN_WIDTH))
    pygame.display.set_caption(TITLE)
    running = True
    b = Block(500,500)
    b1 = Block(200,200)

    while running:
        for event in pygame.event.get():
            pressed = pygame.mouse.get_pressed()
            mouseX, mouseY = pygame.mouse.get_pos()
            if pressed[0] and b.in_range(mouseX,mouseY):
                b.update_cords(mouseX, mouseY)
            if pressed[0] and b1.in_range(mouseX,mouseY):
                b1.update_cords(mouseX, mouseY)
            if event.type == pygame.QUIT:
                running = False
            screen.fill((0,0,0))
            b.update()
            b1.update()
        b.draw(screen)
        b1.draw(screen)
        pygame.display.flip()

main()
