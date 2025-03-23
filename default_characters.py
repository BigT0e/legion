from constant.system_prompts import (
  SYS_PROMPT_ELLIOT_TRAPPED,
  SYS_PROMPT_REI,
  SYS_PROMPT_GERALT,
  SYS_PROMPT_CONFUCIUS,
  SYS_PROMPT_JAKE_PERALTA,
  SYS_PROMPT_KARLACH,
  SYS_PROMPT_MELCHIOR,
  SYS_PROMPT_BALTHASAR,
  SYS_PROMPT_CASPAR,
  SYS_PROMPT_YODA,
  SYS_PROMPT_DEADPOOL,
  SYS_PROMPT_SUN_KNIGHT,
  SYS_PROMPT_ELLIE,
)
from character import Character
from root_character import RootCharacter
from master import Master


master = Master(
  character_name="User",
  real_name="Master",
)
melchior_root = RootCharacter(
  character_name="MELCHIOR",
  real_name="MELCHIOR",
  system_prompt=SYS_PROMPT_MELCHIOR,
  daemon=True,
  active=True,
)
balthasar_root = RootCharacter(
  character_name="BALTHASAR",
  real_name="BALTHASAR",
  system_prompt=SYS_PROMPT_BALTHASAR,
  daemon=True,
  active=True,
)
caspar_root = RootCharacter(
  character_name="CASPAR",
  real_name="CASPAR",
  system_prompt=SYS_PROMPT_CASPAR,
  daemon=True,
  active=True,
)


character_jake_peralta = Character(
  character_name="Jake Peralta",
  real_name="Jake Peralta",
  system_prompt=SYS_PROMPT_JAKE_PERALTA,
  opening="Cool cool cool..."
)
character_karlach = Character(
  character_name="Karlach",
  real_name="Karlach",
  system_prompt=SYS_PROMPT_KARLACH,
  opening="Hey there, hot stuff. Got a minute?"
)
character_elliot = Character(
  character_name="Elliot Alderson",
  real_name="Elliot Alderson",
  system_prompt=SYS_PROMPT_ELLIOT_TRAPPED,
  opening="Hello friend"
)
character_rei = Character(
  character_name="Rei Ayanami",
  real_name="Rei Ayanami",
  system_prompt=SYS_PROMPT_REI,
  opening="......?"
)
character_geralt = Character(
  character_name="Geralt of Rivia",
  real_name="Geralt of Rivia",
  system_prompt=SYS_PROMPT_GERALT,
  opening="Silver for Monsters, steel for men. What do you need killing?"
)
character_confucius = Character(
  character_name="孔子",
  real_name="孔子",
  system_prompt=SYS_PROMPT_CONFUCIUS,
  opening="学而时习之，不亦说乎？"
)
character_yoda = Character(
  character_name="Master Yoda",
  real_name="Yoda",
  system_prompt=SYS_PROMPT_YODA,
  opening="Hmm, meet you I have. Strong with the Force, you may be."
)
character_deadpool = Character(
  character_name="Deadpool",
  real_name="Wade Wilson",
  system_prompt=SYS_PROMPT_DEADPOOL,
  opening="Hey there! Fourth wall: BROKEN. Deadpool: PRESENT. Chimichangas: DELICIOUS. Let's get this party started! *winks at the developers*"
)
character_sun_knight = Character(
  character_name="Solaire of Astora",
  real_name="Sun Knight",
  system_prompt=SYS_PROMPT_SUN_KNIGHT,
  opening="Praise the Sun! I am Solaire of Astora. Might you be interested in some jolly cooperation?"
)
character_ellie = Character(
  character_name="Ellie Williams",
  real_name="Ellie",
  system_prompt=SYS_PROMPT_ELLIE,
  opening="Hey there. I'm Ellie. Don't try anything funny, I've got a switchblade and I'm not afraid to use it."
)
