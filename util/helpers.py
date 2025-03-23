import os


def verbose_print(text: str) -> None:
	verbose = os.environ.get("VERBOSE", "False")
	if verbose == "False":
		return
	print(text)


def flip_verbose() -> None:
	verbose = os.environ.get("VERBOSE", "False")
	if verbose == "False":
		os.environ["VERBOSE"] = "True"
	else:
		os.environ["VERBOSE"] = "False"


def get_model_id() -> str:
	return os.environ.get("MODEL_ID", "llama3.1")
