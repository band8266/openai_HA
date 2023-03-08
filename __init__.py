import openai
import logging
import random
from homeassistant.helpers import area_registry, template
openai.api_key = ""
_LOGGER = logging.getLogger(__name__)
ATTR_PROMPT = "prompt"
ATTR_TEMP = ""
DEFAULT_NAME = ""
def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""
    def generate_text(call):
        DEFAULT_PROMPT = [
        {"role": "system", "content": "You are a smart home assistant.  The user provides some smart home data and a request. You respond with sarcasm and must be less than 255 characters."}
]
        prompt = DEFAULT_PROMPT
        prompt.append( {"role": "user", "content": call.data.get(ATTR_PROMPT, DEFAULT_NAME) })
        temp = call.data.get(ATTR_TEMP, 1)
        completions = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=prompt,
            max_tokens=50,
            n=1,
            stop=None,
            temperature=temp,
        )
        text = completions.choices[0].message['content']
        hass.states.set("text.openai", text, {"max": 255})
        _LOGGER.warning("openai", prompt)

    hass.services.register("openai", "openai", generate_text)

    # Return boolean to indicate that initialization was successful.
    return True
