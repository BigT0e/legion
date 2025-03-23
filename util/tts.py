import pyttsx3
import threading
import os

from util.helpers import verbose_print

# Global TTS engine
_engine = None
_is_enabled = False
_voice_cache = {}

def initialize_tts():
    """Initialize the text-to-speech engine."""
    global _engine, _is_enabled
    try:
        _engine = pyttsx3.init()
        _engine.setProperty('rate', 150)  # Speed of speech
        _engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
        _is_enabled = False
        verbose_print("Text-to-speech initialized successfully.")
        return True
    except Exception as e:
        verbose_print(f"Failed to initialize text-to-speech: {str(e)}")
        _is_enabled = False
        return False

def is_tts_enabled():
    """Check if TTS is enabled."""
    return _is_enabled

def toggle_tts():
    """Toggle text-to-speech on/off."""
    global _is_enabled
    if _engine is None:
        initialize_tts()
    else:
        _is_enabled = not _is_enabled
    return _is_enabled

def get_available_voices():
    """Get a list of available voices."""
    if _engine is None:
        initialize_tts()
    
    if not _is_enabled:
        return []
    
    voices = _engine.getProperty('voices')
    return [(voice.id, voice.name) for voice in voices]

def set_voice_for_character(character_name, voice_id=None):
    """Set a specific voice for a character."""
    global _voice_cache
    
    if not _is_enabled:
        return False
    
    if voice_id is None:
        # If no voice_id is provided, try to assign a voice based on the character name
        voices = get_available_voices()
        if not voices:
            return False
        
        # Simple hash function to consistently assign the same voice to the same character
        voice_index = hash(character_name) % len(voices)
        voice_id = voices[voice_index][0]
    
    _voice_cache[character_name] = voice_id
    return True

def speak_text(text, character_name=None):
    """
    Speak the given text using text-to-speech.
    If character_name is provided, use the voice assigned to that character.
    """
    if not _is_enabled or _engine is None:
        return False
    
    # Use a separate thread to avoid blocking the main program
    def _speak_thread():
        try:
            # Set the voice for the character if available
            if character_name and character_name in _voice_cache:
                _engine.setProperty('voice', _voice_cache[character_name])
            
            try:
                _engine.endLoop()
            except Exception as e:
                print(f"Error ending loop: {str(e)}")
            _engine.say(text)
            _engine.runAndWait()
            _engine.stop()
        except Exception as e:
            print(f"TTS Error: {str(e)}")
    
    # Start the speech in a separate thread
    threading.Thread(target=_speak_thread, daemon=True).start()
    return True 