import pygame
import typing

SCREEN_HEIGHT: int = 1280
SCREEN_WIDTH: int = 720
SCREEN_BACKGROUND_COLOR: tuple[int,int,int] = (53,101,77)
TITLE_NAME: str = "WarGame"
MAJOR: str = str(0)
MINOR: str = str(2)
PATCH: str = str(0)
TITLE: str = TITLE_NAME + " v." + MAJOR + "." + MINOR + "." + PATCH

# Global Game State Object
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_HEIGHT ,SCREEN_WIDTH))
        self.running: bool = False 
        self.mouseHeld: bool 
        self.mousePos: tuple[float,float] = (0.0,0.0)
    # Setters and Getters
    def set_running(self, running: bool):
        self.running = running
    def get_running(self) -> bool:
        return self.running
    def get_screen(self): # Returns Pygame Screen
        return self.screen
    def get_pressed(self) -> bool:
        return self.mouseHeld
    def get_mouse(self) -> tuple[float,float]:
        return self.mousePos
    def update(self):
        mouseState = pygame.mouse
        self.mouseHeld = mouseState.get_pressed()[0]
        self.mousePos = mouseState.get_pos()

# Card that can be played
# TODO: Typing on Card Class
class Card:
    def __init__(self, x:float, y:float):
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
    def draw(self,screen): # Draw card on the screen
        pygame.draw.rect(screen, self.color, (self.x,self.y,self.size_x,self.size_y))
    def update(self): # Update card bounding box position 
        self.x_min = self.x 
        self.x_max = self.x + (2*self.x_diff)
        self.y_min = self.y 
        self.y_max = self.y + (2*self.y_diff)
    def update_cords(self, x, y): # Update card position
        self.x = x - self.size_x/2
        self.y = y - self.size_y/2
    def in_range(self,x,y): # Check range of input x y in relation to the card
        if self.x_min <= x <= self.x_max:
            if self.y_min <= y <= self.y_max:
                return True
        return False 


def setup():
    print("Start setup")
    try:
        pygame.init()
        pygame.display.set_caption(TITLE)
        game = Game()

    except(e):
        print("Setup failed. Is pygame installed?")
    print("Setup complete")
    game.set_running(True)
    return game 

def main():
    game = setup()
    screen = game.get_screen()    
    running = game.get_running() 
    c: Card = Card(500,500)
    c1: Card = Card(200,200)

    # Game Loop
    while running:
        # Event Detection
        for event in pygame.event.get():
            game.update()
            pressed = game.get_pressed() 
            mouseX, mouseY = game.get_mouse()

            # Card press detection needs to be generalized
            if pressed and c.in_range(mouseX,mouseY):
                c.update_cords(mouseX, mouseY)
            if pressed and c1.in_range(mouseX,mouseY):
                c1.update_cords(mouseX, mouseY)
            
            # Global and Menu Detection
            if event.type == pygame.QUIT:
                running = False
            screen.fill(SCREEN_BACKGROUND_COLOR)

            # NOTE: Game Objects Update Function
            c.update()
            c1.update()

        # NOTE: Game Objects Draw Function 
        
        # Update all Cards
        c.draw(screen)
        c1.draw(screen)
        pygame.display.flip()

main()
