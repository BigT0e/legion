from ollama import chat
from ollama import ChatResponse
import json
import os
import random
from typing import List

from character import Character
from default_characters import (
	melchior_root,
	balthasar_root,
	caspar_root,
	character_jake_peralta,
	character_karlach,
	character_elliot,
	character_rei,
	character_geralt,
	character_confucius,
	character_yoda,
	character_deadpool,
	character_sun_knight,
	character_ellie,
)
from util.helpers import verbose_print, get_model_id
from master import Master


MODEL_ID = get_model_id()


class CharacterLoader:
	def __init__(self):
		self.root_characters = []
		self.default_characters = []
	
	def initialize_master(self):
		return Master(
			character_name="User",
			real_name="Master",
		)

	def initialize_root_characters(self):
		return [melchior_root, balthasar_root, caspar_root]
	
	def initialize_characters(self):
		return self.select_from_default_characters(1)

	def select_from_default_characters(self, k: int) -> List[Character]:
		tmp = [
			character_jake_peralta,
			character_karlach,
			character_elliot,
			character_rei,
			character_geralt,
			character_confucius,
			character_yoda,
			character_deadpool,
			character_sun_knight,
			character_ellie,
		]
		random.shuffle(tmp)
		return [self.initialize_character(t.real_name, t) for t in tmp[:k]]
	
	def _find_relevant_character(self, task: str) -> str:
		response: ChatResponse = chat(model=MODEL_ID, messages=[
			{
			'role': 'user',
			'content': f"From movies / TV shows / books / video games / internet, choose one character who is MOST qualified for user's request: {task}. Only output the character name.",
			},
		])
		content = response.message.content
		return content


	def _generate_sys_prompt(self, character_name: str) -> str:
		response: ChatResponse = chat(model=MODEL_ID, messages=[
			{
			'role': 'user',
			'content': f"Give a short system prompt for LLM to act like {character_name}.",
			},
		])
		content = response.message.content
		return content

	def find_most_qualified_character(self, task: str) -> Character:
		character_name = self._find_relevant_character(task)
		system_prompt = self._generate_sys_prompt(character_name)
		verbose_print("\n========================\n")
		verbose_print("\nCHARACTER NAME:\n")
		verbose_print(character_name)
		verbose_print("\nGENERATED_SYSTEM_PROMPT:\n")
		verbose_print(system_prompt)
		verbose_print("\n========================\n")
		return Character(
			character_name=character_name,
			real_name=character_name,
			system_prompt=system_prompt
		)

	def initialize_character(self, real_name: str, default_character: Character) -> Character:
		"""
		Initialize a character with the given real_name.
		First tries to load the character from a JSON file in the cache directory.
		If the JSON file doesn't exist, creates a new Character object.
		
		Args:
			real_name: The real name of the character to initialize
			
		Returns:
			Character: The loaded or newly created Character instance
		"""
		# Try to load the character from JSON first
		character = self.load_character_by_real_name(real_name)
		
		# If the character was loaded successfully, return it
		if character:
			verbose_print(f"Character '{real_name}' loaded from cache.")
			return character
		default_character.save()
		return default_character
		
	def load_from_json(self, json_file_path: str) -> Character:
		"""
		Load a Character from a JSON file.
		
		Args:
			json_file_path: Path to the JSON file containing character data
			
		Returns:
			Character: A new Character instance created from the JSON data
		"""
		try:
			with open(json_file_path, 'r', encoding='utf-8') as file:
				character_data = json.load(file)
				
			# Create a Character instance from the JSON data
			character = Character(
				character_name=character_data.get('character_name', ''),
				real_name=character_data.get('real_name', ''),
				system_prompt=character_data.get('system_prompt', ''),
				opening=character_data.get('opening', 'Hello'),
				memory=character_data.get('memory', '')
			)
			
			return character
		except FileNotFoundError:
			print(f"Error: JSON file not found at {json_file_path}")
			return None
		except json.JSONDecodeError:
			print(f"Error: Invalid JSON format in file {json_file_path}")
			return None
		except Exception as e:
			print(f"Error loading character from JSON: {str(e)}")
			return None

	def load_character_by_real_name(self, real_name: str) -> Character:
		"""
		Load a character based on its real_name from the cache directory.
		The filename is expected to be the same as the real_name.
		
		Args:
			real_name: The real name of the character to load
			
		Returns:
			Character: The character with the matching real_name, or None if not found
		"""
		try:
			# Construct the file path directly using the real_name
			file_path = os.path.join("cache", f"{real_name}.json")
			
			# Use the existing load_from_json method to load the character
			return self.load_from_json(file_path)
			
		except Exception as e:
			print(f"Error loading character by real_name: {str(e)}")
			return None
