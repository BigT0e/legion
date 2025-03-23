from typing import List


class SingleMessage:
  def __init__(self, character, text):
    self.character = character
    self.text = text


class Conversation:
  def __init__(self, messages: List[SingleMessage]=[]):
    self.messages = messages

  def stringify(self, root: bool=False) -> str:
    tmp = ""
    for m in self.messages:
      if root:
        name = m.character.real_name
      else:
        name = m.character.character_name
      tmp += f"{name}: {m.text}\n"
    return tmp

  def format_llm_messages(self) -> List[dict]:
    tmp = []
    for m in self.messages:
      c = m.character
      if c.real_name != "Master":
        role = "user" # assistant or user?
        content = f"Here are the converations from another AI that play as {c.character_name}: {m.text}"
      else:
        role = "user"
        content = m.text
      tmp.append({"role": role, "content": content})
    return tmp
