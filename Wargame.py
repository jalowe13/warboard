import pygame
import typing
import random

SCREEN_HEIGHT: int = 1920 
SCREEN_WIDTH: int = 1080
SCREEN_BACKGROUND_COLOR: tuple[int,int,int] = (53,101,77)
TITLE_NAME: str = "WarBoard"
MAJOR: str = str(0)
MINOR: str = str(4)
PATCH: str = str(0)
TITLE: str = TITLE_NAME + " v." + MAJOR + "." + MINOR + "." + PATCH

# Global Game State Object
class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN_HEIGHT ,SCREEN_WIDTH))
        self.running: bool = False 
        self.mouseHeld: bool 
        self.mousePos: tuple[float,float] = (0.0,0.0)
    # Setters and Getters
    def set_running(self, running: bool):
        self.running = running
    def get_running(self) -> bool:
        return self.running

    def get_clock(self):
        return self.clock
    def get_fps(self): # Get the total time of the running game
        return self.clock.get_fps()
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


class Deck:
    def __init__(self, suits: [str]):
        self.suits: array[str] = suits 
        # self.suits: array[str] = ["Life", "Currency", "Attack"]
        self.ranks: array[str] = ["Ace", "King", "Queen", "Jack", "10", "9", "8", "7", "6", "5", "4", "3", "2"]
        self.cards: array[Card] = []
        self.draw_primary = True # Determines positioning of next draw of card, toggles each draw
        # Generate pairs
        for s in self.suits:
            for r in self.ranks:
                card = Card(r,s,0,0)
                self.cards.append(card)

        self.shuffle()
    def shuffle(self):
        print("Shuffling...")
        random.shuffle(self.cards)
        self.show_deck()

    def show_deck(self):
        for c in self.cards:
            print(c.get_info())

    def draw_card(self):
        # Could draw based on card type
        card = self.cards.pop()
        if self.draw_primary:  
            #self.draw_primary = False
            if card.get_suit() == "Attack":
                card.update_cords(SCREEN_WIDTH/2 + 2*card.x_max,SCREEN_HEIGHT/4)
            elif card.get_suit() == "Life":
                card.update_cords(SCREEN_WIDTH/2,SCREEN_HEIGHT/4)
            elif card.get_suit() == "Currency":
                card.update_cords(SCREEN_WIDTH/2 + card.x_max,SCREEN_HEIGHT/3)
        print(card.get_cords())
        """"
        else:
            self.draw_primary = True
            if card.get_suit() == "Attack":
                card.update_cords(SCREEN_WIDTH + 2*card.x_max,SCREEN_HEIGHT/4)
            if card.get_suit() == "Life":
                card.update_cords(SCREEN_WIDTH,SCREEN_HEIGHT/4)
            elif card.get_suit() == "Currency":
                card.update_cords(SCREEN_WIDTH + card.x_max,SCREEN_HEIGHT/3)
        """
        print("The card drawn was ", card.get_info())
        print("There are now ", len(self.cards), " left")
        return card
# Card that can be played
class Card:
    def __init__(self, rank:str, suit:str, x:float, y:float):
        self.rank: str = rank
        self.suit: str = suit  
        self.x: float = x
        self.y: float = y
        self.color: tuple[int,int,int] = (255,0,0)
        self.size_x: int = 64 
        self.size_y: int = 89 
        self.x_diff: float = self.size_x/2
        self.y_diff: float = self.size_y/2
        self.x_min: float = self.x - self.x_diff
        self.x_max: float = self.x + self.x_diff
        self.y_min: float = self.y - self.y_diff
        self.y_max: float = self.y + self.y_diff
    def get_suit(self):
        return self.suit
    def get_info(self):
        return f"{self.rank} of {self.suit}"
    def get_cords(self):
        return f"{self.x},{self.y}"
    def draw(self,screen): # Draw card on the screen
        # Card Background
        pygame.draw.rect(screen, self.color, (self.x,self.y,self.size_x,self.size_y))
        font = pygame.font.SysFont("Arial", 30)  # Use Arial font at size 30
        suit_text = font.render(self.suit, True, (255, 255, 255))  # Render text in white
        rank_text = font.render(self.rank, True, (255, 255, 255))  # Render text in white
             
        screen.blit(suit_text, (self.x, self.y))  # Draw text at position (10, 10)
        screen.blit(rank_text, (self.x, self.y + 50))  # Draw text at position (10, 10)
        # Card Face
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
# Display the fps 
def display_fps(game,screen,font):
    fps = str(int(game.get_fps()))
    fps_text = font.render(fps, True, (255, 255, 255))  # Render text in white
    screen.blit(fps_text, (10, 10))  # Draw text at position (10, 10)
def main():
    game = setup()
    screen = game.get_screen()    
    font = pygame.font.SysFont("Arial", 30)  # Use Arial font at size 30
    running = game.get_running() 
    attack_deck = Deck(["Attack"]) 
    life_deck = Deck(["Life"])
    currency_deck = Deck(["Currency"])
    

    player_cards: array[Card] = [] 
    # Generate set of attack, life, and currency cards
    c: Card = attack_deck.draw_card()
    c1: Card = life_deck.draw_card()
    c2: Card = currency_deck.draw_card()
    player_cards.append(c)
    player_cards.append(c1)
    player_cards.append(c2)


    # Game Loop
    while running:
        # Event Detection
        for event in pygame.event.get():
            game.update()
            pressed = game.get_pressed() 
            mouseX, mouseY = game.get_mouse()

            # Card press detection needs to be generalized
            print(len(player_cards))
            for c in player_cards:
                if pressed and c.in_range(mouseX,mouseY):
                    c.update_cords(mouseX, mouseY)
                c.update()
                print("Card updated", c.get_cords(), c.get_info())
            # Global and Menu Detection
            if event.type == pygame.QUIT:
                running = False
            screen.fill(SCREEN_BACKGROUND_COLOR)

            # NOTE: Game Objects Update Function

        # NOTE: Game Objects Draw Function 
        
        # Update all Cards
        for c in player_cards:
            c.draw(screen)
        display_fps(game,screen,font)
        pygame.display.flip()
        game.get_clock().tick(144)

main()
