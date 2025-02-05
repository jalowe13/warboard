import array
import typing
import pygame
import random
import os

SCREEN_HEIGHT: int = 1280 
SCREEN_WIDTH: int = 720
SCREEN_BACKGROUND_COLOR: tuple[int,int,int] = (53,101,77)
TITLE_NAME: str = "WarBoard"
MAJOR: str = str(0)
MINOR: str = str(7)
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
    def get_rank(self):
        if self.rank == 'Jack':
            return 10
        if self.rank == 'Queen':
            return 11
        if self.rank == 'King':
            return 12
        if self.rank == 'Ace':
            return 13
        return int(self.rank)
    def set_rank(self, rank: int):
        self.rank = str(rank) 
    def get_info(self):
        return f"{self.rank} of {self.suit}"
    def get_cords(self):
        return [self.x,self.y]
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
        # self.x_min = self.x 
        # self.x_max = self.x + (2*self.x_diff)
        # self.y_min = self.y 
        # self.y_max = self.y + (2*self.y_diff)
        self.x_min = self.x 
        self.y_min = self.y 
        self.x_max = self.x + self.size_x 
        self.y_max = self.y + self.size_y
    def update_cords(self, x, y): # Update card position
        self.x = x - self.size_x/2
        self.y = y - self.size_y/2
        self.update()
    def in_range(self,x,y): # Check range of input x y in relation to the card
        if self.x_min <= x <= self.x_max and self.y_min <= y <= self.y_max:
            return True
        return False
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

    # Draws a card onto the screen, this does the initial position and constructor spawning
    def draw_card(self, enemy):
        # Could draw based on card type
        card = self.cards.pop()
        modifier: int = 0
        if enemy:
            modifier = 400 
        print("Current self draw primary is ", self.draw_primary)
        if self.draw_primary:  
            #self.draw_primary = False
            if card.get_suit() == "Attack":
                card.update_cords(SCREEN_WIDTH/2 ,SCREEN_HEIGHT/2.5 - modifier)
            elif card.get_suit() == "Life":
                card.update_cords(SCREEN_WIDTH/2 + 3 * card.x_max,SCREEN_HEIGHT/2.5 - modifier)
            elif card.get_suit() == "Currency":
                card.update_cords(SCREEN_WIDTH/2 + card.x_max,SCREEN_HEIGHT/2 - modifier)
            self.draw_primary = False
        else:
            print("Draw primary is not false")
            if card.get_suit() == "Attack":
                card.update_cords(SCREEN_WIDTH + 6*card.x_max ,SCREEN_HEIGHT/2.5 - modifier)
            if card.get_suit() == "Life":
                card.update_cords(SCREEN_WIDTH + 9*card.x_max,SCREEN_HEIGHT/2.5 - modifier)
            elif card.get_suit() == "Currency":
                card.update_cords(SCREEN_WIDTH + 7*card.x_max,SCREEN_HEIGHT/2 - modifier)
            self.draw_primary = True
        print("The card drawn was ", card.get_info(), card.get_cords())
        print("There are now ", len(self.cards), " left")
        return card

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
    screen.fill(SCREEN_BACKGROUND_COLOR, (10, 10, 50, 30))  
    fps = str(int(game.get_fps()))
    fps_text = font.render(fps, True, (255, 255, 255))  # Render text in white
    screen.blit(fps_text, (10, 10))  # Draw text at position (10, 10)

# Intialize Player Cards and Enemy Cards 
def init_cards():
    attack_deck = Deck(["Attack"]) 
    life_deck = Deck(["Life"])
    currency_deck = Deck(["Currency"])
    enemy_attack_deck = Deck(["Attack"]) 
    enemy_life_deck = Deck(["Life"])
    enemy_currency_deck = Deck(["Currency"])
    player_cards: array[Card] = [] 
    enemy_cards: array[Card] = []
    # Generate set of attack, life, and currency cards
    c: Card = attack_deck.draw_card(enemy=False)
    c1: Card = life_deck.draw_card(enemy=False)
    c2: Card = currency_deck.draw_card(enemy=False)
    c3: Card = attack_deck.draw_card(enemy=False)
    c4: Card = life_deck.draw_card(enemy=False)
    c5: Card = currency_deck.draw_card(enemy=False)
    player_cards.append(c)
    player_cards.append(c1)
    player_cards.append(c2)
    player_cards.append(c3)
    player_cards.append(c4)
    player_cards.append(c5)
    ec: Card = enemy_attack_deck.draw_card(enemy=True)
    ec1: Card = enemy_life_deck.draw_card(enemy=True)
    ec2: Card = enemy_currency_deck.draw_card(enemy=True)
    ec3: Card = enemy_attack_deck.draw_card(enemy=True)
    ec4: Card = enemy_life_deck.draw_card(enemy=True)
    ec5: Card = enemy_currency_deck.draw_card(enemy=True)
    enemy_cards.append(ec)
    enemy_cards.append(ec1)
    enemy_cards.append(ec2)
    enemy_cards.append(ec3)
    enemy_cards.append(ec4)
    enemy_cards.append(ec5)
    return [player_cards,enemy_cards]

# Detect if a card press occurs and send a need update request with updated mouse cords
def detect_cardpress(pressed, current_card, player_cards, mouseX, mouseY, need_update):
    for c in player_cards:
        x, y = c.get_cords()
        if pressed and current_card is not c and c.in_range(mouseX, mouseY):
            if current_card is None:
                current_card = c 
        if current_card is not None and pressed:
            current_card.update_cords(mouseX, mouseY)
            need_update = True
        elif not pressed:
            current_card = None
    return [x,y,current_card,need_update]

# Detect if a game event happens
def detect_events(game, running):
    mouseX, mouseY, pressed = 0, 0, False  # Initialize variables
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.update()
        pressed = game.get_pressed()
        mouseX, mouseY = game.get_mouse()
    return [mouseX,mouseY,pressed, running]

# Detect if a card is colliding with another card
def detect_collision(current_card,player_cards,enemy_cards,x,y, need_update):
    if current_card is not None:
        for c in enemy_cards:
            if current_card is not c and (
                current_card.in_range(x, y) or
                current_card.in_range(c.x_min, c.y_min) or
                current_card.in_range(c.x_max, c.y_min) or
                current_card.in_range(c.x_min, c.y_max) or
                current_card.in_range(c.x_max, c.y_max)
            ):
                print("Enemy collision")
                print("Card info", c.get_info())
                print("Current Card Info", current_card.get_info())
                # Card info needs to be compared
                # Needs to be an attack card, against a life card

                if current_card.get_suit() == 'Attack' and c.get_suit() == 'Life':
                    print("It is")
                    # Compare the values
                    r1 = current_card.get_rank()
                    r2 = c.get_rank()
                    if r1 >= r2: 
                        print("Overtakes")
                    else: # Calc diff
                        diff = r2 - r1
                        print("Diff", diff)
                        c.set_rank(diff)

                    if current_card in player_cards:
                        player_cards = player_cards.remove(current_card)
                        need_update = True
                        break

                #os.system("pause")
    return current_card, need_update

def main():
    game = setup()
    screen = game.get_screen()    
    font = pygame.font.SysFont("Arial", 30)  # Use Arial font at size 30
    running = game.get_running() 
    player_cards, enemy_cards = init_cards()

    # Game Loop
    prev_cords = 0, 0
    initial_draw = True
    current_card = None
    need_update = True 

    # Game Loop
    while running:
        # Event Detection
        mouseX, mouseY, pressed, running = detect_events(game, running)
        # Card press detection needs to be generalized
        x,y,current_card,need_update = detect_cardpress(pressed, current_card, player_cards, mouseX, mouseY, need_update) 
        # Enemy collision detection
        current_card, need_update = detect_collision(current_card,player_cards, enemy_cards,x,y, need_update)
        # Only update the screen if needed
        if need_update or initial_draw:
            screen.fill(SCREEN_BACKGROUND_COLOR)
            for c in player_cards:
                c.draw(screen)
            for c in enemy_cards:
                c.draw(screen)
            if current_card is not None:
                current_card.draw(screen) 
            else:
                need_update = False
                initial_draw = False

        display_fps(game, screen, font)
        pygame.display.flip()
        game.get_clock().tick(144)

main()
