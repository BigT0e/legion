from enum import Enum
from typing import List


class CharacterActionType(Enum):
  NOTHING = "nothing"
  HIDE = "hide"
  CHAT = "chat"
  KEEP_CHARACTERS = "keep_characters"
  SHUFFLE_CHARACTERS = "shuffle_characters"
  REMOVE_CHARACTERS = "remove_characters"
  ADD_NEW_CHARACTER = "add_new_character"
  FIND_POPULAR_CHARACTERS = "find_popular_characters"


class CharacterAction:
  def __init__(self, action: CharacterActionType, text: str="", targets: List[str]=[], from_root: bool=False):
    self.action = action
    self.text = text
    self.targets = targets
    self.from_root = from_root
  
  def __eq__(self, other):
    return self.action == other.action and self.text == other.text and self.targets == other.targets and self.from_root == other.from_root
  
  def __hash__(self):
    return hash((self.action, self.text, str(self.targets), self.from_root))

