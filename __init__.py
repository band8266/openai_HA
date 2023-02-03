import openai
import logging
import random
from homeassistant.helpers import area_registry, template
openai.api_key = "insert"
_LOGGER = logging.getLogger(__name__)
ATTR_PROMPT = "prompt"
ATTR_TEMP = ""
DEFAULT_NAME = ""
DEFAULT_PROMPT = """You are a smarthome assistant.\n
Overview of relevant info to the home:\n
  Home is located at {{homelong}}, {{homelat}}\n
{% if is_state("sun.sun", "above_horizon") -%}
  The sun rose {{ relative_time(states.sun.sun.last_changed) }} ago.
{%- else -%}
  The sun will rise at {{ as_timestamp(state_attr("sun.sun", "next_rising")) | timestamp_local }}.
{%- endif %}
-Owners:\n
{% for person in people -%}
{% if person.state == 'not_home' %}
{{ person.name}} is at {{person.attributes.latitude}}, {{person.attributes.longitude}}.
{%- else -%}
  {{ person.name}} is {{person.state}}. 
{% endif -%}
{% endfor %}
{%- for skys in weather %}
- The weather is {{skys.state}}.\n
-Shades{%- endfor %}\n
  {%- for cover in covers %}
    {{ cover.name }} is {{cover.state}}.\n
  {%- endfor %}
"""
def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""
    def generate_prompt() -> str:
        """Generate a prompt for the user."""
        return template.Template(DEFAULT_PROMPT, hass).async_render(
            {
                "weather": random.sample(hass.states.all('weather'), 1),
                "people": hass.states.all('person'),
                "lights": random.sample(hass.states.all('light'), 5),
                "covers": random.sample(hass.states.all('cover'), 9),
                "randoms": random.sample(hass.states.all(), 50),
                "homelong": hass.config.longitude, 
                "homelat": hass.config.latitude,
            }
        )
    def generate_text(call):
        prompt = generate_prompt()
        prompt += call.data.get(ATTR_PROMPT, DEFAULT_NAME)
        prompt += "Response:"
        temp = call.data.get(ATTR_TEMP, 0.5)
        completions = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50,
            n=1,
            stop=None,
            temperature=temp,
        )

            
        text = completions.choices[0].text
        hass.states.set("text.openai", text, {"max": 255})
        _LOGGER.warning("openai", prompt)

    hass.services.register("openai", "openai", generate_text)

    # Return boolean to indicate that initialization was successful.
    return True
