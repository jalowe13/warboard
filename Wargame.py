import pygame

SCREEN_HEIGHT = 1280
SCREEN_WIDTH = 720
TITLE_NAME = "WarGame"
MAJOR = str(0)
MINOR = str(1)
PATCH = str(0)
TITLE = TITLE_NAME + " v." + MAJOR + "." + MINOR + "." + PATCH

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

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            screen.fill((255,255,255))
        pygame.display.flip()

main()
