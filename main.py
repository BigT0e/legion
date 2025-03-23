from legion import Legion
from constant.commands import EXIT_STRATEGIES, SPECIAL_COMMANDS


def display_help():
    """Display available commands to the user."""
    print("\n=== LEGION CHAT SYSTEM ===")
    print("\nAvailable commands:")
    
    print("\nSpecial Commands:")
    for cmd, desc in SPECIAL_COMMANDS.items():
        print(f"  {cmd} - {desc}")
    
    print("\nExit Commands:")
    print(f"  {', '.join(EXIT_STRATEGIES)}")
    
    print("\n=========================\n")

# Display help information at startup
display_help()

# TODO: add personality
# Initialize and start Legion
legion = Legion()
legion.orchestrate()
# legion.test_one_character()
