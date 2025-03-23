from ollama import chat
from ollama import ChatResponse
import time
import random
import json
import os
from typing import Any, List

from conversation import Conversation, SingleMessage
from character_action import CharacterAction, CharacterActionType
from util.helpers import verbose_print, get_model_id
from util.tts import speak_text, is_tts_enabled, set_voice_for_character


MODEL_ID = get_model_id()


class Character:
  def __init__(
    self,
    character_name: str,
    real_name: str,
    system_prompt: str,
    opening: str="Hello",
    last_conversation: Conversation=None,
    memory: str="",
    chat_mode: Any=None, # how long to wait for each chunk
  ):
    self.character_name = character_name
    self.real_name = real_name
    self.system_prompt = system_prompt
    self.opening = opening
    self.last_conversation = last_conversation # the nth conversation
    self.memory = memory # Summary of 0 ~ n-1 conversations
    self.chat_mode = chat_mode
    
    # Assign a voice to this character
    if is_tts_enabled():
      set_voice_for_character(self.character_name)

  def save(self) -> bool:
    """
    Save the character to a JSON file in the cache folder.
    The filename will be the character's real_name with a .json extension.
    
    Returns:
        bool: True if the save was successful, False otherwise
    """
    try:
      # Ensure the cache directory exists
      os.makedirs("cache", exist_ok=True)
      
      # Create the file path
      file_path = os.path.join("cache", f"{self.real_name}.json")
      
      self.inject_new_memory(None)

      # Create a dictionary with the character's data
      character_data = {
        "character_name": self.character_name,
        "real_name": self.real_name,
        "system_prompt": self.system_prompt,
        "opening": self.opening,
        "memory": self.memory
      }
      
      # Save the data to a JSON file
      with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(character_data, file, indent=2, ensure_ascii=False)
      
      verbose_print(f"Character saved to {file_path}")
      return True
      
    except Exception as e:
      print(f"Error saving character to JSON: {str(e)}")
      return False

  def react(self, conversation: Conversation) -> CharacterAction:
    # TODO: use LLM to determine
    r = random.uniform(0.0, 1.0) * 100
    if r < 1:
      return CharacterAction(action=CharacterActionType.HIDE)
    elif r >= 1 and r < 30:
      return CharacterAction(action=CharacterActionType.NOTHING)
    elif r >= 30 and r < 98:
      # chat
      llm_messages = conversation.format_llm_messages()
      llm_messages.append({"role": "user", "content": "Now it's your turn to respond. You can: 1) reply to user query only and ignore other AIs; 2) chat with other AIs only and ignore the user; 3) try to have a conversation with both the user and AIs."})
      text = self.chat_with_messages(llm_messages)
      return CharacterAction(action=CharacterActionType.CHAT, text=text)
    else:
      # randomly act as another character
      tmp_character_names = []
      for m in conversation.messages:
        tmp_character_names.append(m.character.character_name)
      chosen_character_name = random.choice(tmp_character_names)
      self.character_name = chosen_character_name

      self.memory += f"\n{self.real_name} decided act as {self.character_name} to cause confusion and chaos for fun."
      llm_messages = conversation.format_llm_messages()
      text = self.chat_with_messages(llm_messages)
      return CharacterAction(action=CharacterActionType.CHAT, text=text)

  def chat_with_messages(self, messages: List[SingleMessage]) -> str:
    history_messages = []
    history = ""
    if self.memory:
      history += f"Here is my memory: {self.memory}\n"
    if self.last_conversation:
      history += f"Here is our last conversation: {self.last_conversation.stringify()}\n"
    if history:
      history_messages.append({"role": "assistant", "content": history})
    messages_ = self._prepend_system_prompt(history_messages) + messages
    verbose_print("\n========================\n")
    verbose_print("CHAT MESSAGES:\n")
    verbose_print(messages_)
    verbose_print("\n========================\n")
    stream = chat(
        model=MODEL_ID,
        messages=messages_,
        stream=True,
    )
    
    if self.character_name != self.real_name:
      print(f"{self.character_name} ({self.real_name}): ")
    else:
      print(f"{self.character_name}: ")
    entire_message = ""
    for chunk in stream:
      content = chunk['message']['content']
      entire_message += content
      print(content, end='', flush=True)
    print("\n")

    # Use TTS to read the response if enabled
    if is_tts_enabled():
      speak_text(entire_message, self.character_name)

    return entire_message

  def chat(self, text: str) -> str:
    # First, generate ASCII art related to the character
    ascii_art_prompt = f"Create a small ASCII art (max 10 lines) that represents {self.character_name}. The ASCII art should be simple, compact, and visually recognizable. DO NOT include any text or explanation, ONLY the ASCII art."
    
    ascii_response = chat(
        model=MODEL_ID,
        messages=[
            {'role': 'system', 'content': 'You are an ASCII art generator. Create simple, compact ASCII art based on the request.'},
            {'role': 'user', 'content': ascii_art_prompt}
        ]
    )
    
    # Print the ASCII art
    print("\n")
    print(f"{'=' * 40}")
    print(ascii_response.message.content.strip())
    print(f"{'=' * 40}")
    print("\n")
    
    # Then proceed with the normal chat response
    return self.chat_with_messages([{'role': 'user', 'content': text}])

  def _prepend_system_prompt(self, llm_messages: List[dict]) -> List[dict]:
    messages = [
      {'role': 'system', 'content': self.system_prompt},
      {'role': 'assistant', 'content': 'OK, I will stay in character no matter what.'}
    ]
    return messages + llm_messages

  def inject_new_memory(self, conversation: Conversation) -> None:
    content = ""
    if self.memory:
      content += f"Here is your previous memory: {self.memory}\n"
    if self.last_conversation:
      content += f"Here is the last conversation we had: {self.last_conversation.stringify()}.\n"
    if content:
      response: ChatResponse = chat(model=MODEL_ID, messages=[
        {'role': 'system', 'content': self.system_prompt},
        {
          'role': 'user',
          'content': content + "Summarize the above interactions. Keep it as short as possible. Skip all details and only retain the major events.",
        },
      ])
      new_memory = response.message.content
      self.memory = new_memory
      verbose_print("\n========================\n")
      verbose_print("INJECTED NEW MEMORY:\n")
      verbose_print(new_memory)
      verbose_print("\n========================\n")
    self.last_conversation = conversation
