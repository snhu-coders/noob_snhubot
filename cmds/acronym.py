import random
import os

command = 'acronym'
public = True

def execute(command, user):
    acro = command.replace(' ', '') # We don't want spaces

    # Validate that we have some enough characters
    if len(acro) <= 1:
        return 'This isn\'t a random word generator. I need more than one letter.', None

    # Enum-like variables for each part of speech (POS)
    NOUN = 1
    VERB = 2
    ADJECTIVE = 3
    ADVERB = 4
    PREPOSITION = 5

    # Variables to hold our different word lists
    nouns = []
    verbs = []
    adjectives = []
    adverbs = []
    prepositions = []

    base_path = os.path.join('BotHelper', 'Files', 'Words')

    # Read the files
    try:
        with open(os.path.join(base_path, 'Nouns', 'nouns.txt'), 'r') as reader:
            nouns = reader.readlines()

        with open(os.path.join(base_path, 'Verbs', 'verbs.txt'), 'r') as reader:
            verbs = reader.readlines()

        with open(os.path.join(base_path, 'Adjectives', 'adjectives.txt'), 'r') as reader:
            adjectives = reader.readlines()

        with open(os.path.join(base_path, 'Adverbs', 'adverbs.txt'), 'r') as reader:
            adverbs = reader.readlines()

        with open(os.path.join(base_path, 'Prepositions', 'prepositions.txt'), 'r') as reader:
            prepositions = reader.readlines()
    except FileNotFoundError:
        return 'I was unable to locate one of the word files. Please try again later.', None

    result = [] # The final result of words for the given acronym

    # I want to keep track of the parts of speech (POS) to prevent getting combinations
    # that don't make any sense syntactically
    prev_choice = 0 # The previously chosen POS
    choice = 0 # The current POS

     # Loop through each letter of the acronym
    for ch in acro:
        # Determine the next POS options based on the previous one
        # If it's a digit, keep it and then make the next choice a noun
        if ch.isdigit():
            result.append(ch)
            # If adding the digit puts us at the end of the acronym, we're done
            if len(result) == len(acro):
                break
            choice = NOUN # After a number, let's do a noun next
        # If it's not a number or a letter, then it should be skipped
        elif not ch.isalpha():
            continue # skip
        elif prev_choice == 0: # nothing
            choice = random.choice([NOUN,VERB,ADJECTIVE,ADVERB]) # choose POS
        elif prev_choice == NOUN:
            choice = random.choice([NOUN,VERB,ADJECTIVE,ADVERB,PREPOSITION]) 
        elif prev_choice == VERB:
            choice = random.choice([VERB,ADJECTIVE,ADVERB,PREPOSITION]) 
        elif prev_choice == ADJECTIVE:
            choice = random.choice([NOUN,ADJECTIVE]) 
        elif prev_choice == ADVERB:
            choice = random.choice([NOUN,VERB,ADVERB]) 
        elif prev_choice == PREPOSITION:
            choice = NOUN # If we just selected a preposition, a noun next is really all that makes sense
        
        # Now that we have the next choice, let's get a random word.
        # List comprehension to get all the words that begin with the 
        # current letter of the acronym, then chose a random word from 
        # that list and remove the newline character
        if choice == NOUN: 
            result.append(random.choice([x for x in nouns if x.lower().startswith(ch.lower())]).strip())
        elif choice == VERB:
            result.append(random.choice([x for x in verbs if x.lower().startswith(ch.lower())]).strip())
        elif choice == ADJECTIVE:
            result.append(random.choice([x for x in adjectives if x.lower().startswith(ch.lower())]).strip())
        elif choice == ADVERB:
            result.append(random.choice([x for x in adverbs if x.lower().startswith(ch.lower())]).strip())
        elif choice == PREPOSITION:
            result.append(random.choice([x for x in prepositions if x.lower().startswith(ch.lower())]).strip())

        # Update our previous choice
        prev_choice = choice

    return ' '.join(result), None
