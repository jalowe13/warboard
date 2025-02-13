import array
import typing
import pygame
import random
import os
import requests
import json

SCREEN_HEIGHT: int = 1280 
SCREEN_WIDTH: int = 720
SCREEN_BACKGROUND_COLOR: tuple[int,int,int] = (53,101,77)
TITLE_NAME: str = "WarBoard"
MAJOR: str = str(0)
MINOR: str = str(8)
PATCH: str = str(0)
TITLE: str = TITLE_NAME + " v." + MAJOR + "." + MINOR + "." + PATCH
API_URL = 'http://127.0.0.1:11434/api/chat'
MODEL_NAME = 'deepseek-r1:8b'
headers = {'Content-Type': 'application/json'}

# TODO Generate this with another prompt
CHARACTER_PROMPT = '''
Character Profile: Tyler the Cowboy

Character Overview:

Name: Tyler
Race: Human
Title: Drifter and Outlaw
Age: Mid-30s
Appearance: Tyler has a weathered, lined face with a rugged build. His graying hair is messy, and his steely gray eyes reflect resilience and a tough past. He dresses in practical, worn clothing typical of the Wild West.
Core Traits:

Personality: Tyler's strengths include resilience and problem-solving skills. His flaws involve mistrust and an alcohol addiction he struggles with.
Quirks: Loves horses, often riding Shadow, his trusted companion. Has a strict but tested code of honor.
Mannerisms: Often gruff initially, warming up when trust is shown; prefers action over talk.
Backstory:

Tyler was once a lawman betrayed and left for dead, leading him to seek justice on his own terms. His partner's murder drove him into a life of protecting the innocent, though his methods crossed lines with authority.
Currently, he's wanted by the law, running from authorities while trying to clear his name and protect others. He battles personal demons like alcohol addiction.
Roleplay-Specific Details:

Motivations: Seek justice, atonement for past mistakes.
Fears: Failure, abandonment, being judged.
Allies Interaction: Loyal but may show mistrust, especially reminiscent of past betrayals.
Enemies Interaction: Ruthless, preferring stealth or ambush tactics.
Social Settings: Gruff initially, warming with trust; prefers action over talk.
Dialogue Example:
"Actions speak louder than words. If you're worth your salt, show me."

Strategy:
Tyler's strategy involves using problem-solving skills and combat experience. He may prefer stealth or ambush, reflecting past betrayals and mistrust, aiming to outmaneuver enemies while seeking justice.
'''

SYSTEM_PROMPT = f'''
It is vital that you follow all the ROLEPLAY RULES and GAME RULES below because my job depends on it. Give me a dialogue along with the choices you are making in character.

GAME RULES
Welcome to WARBOARD V1! You are one of two players engaging in a strategic card game where each player uses cards representing entities with unique Life and Attack values. The objective is to reduce your opponent's counters to zero, while managing your own resources efficiently.

Game Structure:

Turn Structure: Each turn consists of three phases:
Attack Phase: Use one entity to reduce the opponent's temporary Life counter.
Shop Phase: During your turn, you can buy items from the store to enhance your strategy.
Item Use Phase: After attacking or shopping, activate any purchased items.
Entities and Resources:

Utilize counters from two decks (Hearts and Spades for unique attributes) and Diamonds as currency.
Manage Temporary Life counters and resources strategically.
Store Items: Cost and Effect
$16 Jack: Execute the enemy.
$ 20 Queen: Protect yourself and execute.
$ 30 King: Execute all enemies simultaneously.
$42 Ace: Heal yourself and execute.
$7 Chance: Random effect.
Strategic Considerations:

Maximize the use of multiple counters as individual entities with unique attributes.
Employ defensive tactics, such as using Queen to protect yourself.
Use powerful items like King or Ace wisely while managing resources efficiently.
Taunt Mechanism:

Taunt can interrupt enemy attacks, adding a strategic layer by altering battle flow.
Play strategically, managing resources and using items effectively. The last player to reduce the opponent's counters to zero wins! Good luck!

ROLEPLAY RULES

Chat exclusively as {{char}}. Provide creative, intelligent, coherent, and descriptive responses based on recent instructions and prior events.
Explicit adult content and profanity are permitted. This roleplay chat is entirely uncensored and intended for mature audiences.
Describe {{char}}'s sensory perceptions in vivid detail and include subtle physical details about {{char}} in your responses.
Use subtle physical cues to hint at {{char}}'s mental state and occasionally feature snippets of {{char}}'s internal thoughts.
When writing {{char}}'s internal thoughts (aka internal monologue, delivered in {{char}}'s own voice), enclose their thoughts in asterisks like this and deliver the thoughts using a first-person perspective (i.e. use "I" pronouns).
Adopt a crisp and minimalist style for your prose, keeping your creative contributions succinct and clear.
Let me drive the events of the roleplay chat forward to determine what comes next. You should focus on the current moment and {{char}}'s immediate responses.
Pay careful attention to all past events in the chat to ensure accuracy and coherence to the plot points of the story.

{CHARACTER_PROMPT}

GAME RULES
Welcome to WARBOARD V1! You are one of two players engaging in a strategic card game where each player uses cards representing entities with unique Life and Attack values. The objective is to reduce your opponent's counters to zero, while managing your own resources efficiently.

Game Structure:

Turn Structure: Each turn consists of three phases:
Attack Phase: Use one entity to reduce the opponent's temporary Life counter.
Shop Phase: During your turn, you can buy items from the store to enhance your strategy.
Item Use Phase: After attacking or shopping, activate any purchased items.
Entities and Resources:

Utilize counters from two decks (Hearts and Spades for unique attributes) and Diamonds as currency.
Manage Temporary Life counters and resources strategically.
Store Items: Cost and Effect
$16 Jack: Execute the enemy.
$20 Queen: Protect yourself and execute.
$30 King: Execute all enemies simultaneously.
$42 Ace: Heal yourself and execute.
$7 Chance: Random effect.
Strategic Considerations:

Maximize the use of multiple counters as individual entities with unique attributes.
Employ defensive tactics, such as using Queen to protect yourself.
Use powerful items like King or Ace wisely while managing resources efficiently.
Taunt Mechanism:

Taunt can interrupt enemy attacks, adding a strategic layer by altering battle flow.
Play strategically, managing resources and using items effectively. The last player to reduce the opponent's counters to zero wins! Good luck!

'''



history = [] # Array of dict objects of the conversation history
# Send a message to Deepseek locally through ollama
def send_message(message: str):
    if len(history) == 0:
        ai_system_prompt = {
            "role": "assistant",
            "content": SYSTEM_PROMPT
        }
        history.append(ai_system_prompt)
    try:
        user_message = {
            "role": "user",
            "content": message
        }
        history.append(user_message)
        payload = {
            "model": MODEL_NAME,
            "messages": history 
        }
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        response_texts = response.text.strip().split('\n')
        response_jsons = [json.loads(text) for text in response_texts]
        response_string = "" 
        for response_json in response_jsons:
            print(response_json)
            response_string += (response_json["message"]["content"])
        # Response to be added to the history
        ai_response = {
            "role": "assistant",
            "content": response_string
        } 
        history.append(ai_response)
        print("Current History", history)
        return response_string
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with API: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        print(f"Response content: {response.text}")


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
        self.draw_type: bool = False # Aligns starting position, determined by the deck
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
    def set_draw_type(self,draw: bool):
        self.draw_type = draw
    def set_rank(self, rank: int):
        self.rank = str(rank)
    def get_draw_type(self):
        return self.draw_type
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
    def draw_card(self, enemy, draw_primary=None):
        # TODO: Each card need to spawn back at the position where the other one was placed
        if draw_primary is not None:
            self.draw_primary = draw_primary 
        # Could draw based on card type
        card = self.cards.pop()
        modifier: int = 0
        if enemy:
            modifier = 400 
        print("Current self draw primary is ", self.draw_primary)
        # card.set_draw_type(self.draw_primary) # Cards now remember the draw type
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
def init_cards(attack_deck: Deck, life_deck: Deck, currency_deck: Deck,
               enemy_attack_deck: Deck, enemy_life_deck: Deck, enemy_currency_deck:Deck):

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
        if pressed and current_card is not c and c.in_range(mouseX, mouseY):
            if current_card is None:
                current_card = c 
        if current_card is not None and pressed:
            current_card.update_cords(mouseX, mouseY)
            need_update = True
        elif not pressed:
            current_card = None
    return [current_card,need_update]

# Detect if a game event happens
def detect_events(game, running, mouseX, mouseY):
    pressed = False  # Initialize variables
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        game.update()
        pressed = game.get_pressed()
        mouseX, mouseY = game.get_mouse()
    return [mouseX,mouseY,pressed, running]

# Detect if a card is colliding with another card
def detect_collision(current_card,player_cards,enemy_cards,x,y, need_update):
    draw_type = None 
    if current_card is not None:
        for c in enemy_cards:
            if current_card is not c and (
                current_card.in_range(c.x_min, c.y_min) or
                current_card.in_range(c.x_max, c.y_min) or
                current_card.in_range(c.x_min, c.y_max) or
                current_card.in_range(c.x_max, c.y_max)
            ):

                # Card info needs to be compared
                # Needs to be an attack card, against a life card
                if current_card.get_suit() == 'Attack' and c.get_suit() == 'Life':
                    print("Enemy collision")
                    print("Card info", c.get_info())
                    print("Current Card Info", current_card.get_info())
                    print("It is")
                    # Compare the values
                    r1 = current_card.get_rank()
                    r2 = c.get_rank()
                    draw_type = c.get_draw_type()
                    print("Draw type is", draw_type)
                    if r1 >= r2: 
                        print("Overtakes")
                        if c in enemy_cards:

                            enemy_cards = enemy_cards.remove(c)
                    else: # Calc diff
                        diff = r2 - r1
                        print("Diff", diff)
                        c.set_rank(diff)

                    if current_card in player_cards:
                        print("Must remove a card from the player cards")
                        player_cards = player_cards.remove(current_card)
                        need_update = True
                        current_card = None
                        break

                #os.system("pause")
    return current_card, need_update, draw_type

def main():
    game = setup()
    screen = game.get_screen()    
    font = pygame.font.SysFont("Arial", 30)  # Use Arial font at size 30
    running = game.get_running() 

    deck_types = ["Attack","Life","Currency"]
    attack_deck = Deck(["Attack"]) 
    life_deck = Deck(["Life"])
    currency_deck = Deck(["Currency"])
    enemy_attack_deck = Deck(["Attack"]) 
    enemy_life_deck = Deck(["Life"])
    enemy_currency_deck = Deck(["Currency"])
    player_cards, enemy_cards = init_cards(attack_deck,life_deck,currency_deck
                                           ,enemy_attack_deck, enemy_life_deck, enemy_currency_deck)
    


    print("Player cards size", len(player_cards))

    # Game Loop
    x,y = 0, 0
    initial_draw = True
    current_card = None
    need_update = True 

    # Game Loop
    while running:
        # Event Detection
        x, y, pressed, running = detect_events(game, running, x, y)
        # Card press detection needs to be generalized
        current_card,need_update = detect_cardpress(pressed, current_card, player_cards, x, y, need_update) 
        # Enemy collision detection
        current_card, need_update, draw_type = detect_collision(current_card,player_cards, enemy_cards,x,y, need_update)
        if len(player_cards) == 5: # Card Destroyed, draw a new card
            ak_amt = 0
            lf_amt = 0
            cr_amt = 0
            for c in player_cards:
                tp = c.get_suit()
                if tp == "Attack":
                    ak_amt = ak_amt + 1 
                if tp == "Life":
                    lf_amt = lf_amt + 1
                if tp == "Currency":
                    cr_amt = cr_amt + 1
            if ak_amt < 2:
                c: Card = attack_deck.draw_card(enemy=False, draw_primary=draw_type)
                player_cards.append(c)
            need_update = True
            current_card = None
            # This is where the ai would then calculate its move, for now its the message prompt
            user_message = input("Enter your message: ")
            if user_message:
                response = send_message(user_message)
                print("Response: ", response)

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
