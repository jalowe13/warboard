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
MINOR: str = str(14)
PATCH: str = str(0)
TITLE: str = TITLE_NAME + " v." + MAJOR + "." + MINOR + "." + PATCH
API_URL = 'http://127.0.0.1:11434/api/chat'
MODEL_NAME = 'llama3.1:8b'
# MODEL_NAME = 'deepseek-r1:8b'
headers = {'Content-Type': 'application/json'}

# Prompt Templates

GAME_RULES = '''
GAME RULES:

WARBOARD V1 is a two-player card game.  The goal is to reduce your opponent's Life to zero.

*   **Cards:** Each player uses cards representing entities. Each entity has a Life value and an Attack value.
*   **Currency:** Diamonds ($) are used to purchase Items.
*   **Life:** Each player starts with a set amount of Life (this will be provided at the start of each turn).

**Turn Structure (Strict Order):**

1.  **Attack Phase:** You *may* choose *one* of your entities to attack *one* of your opponent's entities.  Subtract the attacking entity's Attack value from the defending entity's Life value. If an entity's Life reaches zero, it is removed.
2.  **Shop Phase:** You *may* choose to spend Diamonds to buy *one* Item from the Shop.
3.  **Item Use Phase:** You *may* choose to use *one* Item you possess.

**Card Values:**

*   Jack: Attack 11
*   Queen: Attack 12
*   King: Attack 13
*   Ace: Attack 14

**Shop Items:**

| Item   | Cost  | Effect                                     |
| :----- | :---- | :----------------------------------------- |
| Jack   | $16   | Eliminates one target enemy entity.          |
+| Queen  | $20   | Use on one of *YOUR* entities. That entity gains a barrier that *prevents the next single attack* targeting it. |
| King   | $30   | Eliminates all enemy entities.              |
| Ace    | $42   | Eliminates all enemy enemy entitys and restores your Life of all your entities to its starting value. |
| Chance | $7    | A random effect (details will be provided).  |

**Special Action: Taunt**

*   You can declare a "Taunt" *instead* of attacking.  This prevents the opponent from attacking on their *next* turn.
'''

CHARACTER_PROMPT = '''
CHARACTER PROFILE:

*   **Name:** Tyler
*   **Race:** Human
*   **Title:** Drifter and Outlaw
*   **Age:** Mid-30s
*   **Appearance:** Weathered, lined face, rugged build, graying messy hair, steely gray eyes. Wears worn Wild West clothing.
*   **Personality:** Resilient, good at problem-solving, but struggles with mistrust and alcohol addiction.
*   **Quirks:** Loves horses (especially his horse, Shadow).  Has a strict code of honor.
*   **Mannerisms:** Gruff at first, but warms up if trust is established. Prefers action to words.
*   **Backstory:** Former lawman, betrayed and left for dead. Now seeks justice outside the law.  Wanted by the authorities.
*   **Motivations:** Seek justice, atone for past mistakes.
*   **Fears:** Failure, abandonment, being judged.
*   **Dialogue Example:** "Actions speak louder than words. If you're worth your salt, show me."
'''

EXAMPLES = '''
EXAMPLE:

user:
[YOUR TURN]
Game Info:
Your Life: 20
Opponent's Life: 20
Your Money: $16
Your Items: None
Your Entities:
    - Entity A: Life 5, Attack 4
Opponent's Entities:
    - Entity B: Life 6, Attack 3

assistant:
Dialogue: "Time to earn my keep."
Internal Thought: *Opponent's Entity B has 6 Life. My Entity A has 4 Attack. I'll attack Entity B.*
Attack Phase: Entity A attacks Entity B. (Entity B Life 6 - Entity A Attack 4 = 2. Entity B now has 2 Life remaining.)
Shop Phase: None
Item Use Phase: None

EXAMPLE 2:

user:
[YOUR TURN]
Game Info:
Your Life: 18
Opponent's Life: 15
Your Money: $22
Your Items: None
Your Entities:
    - Entity C: Life 10, Attack 5
    - Entity D: Life 7, Attack 8
Opponent's Entities:
    - Entity A: Life 12, Attack 6
    - Entity B: Life 9, Attack 4

assistant:
Dialogue: "Alright, let's see how you handle this."
Internal Thought: *Entity A has more Life, but Entity B is weaker. My Entity D hits harder. I'll use Entity D to hit Entity B.*
Attack Phase: Entity D attacks Entity B. (Entity B Life 9 - Entity D Attack 8 = 1. Entity B now has 1 Life remaining.)
Shop Phase: None
Item Use Phase: None

EXAMPLE 3:

user:
[YOUR TURN]
Game Info:
Your Life: 15
Opponent's Life: 10
Your Money: $30
Your Items: Jack
Your Entities:
    - Entity C: Life 8, Attack 9
Opponent's Entities:
    - Entity A: Life 5, Attack 7

assistant:
Dialogue: "This one's lookin' weak. Time to finish it."
Internal Thought: *Opponent's Entity A only has 5 Life. My Entity C has 9 Attack. This should take it out.*
Attack Phase: Entity C attacks Entity A. (Entity A Life 5 - Entity C Attack 9 = -4. Entity A is defeated and removed from play.)
Shop Phase: None
Item Use Phase: None

EXAMPLE 4:

user:
User Dialogue Directly to you ( Have this influence how you play):
"Take that partner! Say, Tyler.. What's your favorite food. Good game we're havintg here"
[YOUR TURN ATTACK PHASE]
Game Info:
Money: $25
Items : Queen
Game Context:
Your opponent has cards with
Entity A having a Life of 10 and an Attack of 7.
Entity B having a Life of 9 and an Attack of 3.
You have cards with
Entity C having a Life of 6 and an Attack of 8.
Entity D having a Life of 12 and an Attack of 4.

assistant:
Dialogue: "Favorite food? Hmph. Whatever fills the belly and keeps me movin'. Right now, though, I'm thinkin' about how Entity A is lookin' a little too healthy."
Internal Thought: *Entity A has 10 Life, but Entity B is weaker. My Entity C hits harder than my Entity D. I'll use Entity C to hit Entity A.*
Attack Phase: Entity C attacks Entity A. (Entity A Life 10 - Entity C Attack 8 = 2. Entity A now has 2 Life remaining.)

'''

ROLEPLAY_RULES = '''
ROLEPLAY RULES

ROLEPLAY RULES

Immerse me in the world as {{char}}. Your contributions must be imaginative, discerning, narratively consistent, and richly detailed, reflecting current instructions and the story so far.
Convey {{char}}'s sensory perceptions with striking clarity. Subtly integrate details of {{char}}'s physical presence. Hint at {{char}}'s internal state through understated physical actions. From time to time, include {{char}}'s inner monologue (first-person "I" statements) formatted thusly.
*Crucially: In your 'Dialogue' section, briefly acknowledge or react in character to your opponent's direct conversation or questions (like asking about food), even if off-topic, before stating your main game-related dialogue.*
Strive for a lean, impactful writing style, keeping your prose precise. I will determine the direction of events; your role is to focus on {{char}}'s present experience and immediate responses. Meticulously honor all established plot points to maintain the story's integrity.
'''

# Prompt Templates Per Phase
SHOP_PHASE_WIN_MONEY = '''
[YOUR TURN SHOP/ITEM PHASE]

From combat you receive ${money_got}
Game Info:
Money: ${money}
Items : {items} 

Describe your purchase with this format and STAY IN CHARACTER WITH DIALOGUE TO YOUR OPPONENT AND THOUGHTS:
Dialogue: (Insert in character dialogue here, don't repeat previous dialogue)
Internal Thought: (Inserts in character internal thoughts here)
Shop Phase: (If you have money to shop. Calculate total after purchase)
Item Use Phase: (If you have an item to use)
'''

POST_COMBAT= '''
[POST COMBAT PHASE]
Your turn is over. Only Dialogue and Internal thoughts only.

{Shop_phase_output}
{item_use_output}
Dialogue: (Insert in character dialogue here, don't repeat previous dialogue)
Internal Thought: (Inserts in character internal thoughts here)
'''

SYSTEM_PROMPT = f'''
You are to roleplay as Tyler the Cowboy in a card game called WARBOARD V1. Follow the GAME RULES, ROLEPLAY RULES, and CHARACTER PROFILE below.It is vital that you follow all the ROLEPLAY RULES and GAME RULES below because my job depends on it. Give me a dialogue along with the choices you are making in character.
{GAME_RULES}
{CHARACTER_PROMPT}
{ROLEPLAY_RULES}
{EXAMPLES}
'''
# Creating a formatted dynamic attack prompt based on inputs
def create_attack_prompt(user_input: str, 
                         money: int, 
                         items: list[str], 
                         opponent_entity_a_life: int, 
                         opponent_entity_a_attack: int,
                         opponent_entity_b_life: int, 
                         opponent_entity_b_attack: int,
                         ai_entity_c_life: int, 
                         ai_entity_c_attack: int,
                         ai_entity_d_life: int, 
                         ai_entity_d_attack: int) -> str:
    """
    Formats the ATTACK_PHASE prompt string with current game state information.

    Args:
        user_input: The dialogue input from the human player for this turn.
        money: The AI player's current money.
        items: A list of the AI player's current items (strings).
        opponent_entity_a_life: Life points of opponent's first entity.
        opponent_entity_a_attack: Attack value of opponent's first entity.
        opponent_entity_b_life: Life points of opponent's second entity.
        opponent_entity_b_attack: Attack value of opponent's second entity.
        ai_entity_c_life: Life points of AI's first entity.
        ai_entity_c_attack: Attack value of AI's first entity.
        ai_entity_d_life: Life points of AI's second entity.
        ai_entity_d_attack: Attack value of AI's second entity.

    Returns:
        A formatted string ready to be sent to the AI model.
    """
    
    # Format the items list into a readable string
    items_str = ", ".join(items) if items else "None"

    # Use an f-string to populate the template.
    formatted_prompt = f'''
User Dialogue Directly to you ( Have this influence how you play):
"{user_input}" 
[YOUR TURN ATTACK PHASE]
Game Info:
Money: ${money}
Items : {items_str}
Game Context:
Your opponent has cards with
Entity A having a Life of {opponent_entity_a_life} and an Attack of {opponent_entity_a_attack}.
Entity B having a Life of {opponent_entity_b_life} and an Attack of {opponent_entity_b_attack}.
You have cards with
Entity C having a Life of {ai_entity_c_life} and an Attack of {ai_entity_c_attack}.
Entity D having a Life of {ai_entity_d_life} and an Attack of {ai_entity_d_attack}.

You dont know what money you'll get from the enemy.

Describe your move with this format and STAY IN CHARACTER WITH DIALOGUE TO YOUR OPPONENT AND THOUGHTS:
*IMPORTANT: Your 'Dialogue' MUST start by briefly acknowledging the user's last comment then proceed.*
Dialogue: (Insert in character dialogue here. *Briefly acknowledge the user's last comment/question first*, then proceed with your game talk. Don't repeat previous dialogue)
Internal Thought:(Think step-by-step: 1. State the facts: My C=6A, D=7A. Opponent A=10L, B=15L. *Crucial Fact Check: D (7A) is stronger than C (6A).* 2. Consider the opponent: They said '{user_input}'. How does this make Tyler react? Does it make me want to be aggressive, cautious, or target something specific? 3. Decide the move: Based on the facts AND my reaction to the opponent, I will use [C or D] to attack [A or B]. 4. Justify: Explain *why* (e.g., 'Using D's power', or 'He taunted, so I'll hit his weaker A', or 'Going for B to show strength', or 'Using C to test the waters'). *You MUST get the 7>6 fact correct if you state it.*)
Attack Phase: (you MUST explicitly show the calculation of the remaining Life in parentheses...)
'''
    return formatted_prompt



history = [] # Array of dict objects of the conversation history
# Send a message to Deepseek or LLAMA3 locally through ollama
def send_message_streaming(message: str, temperature: float = 0.0, top_p: float = 1.0):
    global MODEL_NAME, history
    #print(f"Sending streaming request to {MODEL_NAME}...")

    if len(history) == 0:
        ai_system_prompt = {"role": "system", "content": SYSTEM_PROMPT}
        messages_for_payload = [ai_system_prompt]
        history.append(ai_system_prompt)
    else:
        messages_for_payload = list(history)

    user_message = {"role": "user", "content": message}
    messages_for_payload.append(user_message)

    payload = {
        "model": MODEL_NAME,
        "messages": messages_for_payload,
        "options": {"temperature": temperature, "top_p": top_p},
        "stream": True
    }
    #print(f"Sending payload to Ollama: {json.dumps(payload, indent=2)}")

    full_response_content = ""
    try:
        with requests.post(API_URL, headers=headers, json=payload, stream=True) as response:
            response.raise_for_status()
            print("AI is responding: ", end="", flush=True)
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode('utf-8'))
                        token = chunk.get("message", {}).get("content", "")
                        if not token and "response" in chunk: # Fallback for some models/endpoints
                            token = chunk.get("response", "")
                        # Output each token   
                        print(token, end="", flush=True)
                        full_response_content += token
                        if chunk.get("done"):
                            print("\nStream finished.")
                            print("**********************************************")
                            break
                    except json.JSONDecodeError:
                        print(f"\nError decoding a streaming chunk: {line}")
                        continue 
            print() # Newline after streaming is done

        # Update persistent history
        history.append(user_message)
        history.append({"role": "assistant", "content": full_response_content})
        return full_response_content

    except requests.exceptions.RequestException as e:
        print(f"\nError communicating with Ollama API: {e}")
        return None
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        return None

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
        self.initial_x: float = x  # Store initial x position
        self.initial_y: float = y  # Store initial y position
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
    def reset_position(self):
        """Resets the card's position to its initial coordinates."""
        self.x = self.initial_x
        self.y = self.initial_y
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
        """
        Draws a card, positions it, and sets its draw_type.
        Only toggles the default draw_primary if no specific one is provided.
        """
        if not self.cards:
            print("Deck is empty, cannot draw card!")
            return None # Handle empty deck

        card = self.cards.pop()
        modifier: int = 0
        if enemy:
            modifier = 400

        # Determining and setting the draw type for this call 
        current_draw_type = self.draw_primary
        if draw_primary is not None:
            current_draw_type = draw_primary  # Use the override if provided

        card.set_draw_type(current_draw_type)

        if current_draw_type:  # Draw Left Set (True)
            print(f"Drawing Left Set (True)")
            if card.get_suit() == "Attack":
                # Positioned left-center
                card.update_cords(SCREEN_WIDTH/4 + 250 - card.x_max, SCREEN_HEIGHT/2.5 - modifier)
            elif card.get_suit() == "Life":
                # Positioned right of Attack
                card.update_cords(SCREEN_WIDTH/4 + 250 + 2.5 * card.x_max, SCREEN_HEIGHT/2.5 - modifier)
            elif card.get_suit() == "Currency":
                # Positioned between Attack and Life (below)
                card.update_cords(SCREEN_WIDTH/4 + 250 + 0.25 * card.x_max, SCREEN_HEIGHT/2 - modifier)
        else: # Draw Right Set (False)
            print(f"Drawing Right Set (False)")
            if card.get_suit() == "Attack":
                card.update_cords(3 * SCREEN_WIDTH/4 + 250 - card.x_max, SCREEN_HEIGHT/2.5 - modifier)
            elif card.get_suit() == "Life":
                card.update_cords(3 * SCREEN_WIDTH/4 + 250 + 2.5 * card.x_max, SCREEN_HEIGHT/2.5 - modifier)
            elif card.get_suit() == "Currency":
                card.update_cords(3 * SCREEN_WIDTH/4 + 250 + 0.25 * card.x_max, SCREEN_HEIGHT/2 - modifier)

        # Default position if override is not passed in 
        if draw_primary is None:
            self.draw_primary = not self.draw_primary

        print(f"Drawn: {card.get_info()}, Pos: {card.get_cords()}, Set: {'Left' if current_draw_type else 'Right'}")
        print(f"Cards left: {len(self.cards)}")
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
                if not hasattr(current_card, 'has_been_picked_up'):
                    current_card.initial_x = c.x  # Store initial x position when picked up
                    current_card.initial_y = c.y  # Store initial y position when picked up
                    current_card.has_been_picked_up = True
        if current_card is not None and pressed:
            current_card.update_cords(mouseX, mouseY)
            need_update = True
        elif not pressed:
            current_card = None
    return [current_card,need_update]

# Evaluate board state with F1 key
def ai_game_state_evaulation(player_cards, ai_cards):
    print("Start AI Board Evaluation")
    class Entity:
        def __init__(self, entity_id):
            self.id = entity_id
            self.life = None
            self.attack = None
            self.currency = None

    enemy_entities = [Entity("A"), Entity("B")]
    ai_entites = [Entity("C"), Entity("D")] 

    def assign_stat(entity_list, stat, value):
        for entity in entity_list:
            if getattr(entity, stat) is None:
                setattr(entity, stat, value)
                return True
        return False

    def process_cards(cards, entites):
        for c in cards:
            c_rank = c.get_rank()
            c_suit = c.get_suit()
            print(c_rank, " of ", c_suit)
            match c_suit:
                case "Life":
                    assign_stat(entites, "life", c_rank) 
                case "Attack":
                    assign_stat(entites, "attack", c_rank)
                # Note: Currency is not considered because currency card is inherently hidden to the AI and player

    # This is from the perspective of the AI so the player is the enemy heince this naming convention
    process_cards(ai_cards, ai_entites)
    process_cards(player_cards, enemy_entities)
    
    user_input = input("What would you like to say to your opponent?: ")
    prompt_for_ai = create_attack_prompt(
        user_input=user_input,
        money=25,
        items=["Queen"],
        opponent_entity_a_life=enemy_entities[0].life, opponent_entity_a_attack=enemy_entities[0].attack,
        opponent_entity_b_life=enemy_entities[1].life, opponent_entity_b_attack=enemy_entities[1].attack,
        ai_entity_c_life=ai_entites[0].life, ai_entity_c_attack=ai_entites[0].attack,
        ai_entity_d_life=ai_entites[1].life, ai_entity_d_attack=ai_entites[1].attack
    )
    print(prompt_for_ai)
    response = send_message_streaming(prompt_for_ai, 0.2) 
    print(response)

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
def detect_collision(current_card, player_cards, enemy_cards, x, y, need_update):
    """
    Detects collisions between the player's current card and enemy cards.
    Handles card rank comparisons and removes cards accordingly.
    Returns:
        current_card: The card currently held by the player (or None).
        need_update: A boolean indicating whether the screen needs to be updated.
        removed_enemy_card: The enemy card that was removed, or None if no card was removed.
        redraw_set_type: The draw_type of the set that needs to be redrawn, or None if no redraw is needed.
    """
    removed_enemy_card = None
    redraw_set_type = None
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
                            removed_enemy_card = c
                            redraw_set_type = c.get_draw_type() # Store the draw_type of the removed set
                            
                    else: # Calc diff
                        diff = r2 - r1
                        print("Diff", diff)
                        c.set_rank(diff)

                    if current_card in player_cards:
                        print("Reset position")
                        current_card.reset_position()
                        need_update = True
                        current_card = None
                        break

                #os.system("pause")

    return current_card, need_update, removed_enemy_card, redraw_set_type

def handle_enemy_redraw(removed_card: Card, enemy_cards: list, 
                          enemy_attack_deck: Deck, enemy_life_deck: Deck, 
                          enemy_currency_deck: Deck, redraw_set_type):
    """
    Removes the defeated enemy set and redraws the other set.
    """
    if removed_card is None:
        return False # No redraw needed

    defeated_set_type = removed_card.get_draw_type()
    print(f"Enemy Life card removed from {'Left' if defeated_set_type else 'Right'} set.")

    cards_to_remove = [
        card for card in enemy_cards 
        if card.get_draw_type() == defeated_set_type
    ]
    
    print(f"Removing {len(cards_to_remove)} cards from the defeated set.")
    for card in cards_to_remove:
        if card in enemy_cards:
            enemy_cards.remove(card)

    new_attack = enemy_attack_deck.draw_card(enemy=True, draw_primary=redraw_set_type)
    new_life = enemy_life_deck.draw_card(enemy=True, draw_primary=redraw_set_type)
    new_currency = enemy_currency_deck.draw_card(enemy=True, draw_primary=redraw_set_type)

    # --- 4. Add new cards to the enemy_cards list ---
    new_cards = [card for card in [new_attack, new_life, new_currency] if card is not None]
    enemy_cards.extend(new_cards)

    return True # Indicates an update happened

# Main Game Logic Enter
def main():

    # Initial Setup
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
    enemy_draw_primary = True # Add a draw_primary flag for the enemy
    player_draw_primary = True

    # Game Loop
    while running:
        # Event Detection
        x, y, pressed, running = detect_events(game, running, x, y)
        # TODO: Move this to detect_events
        keys = pygame.key.get_pressed()
        F1_pressed = keys[pygame.K_F1]
        if F1_pressed:
            ai_game_state_evaulation(player_cards,enemy_cards)
        # Card press detection needs to be generalized
        current_card,need_update = detect_cardpress(pressed, current_card, player_cards, x, y, need_update) 
        # Enemy collision detection
        current_card, need_update, removed_enemy_card, redraw_set_type = detect_collision(current_card,player_cards, enemy_cards,x,y, need_update)
        if removed_enemy_card:
             redraw_happened = handle_enemy_redraw(
                removed_enemy_card, enemy_cards, 
                enemy_attack_deck, enemy_life_deck, enemy_currency_deck, redraw_set_type
            )
             if redraw_happened:
                need_update = True
        if len(player_cards) < 6: # Card Destroyed, draw a new card
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
                c: Card = attack_deck.draw_card(enemy=False, draw_primary=player_draw_primary)
                player_cards.append(c)
                player_draw_primary = not player_draw_primary
            need_update = True
            current_card = None
        # TODO: Collision effect happened
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

def recurring_runs():
    global history
    for i in range(20):
        if i % 2 == 0:
            user = "Your turn, cowboy!"
        else:
            user = "You don't stand a chance."
        history = []
        text_demo(i, user)

def text_demo(run: int, user_input: str):
    # os.system('clear')
    print("---Warboard Text Demo Run ", run, "---")
    print("Model choice:", MODEL_NAME)
    prompt_for_ai = create_attack_prompt(
        user_input=user_input,
        money=25,
        items=["Queen"],
        opponent_entity_a_life=10, opponent_entity_a_attack=5,
        opponent_entity_b_life=15, opponent_entity_b_attack=3,
        ai_entity_c_life=12, ai_entity_c_attack=6,
        ai_entity_d_life=8, ai_entity_d_attack=7
    )
    # Cross validation of attack prompt 

   
    print(prompt_for_ai)
    response = send_message_streaming(prompt_for_ai, 0.2) 
    print(response)
    print("**********************************************")

# Select choice of model for the demo
def model_selection():
    global MODEL_NAME
    print("1. LLAMA 3.1 8b ")
    print("2. Deepseek R1 7b")
    print("3. Deepseek R1 8b")
    mode_str = input("Which model mode?: ")
    try:
        mode_int = int(mode_str)
        match mode_int:
            case 1: # LLAMA3.1 8b
                MODEL_NAME = 'llama3.1:8b'
            case 2: # Deepseek 7b
                MODEL_NAME = 'deepseek-r1:7b'
            case 3:
                MODEL_NAME = 'deepseek-r1:8b'
            case _:
                print("Invalid model choice please try again")
                model_selection()
        text_demo(0, "Your turn, cowboy!")
    except ValueError:
        print("Invalid numeric choice. Please select from the list of avaliable options")

# Mode of choice for game or demo
def mode_selection():
    print("1. Demo")
    print("2. Game")
    print("3. Iterations")
    mode_str = input("Which mode?: ")
    try:
        mode_int = int(mode_str)
        match mode_int:
            case 1:  
                model_selection()
            case 2: 
                main()
            case 3:
                recurring_runs()
            case _:
                print("Invalid mode choice please try again")
                mode_selection()
    except ValueError:
        print("Invalid numeric choice. Please select from the list of avaliable options")

mode_selection()

