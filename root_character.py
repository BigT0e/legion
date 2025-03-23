from ollama import chat
from ollama import ChatResponse
import time
import random
from typing import Any, List

from character import Character
from character_action import CharacterAction, CharacterActionType
from util.helpers import verbose_print, get_model_id
from conversation import SingleMessage


MODEL_ID = get_model_id()


class RootCharacter(Character):
  def __init__(
    self,
    character_name: str,
    real_name: str,
    system_prompt: str,
    chat_mode: Any=None,
    daemon: bool=True,
    active: bool=False,
  ):
    super().__init__(
      character_name=character_name,
      real_name=real_name,
      system_prompt=system_prompt,
      chat_mode=chat_mode,
    )
    self.daemon = daemon
    self.active = active

  # judge current characters
  # - KEEP
  # - REMOVE
  # - SHUFFLE
  # - ADD_NEW
  # - FIND_POPULAR
  def interview_characters(self, user_input: str, current_characters: List[Character]=[]) -> CharacterAction:
    if len(current_characters) == 0:
      # If there are no characters, always add a new one
      return CharacterAction(action=CharacterActionType.ADD_NEW_CHARACTER, from_root=True)

    characters = [cc for cc in current_characters]
    character_names = ",".join([c.real_name for c in characters])
    # Create a more detailed prompt that helps the LLM make better decisions
    prompt = f"""
As {self.character_name}, analyze the current conversation situation:

USER REQUEST: "{user_input}"

CURRENT CHARACTERS: {character_names}

In most cases, there should be 1~3 characters in the conversation.
In rare cases, there should be 3~5 characters in the conversation.
There should not be more than 5 characters in the conversation.
Each character speaks in order.
The characters should be well-balanced and diverse.

Based on these rules, choose ONE of the following actions that best fits the user's request:

1. KEEP - If the current characters are well-suited to handle the user's request and should continue the conversation.

2. REMOVE: [character name(s)] - If specific character(s) are inappropriate for this conversation or are not contributing meaningfully. Only remove characters when absolutely necessary.

3. SHUFFLE - If the current characters should remain but their speaking order should be changed to improve the conversation flow.

4. ADD_NEW - If a new character with different expertise or personality would help address the user's request.

5. FIND_POPULAR - If the user's request would be best handled by characters that have been frequently used in past conversations. This is useful when the user wants familiar characters or when popularity-based selection is mentioned.

Consider:
- The expertise and personality of each character
- The nature of the user's request
- The diversity and balance of the current group
- The potential for interesting interactions
- Whether the user is explicitly asking for popular or frequently used characters

RESPOND WITH EXACTLY ONE OF:
- KEEP
- REMOVE: [character name(s)]
- SHUFFLE
- ADD_NEW
- FIND_POPULAR

DO NOT include any explanation or reasoning in your response.
"""

    response: ChatResponse = chat(model=MODEL_ID, messages=[
      {'role': 'system', 'content': self.system_prompt},
      {'role': 'user', 'content': prompt},
    ])
    content = response.message.content.strip()
    verbose_print("\n========================\n")
    verbose_print(f"ROOT INTERVIEW {self.real_name}:\n")
    verbose_print(content)
    verbose_print("\n========================\n")
    
    if content == "KEEP":
      return CharacterAction(action=CharacterActionType.KEEP_CHARACTERS, from_root=True)
    elif content == "SHUFFLE":
      return CharacterAction(action=CharacterActionType.SHUFFLE_CHARACTERS, from_root=True)
    elif content.startswith("ADD_NEW"):
      return CharacterAction(action=CharacterActionType.ADD_NEW_CHARACTER, from_root=True)
    elif content == "FIND_POPULAR":
      return CharacterAction(action=CharacterActionType.FIND_POPULAR_CHARACTERS, from_root=True)
    elif content.startswith("REMOVE:"):
      targets = []
      # Extract character names from the response
      remove_part = content.replace("REMOVE:", "").strip()
      for c in characters:
        # Check if either character_name or real_name is mentioned
        if c.character_name in remove_part or c.real_name in remove_part:
          targets.append(c.real_name)
      
      if targets:
        return CharacterAction(action=CharacterActionType.REMOVE_CHARACTERS, targets=targets, from_root=True)
      else:
        # If no valid targets were found, default to KEEP
        return CharacterAction(action=CharacterActionType.KEEP_CHARACTERS, from_root=True)
    else:
      # If the response doesn't match any expected format, default to KEEP
      print(f"\n********* WARNING: INTERVIEW FAILED with response: {content} *********\n")
      return CharacterAction(action=CharacterActionType.KEEP_CHARACTERS, from_root=True)
  
  def chat_with_messages(self, messages: List[SingleMessage]) -> str:
    messages_ = self._prepend_system_prompt(messages)
    verbose_print("\n========================\n")
    verbose_print("CHAT MESSAGES:\n")
    verbose_print(messages_)
    verbose_print("\n========================\n")
    response: ChatResponse = chat(
        model=MODEL_ID,
        messages=messages_,
    )
    return response.message.content