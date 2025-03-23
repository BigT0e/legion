from ollama import chat
from ollama import ChatResponse
import time
import random
import os

from constant.commands import EXIT_STRATEGIES
from conversation import Conversation, SingleMessage
from character_group import CharacterGroup
from character import Character
from default_characters import character_jake_peralta, master
from util.helpers import flip_verbose
from util.tts import initialize_tts, toggle_tts, is_tts_enabled


os.environ["MODEL_ID"] = 'llama3.1'
os.environ["VERBOSE"] = "False"


class Legion:
  def __init__(self):
    self.character_group = CharacterGroup()
    # Initialize text-to-speech
    initialize_tts()

  def orchestrate(self) -> None:
    if len(self.character_group.current_characters) > 0:
      opening = f"{self.character_group.current_characters[0].character_name}: {self.character_group.current_characters[0].opening}\n\n{self.character_group.master.character_name}: "
    else:
      opening = f"h3LL0 w0rL?\n\n{self.character_group.master.character_name}: "
    while True:
      user_input = input(opening)
      if user_input.lower() in EXIT_STRATEGIES:
        self.character_group.save_current_characters()
        break
      elif user_input == "SHOW_CURRENT_CHARACTER_GROUP":
        print(self.character_group.__dict__)
      elif user_input == "VERBOSE":
        flip_verbose()
      elif user_input == "TTS":
        # Toggle text-to-speech
        is_enabled = toggle_tts()
        if is_enabled:
          print("Text-to-speech is now ENABLED")
        else:
          print("Text-to-speech is now DISABLED")
      elif user_input.startswith("[MAGI]"):
        self.character_group.magi(user_input)
      else:
        # Root characters perform group interview
        self.character_group.group_interview(user_input)

        # Characters speak in order. Only the first one is guaranteed to speak directly to user
        # TODO: Non-root characters are only aware of the conversations happened when they are "alive"
        # TODO: Root characters knows about the entire conversation history happened when they are active (summarized version at least)
        self.character_group.converse(user_input)

        opening = f"\n\n{self.character_group.master.character_name}: "

  def test_one_character(self) -> None:
    character = character_jake_peralta
    opening = f"{character.opening}\n\n{self.character_group.master.character_name}: "
    while True:
      user_input = input(opening)
      if user_input.lower() in EXIT_STRATEGIES:
        break
      else:
        text = character.chat(user_input)
        conversation = Conversation(messages=[
          SingleMessage(character=master, text=user_input),
          SingleMessage(character=character, text=text)
        ])
        character.inject_new_memory(conversation)
        opening = f"\n\n{self.character_group.master.character_name}: "
