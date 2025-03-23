from character import Character


class Master(Character):
  def __init__(
    self,
    character_name="User",
    real_name="Master",
    system_prompt=None,
  ):
    super().__init__(
      character_name=character_name,
      real_name=real_name,
      system_prompt=system_prompt,
    )

  def chat(self, user_prompt: str) -> None:
    print("I DO NOT TALK WITH MYSELF")
    raise RuntimeError("FUCK YOU")