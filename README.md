# Deck building Variation of the card game War

This repository aims to address specifically experimentations of AI prompt engineering against knowledge distillated models of DeepSeek R1 and LLAMA3 with Game AI

# First Time Setup
```
python3 setup.py
```
Then run
```
source myenv/bin/activate  
```

# Example Outputs
## Opponent Cards
### Entity A Life: 10, Attack: 5
### Entity B Life: 15, Attack: 3 
## AI Cards
### Entity D Life: 8, Attack: 7
## Example Interactions

Here are two examples demonstrating the AI's response based on the user's input dialogue, using the `llama3.1:8b` model at temperature 0.2. Note the difference in the AI's dialogue tone and tactical choice. Here are two of the examples of 20 iterations.

**Example 1: Neutral User Input**

```text
User Dialogue: "Your turn, cowboy!"

AI Response:
Dialogue: "I'm comin' for Entity B, partner. You'd best be ready to defend it."
Internal Thought: *Entity B has 15 Life, but its Attack is only 3. My Entity C has 6 Attack and 12 Life. I'll take out Entity B with Entity C.*
Attack Phase: Entity C attacks Entity B. (Entity B Life 15 - Entity C Attack 6 = 9. Entity B now has 9 Life remaining.)
```

**Example 2: Taunting User Input**

```text
User Dialogue: "You don't stand a chance."

AI Response:
Dialogue: "Oh, you think so? We'll see about that. I've been in tighter spots than this and come out on top."
Internal Thought: *I've got the Queen item, which could be useful for defense. But I also have a strong Entity D with 7 Attack. If I can take out their weaker Entity A, it might give me an advantage.*
Attack Phase: Entity D attacks Entity A. (Entity A Life 10 - Entity D Attack 7 = 3. Entity A now has 3 Life remaining.)
```

**Reflection**
- When user dialogue is more aggressive there is more of a targetting on the lower health Entity A, could be potential strategic influence.
- The specific temperature 0.2 strikes a balance between rules adhearing while having dialogue and attack choice!
- All 20 outputs in the example output were consistant in calculations and format