from ollama import chat
from ollama import ChatResponse
import time
import random
import json
import os
from typing import List, Dict, Any

from conversation import Conversation, SingleMessage
from character import Character
from character_loader import CharacterLoader
from root_character import RootCharacter
from character_action import CharacterActionType
from util.helpers import verbose_print, get_model_id


MODEL_ID = get_model_id()


# organize characters and their history
class CharacterGroup:
  def __init__(self):
    self.character_loader = CharacterLoader()
    self.master = self.character_loader.initialize_master()
    self.root_characters = self.character_loader.initialize_root_characters()
    self.current_characters_limit = 3
    self.current_characters = self.character_loader.initialize_characters()
    self.character_occurrences = {cc.real_name: [0, cc] for cc in self.current_characters}
    self.conversation_history = []
    self.conversation_count = 0
    self.save_frequency = 5  # Save occurrences every 5 conversations
    
    # Ensure cache directory exists
    os.makedirs("cache", exist_ok=True)
    
    # Load existing occurrences if available
    self._load_character_occurrences()
  
  def save_current_characters(self) -> None:
    for cc in self.current_characters:
      cc.save()
      
  def _load_character_occurrences(self) -> None:
    """
    Load character occurrences from the JSON file if it exists.
    """
    try:
      file_path = os.path.join("cache", "_character_occurrence.json")
      if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
          saved_occurrences = json.load(file)
          
          # Update existing character occurrences with saved values
          for char_name, occurrence_data in saved_occurrences.items():
            if char_name in self.character_occurrences:
              # Only update the count, keep the character object
              self.character_occurrences[char_name][0] = occurrence_data["count"]
            else:
              # For characters not currently loaded, we'll just store the count
              # and load the character when needed
              self.character_occurrences[char_name] = [occurrence_data["count"], None]
              
        verbose_print(f"Loaded character occurrences from {file_path}")
    except Exception as e:
      verbose_print(f"Error loading character occurrences: {str(e)}")
      
  def save_character_occurrences(self) -> None:
    """
    Save character occurrences to a JSON file in the cache folder.
    """
    try:
      file_path = os.path.join("cache", "_character_occurrence.json")
      
      # Convert the occurrences to a serializable format
      serializable_occurrences = {}
      for char_name, (count, char_obj) in self.character_occurrences.items():
        serializable_occurrences[char_name] = {
          "count": count,
          "character_name": char_obj.character_name if char_obj else char_name
        }
      
      with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(serializable_occurrences, file, indent=2, ensure_ascii=False)
        
      verbose_print(f"Saved character occurrences to {file_path}")
    except Exception as e:
      verbose_print(f"Error saving character occurrences: {str(e)}")

  def add_character(self, character: Character) -> None:
    """
    Add a character to the current characters list and update occurrences.
    
    Args:
        character: The Character instance to add
    """
    # Add to current characters
    self.current_characters.append(character)
    
    # Update occurrences
    if character.real_name in self.character_occurrences:
      # Character exists in occurrences, update the character object
      self.character_occurrences[character.real_name][1] = character
    else:
      # New character, initialize with count 0
      self.character_occurrences[character.real_name] = [0, character]
    
    # Save occurrences to JSON file
    self.save_character_occurrences()
    
    verbose_print(f"Added character '{character.real_name}' to current characters")

  def get_most_frequent_characters(self, n: int = 5) -> List[tuple]:
    """
    Get the most frequently used characters based on occurrence counts.
    
    Args:
        n: Number of top characters to return
        
    Returns:
        List of tuples (character_name, count, character_obj)
    """
    # Sort characters by occurrence count (descending)
    sorted_chars = sorted(
      [(name, count, char_obj) for name, (count, char_obj) in self.character_occurrences.items()],
      key=lambda x: x[1],
      reverse=True
    )
    
    # Return the top n characters
    return sorted_chars[:n]
    
  def find_popular_characters(self, k: int = 1, pool_size: int = 5) -> List[Character]:
    """
    Randomly select k characters from the most frequently appeared characters.
    
    Args:
        k: Number of characters to select
        pool_size: Size of the pool of most frequent characters to choose from
        
    Returns:
        List of Character objects
    """
    # Get the pool of most frequent characters
    popular_chars = self.get_most_frequent_characters(pool_size)
    
    # Filter out characters with None objects (they might be in the occurrence list but not loaded)
    valid_chars = [(name, count, char_obj) for name, count, char_obj in popular_chars if char_obj is not None]
    
    # If we don't have enough valid characters, load them from cache
    if len(valid_chars) < pool_size:
      for name, count, char_obj in popular_chars:
        if char_obj is None:
          # Try to load the character
          loaded_char = self.character_loader.load_character_by_real_name(name)
          if loaded_char:
            # Update the character object in occurrences
            self.character_occurrences[name][1] = loaded_char
            valid_chars.append((name, count, loaded_char))
            
            # Break if we have enough characters
            if len(valid_chars) >= pool_size:
              break
    
    # Adjust k if we don't have enough characters
    k = min(k, len(valid_chars))
    
    # If we have no valid characters or k is 0, return an empty list
    if k == 0 or not valid_chars:
      return []
    
    # Randomly select k characters from the pool
    selected_indices = random.sample(range(len(valid_chars)), k)
    selected_chars = [valid_chars[i][2] for i in selected_indices]
    
    verbose_print(f"Selected {k} popular characters: {[char.real_name for char in selected_chars]}")
    
    return selected_chars
    
  def invite_popular_characters(self, k: int = 1, pool_size: int = 5) -> None:
    """
    Initialize the current characters with popular characters based on occurrence counts.
    If there aren't enough popular characters, supplement with default characters.
    
    Args:
        k: Number of characters to initialize
        pool_size: Size of the pool of most frequent characters to choose from
    """
    # Get popular characters
    popular_chars = self.find_popular_characters(k, pool_size)
    
    # If we don't have enough popular characters, supplement with default characters
    if len(popular_chars) < k:
      # Calculate how many more characters we need
      remaining = k - len(popular_chars)
      # Get default characters
      default_chars = self.character_loader.select_from_default_characters(remaining)
      # Combine popular and default characters
      self.current_characters = popular_chars + default_chars
    else:
      self.current_characters = popular_chars
    
    # Update character occurrences for the new current characters
    for char in self.current_characters:
      if char.real_name in self.character_occurrences:
        # Update the character object
        self.character_occurrences[char.real_name][1] = char
      else:
        # Initialize with count 0
        self.character_occurrences[char.real_name] = [0, char]
    
    verbose_print(f"Initialized {len(self.current_characters)} characters: {[char.real_name for char in self.current_characters]}")
    
    # Announce the characters that joined the conversation
    character_names = ", ".join([char.character_name for char in self.current_characters])
    self.announce_major_events(f"Popular characters joined the conversation: {character_names}")

  def magi(self, user_input: str) -> None:
    """
    MAGI system - Get responses from all root characters (Melchior, Balthasar, Caspar)
    and display them with EVA-themed ASCII art.
    
    Args:
        user_input: The user's input/query
    """
    # Japanese terms and technical jargon for EVA theme
    jp_terms = [
        "初号機", "使徒", "ネルフ", "セカンドインパクト", "シンクロ率", "エヴァンゲリオン",
        "AT フィールド", "ゼーレ", "ダミープラグ", "LCL", "人類補完計画"
    ]
    
    tech_jargon = [
        "Pattern Blue", "Absolute Terror Field", "S2 Engine", "Evangelion Unit", 
        "Terminal Dogma", "Dummy System", "Progressive Knife", "Umbilical Cable",
        "Entry Plug", "Bakelite Containment", "Synch Ratio", "N2 Mine"
    ]
    
    status_codes = [
        "NERV-SYS-0023", "MAGI-PROT-7721", "EVA-SYNC-9981", "AT-FIELD-3344",
        "LCL-DENS-5566", "TERMINAL-7788", "LILITH-9900", "ADAM-1122"
    ]
    
    print("\n")
    print("=" * 80)
    print("                      MAGI システム 起動中...                      ")
    print("                      MAGI SYSTEM ACTIVATING...                      ")
    print("=" * 80)
    
    # Simulate loading with progress bar
    print("\n[初期化中 / INITIALIZING] ", end="")
    for i in range(20):
        print("■", end="", flush=True)
        time.sleep(0.05)
    print(" 完了 / COMPLETE")
    
    # Random status reports
    for _ in range(3):
        status_code = random.choice(status_codes)
        print(f"[{status_code}] {random.choice(tech_jargon)} status: NOMINAL")
        time.sleep(0.1)
    
    print("\n")
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║                 NERV 汎用人工知能 MAGI SYSTEM                  ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    print(f"[解析中 / ANALYZING] ユーザー入力: {user_input}")
    print(f"[シンクロ率 / SYNCH RATIO] {random.randint(75, 99)}.{random.randint(10, 99)}%")
    
    # Simulate data processing
    print("\n[データ処理中 / PROCESSING DATA] ", end="")
    for i in range(15):
        print("▓", end="", flush=True)
        time.sleep(0.05)
    print(" 完了 / COMPLETE")
    
    # Get responses from each root character
    magi_names = ["メルキオール", "バルタザール", "カスパー"]
    
    all_responses = []  # Store all responses for final analysis
    
    for i, root_char in enumerate(self.root_characters):
        # Create a conversation with just the user input
        conversation = Conversation(messages=[SingleMessage(character=self.master, text=user_input)])
        
        # Simulate MAGI processing
        print(f"\n[MAGI-{i+1} {magi_names[i]} 起動中 / ACTIVATING] ", end="")
        for j in range(10):
            print("●", end="", flush=True)
            time.sleep(0.03)
        print(f" 準備完了 / READY")
        
        # Get response from the root character
        response = root_char.chat_with_messages([{'role': 'user', 'content': user_input}])
        all_responses.append(f"MAGI-{root_char.character_name}: {response}")
        
        # Random technical status
        print(f"[{random.choice(status_codes)}] {random.choice(jp_terms)} {random.choice(['ACTIVE', 'NOMINAL', 'OPTIMAL'])}")
        
        # Display the response with EVA-style formatting
        print(f"\n╔═══ MAGI-{root_char.character_name} // {magi_names[i]} ═{'═' * (50 - len(root_char.character_name))}╗")
        print(f"║                                                                ║")
        print(f"║  思考パターン / THOUGHT PATTERN: {random.choice(['科学者', '母親', '女性'])}                  ║")
        print(f"║  信頼性 / RELIABILITY: {random.randint(95, 99)}.{random.randint(10, 99)}%                       ║")
        print(f"║                                                                ║")
        print(f"║  {random.choice(tech_jargon)} STATUS: ACTIVE                             ║")
        print(f"║  {random.choice(status_codes)}: NOMINAL                              ║")
        print(f"║                                                                ║")
        
        # Format and print the response
        lines = response.split('\n')
        for line in lines:
            # Split long lines
            while len(line) > 62:
                print(f"║  {line[:62]}  ║")
                line = line[62:]
            print(f"║  {line}{' ' * (62 - len(line))}  ║")
        
        print(f"║                                                                ║")
        print(f"╚════════════════════════════════════════════════════════════════╝")
    
    # Simulate final analysis
    print("\n[最終分析中 / FINAL ANALYSIS] ", end="")
    for i in range(25):
        print("█", end="", flush=True)
        time.sleep(0.04)
    print(" 完了 / COMPLETE")
    
    # Call LLM to summarize the responses into a simple decision
    combined_responses = "\n".join(all_responses)
    decision_prompt = f"""
    You are the MAGI supercomputer system from Neon Genesis Evangelion.
    
    The three MAGI supercomputers (Melchior, Balthasar, and Caspar) have analyzed the following query:
    "{user_input}"
    
    Here are their responses:
    {combined_responses}
    
    As the unified MAGI system, synthesize these three perspectives into ONE clear, concise decision or recommendation (maximum 2-3 sentences). 
    Use technical, formal language in the style of NERV's computer systems. Include a simple "APPROVED" or "DENIED" status if appropriate.
    """
    
    # Get the final decision from the LLM
    response = chat(model=MODEL_ID, messages=[
        {'role': 'user', 'content': decision_prompt}
    ])
    final_decision = response.message.content
    
    # Final EVA-themed message
    print("\n")
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║                                                                ║
    ║                MAGI 分析完了 // ANALYSIS COMPLETE              ║
    ║                                                                ║
    ║  AT フィールド: 安定 / STABLE                                  ║
    ║  シンクロ率: 最適 / OPTIMAL                                    ║
    ║  第三新東京市: 安全 / SECURE                                   ║
    ║                                                                ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Display the final decision
    print("\n[MAGI 最終決定 / FINAL DECISION]")
    print("=" * 80)
    print(final_decision)
    print("=" * 80)
    
    # Random final status
    print(f"[NERV-HQ] {random.choice(jp_terms)} status: {random.choice(['NOMINAL', 'OPTIMAL', 'STABLE'])}")
    print(f"[MAGI-SYS] 全システム正常 / All systems normal")
    print("=" * 80)
    print("\n")

  # Group of characters talk
  # First one must answer the user query
  # The rest act on their own will
  # Inject memories for every one at the end
  def converse(self, user_input: str) -> None:
    conversation = Conversation(messages=[SingleMessage(character=self.master, text=user_input)])
    first_character = self.current_characters[0]
    first_text = first_character.chat(user_input)
    conversation.messages.append(SingleMessage(character=first_character, text=first_text))
    self.character_occurrences[first_character.real_name][0] += 1

    characters = [first_character]
    if len(self.current_characters) > 1:
      for cc in self.current_characters[1:]:
        action = cc.react(conversation)
        verbose_print("\n========================\n")
        verbose_print("SIDE CHARACTER ACTION:\n")
        verbose_print(cc.real_name)
        verbose_print(action.__dict__)
        verbose_print("\n========================\n")
        if action.action == CharacterActionType.HIDE:
          continue
        elif action.action == CharacterActionType.CHAT:
          print("\n")
          text = action.text
          conversation.messages.append(SingleMessage(character=cc, text=text))
          characters.append(cc)
          self.character_occurrences[cc.real_name][0] += 1
        else:
          characters.append(cc)

    for c in characters:
      c.inject_new_memory(Conversation(messages=[*conversation.messages]))
    self.conversation_history.append(conversation)
    
    # Increment conversation count and save occurrences periodically
    self.conversation_count += 1
    if self.conversation_count % self.save_frequency == 0:
      self.save_character_occurrences()

  # TODO: async to reduce latency
  def group_interview(self, user_input: str) -> None:
    actions = {}
    for rc in self.root_characters:
      action = rc.interview_characters(user_input, self.current_characters)
      if action not in actions:
        actions[action] = 1
      else:
        actions[action] += 1
    final_action = max(actions, key=actions.get)
    # TODO: create new character, add occurrences
    if final_action.action == CharacterActionType.KEEP_CHARACTERS:
      return
    elif final_action.action == CharacterActionType.SHUFFLE_CHARACTERS:
      current_characters = self.current_characters
      random.shuffle(current_characters)
      self.current_characters = current_characters
      return
    elif final_action.action == CharacterActionType.REMOVE_CHARACTERS:
      current_characters = self.current_characters
      tmp = []
      removed_characters = []
      for cc in current_characters:
        if cc.real_name not in final_action.targets:
          tmp.append(cc)
        else:
          removed_characters.append(cc.real_name)
          cc.save()
      if len(removed_characters) > 0:
        self.announce_major_events(f"{", ".join(removed_characters)} left the conversation.")
      self.current_characters = tmp
      if len(self.current_characters) == 0:
        new_character = self.character_loader.find_most_qualified_character(user_input)
        self.add_character(self.character_loader.initialize_character(new_character.real_name, new_character))
    elif final_action.action == CharacterActionType.ADD_NEW_CHARACTER:
      # Find a qualified character for the user's request
      new_character = self.character_loader.find_most_qualified_character(user_input)
      self.add_character(self.character_loader.initialize_character(new_character.real_name, new_character))
      self.announce_major_events(f"{new_character.character_name} joined the conversation.")
    elif final_action.action == CharacterActionType.FIND_POPULAR_CHARACTERS:
      # Save current characters before replacing them
      for cc in self.current_characters:
        cc.save()
      
      # Initialize with popular characters
      self.invite_popular_characters(k=2, pool_size=5)
    else:
      return

  def announce_major_events(self, events: str) -> str:
    for cc in self.current_characters:
      if cc.last_conversation is None:
        cc.last_conversation = Conversation(messages=[])
      last_conversation = cc.last_conversation
      messages = last_conversation.messages
      cc.last_conversation.messages = [*messages, SingleMessage(
        character=cc,
        text=f"The following events happened: {events}"
      )]

  # save pass history
  # TODO
  def check_point():
    pass
