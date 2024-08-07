# from typing import List, Dict, Any

from ovos_utils import classproperty
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.intents import IntentBuilder
from ovos_workshop.decorators import intent_handler
# from ovos_workshop.intents import IntentHandler # Uncomment to use Adapt intents
from ovos_workshop.skills import OVOSSkill

import json
import os
import random
# import sys

# Optional - if you want to populate settings.json with default values, do so here
DEFAULT_SETTINGS = {
    "PoetrySetting1": True,
    "PoetrySetting2": 50,
    "PoetryFilename": "src/data/poems/BrautiganPoems.json"
}


class TellMeAPoemSkill(OVOSSkill):
    def __init__(self, *args, bus=None, **kwargs):
        """The __init__ method is called when the Skill is first constructed.
        Note that self.bus, self.skill_id, self.settings, and
        other base class settings are only available after the call to super().

        This is a good place to load and pre-process any data needed by your
        Skill, ideally after the super() call.
        """
        super().__init__(*args, bus=bus, **kwargs)
        self.learning = True
        self.poems = []
        poem_file = self.settings.get('PoetryFilename')
        self.load_poems(poem_file)  # Update the path to your JSON file

    def load_poems(self, filepath):
        if not os.path.isfile(filepath):
            self.log.error(f"The file {filepath} does not exist.")
            return

        try:
            with open(filepath, 'r') as file:
                data = json.load(file)

            if 'DOC' in data:
                book_title = data['DOC']['TITLE'][0]
                book_author = data['DOC']['AUTHOR'][0]

                if 'SECTION' in data['DOC']:
                    for section in data['DOC']['SECTION']:
                        section_title = section['SECTIONTITLE'][0] if 'SECTIONTITLE' in section else None

                        for poem in section['POEMS']:
                            self.poems.append({
                                "book_title": book_title,
                                "book_author": book_author,
                                "section_title": section_title,
                                "poem_title": poem['TITLE'][0] if 'TITLE' in poem else "Unknown Title",
                                "poem_author": poem['AUTHOR'][0] if 'AUTHOR' in poem else book_author,
                                "content": poem['CONTENT'][0]
                            })
                else:
                    for poem in data['DOC']['POEMS']:
                        self.poems.append({
                            "book_title": book_title,
                            "book_author": book_author,
                            "section_title": None,
                            "poem_title": poem['TITLE'][0] if 'TITLE' in poem else "Unknown Title",
                            "poem_author": poem['AUTHOR'][0] if 'AUTHOR' in poem else book_author,
                            "content": poem['CONTENT'][0]
                        })
            else:
                self.log.error("Invalid JSON structure: missing 'DOC'")
        except Exception as e:
            self.log.error(f"Error loading poems: {e}")

    def initialize(self):
        # merge default settings
        # self.settings is a jsondb, which extends the dict class and adds helpers like merge
        self.settings.merge(DEFAULT_SETTINGS, new_only=True)

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(
            internet_before_load=False,
            network_before_load=False,
            gui_before_load=False,
            requires_internet=False,
            requires_network=False,
            requires_gui=False,
            no_internet_fallback=True,
            no_network_fallback=True,
            no_gui_fallback=True,
        )

    @property
    def my_setting(self):
        """Dynamically get the my_setting from the skill settings file.
        If it doesn't exist, return the default value.
        This will reflect live changes to settings.json files (local or from backend)
        """
        return self.settings.get("my_setting", "default_value")

    @intent_handler("TellMeAPoem.intent")
    def handle_tell_me_a_poem_intent(self, message):
        """This is a Padatious intent handler.
        It is triggered using a list of sample phrases."""
        poem = random.choice(self.poems)
        self.speak("Here's one of my favorites from the book " + str({poem["book_title"]}))
        self.speak("by " + str({poem["book_author"]}))
        self.speak("the poem is called " + str({poem["poem_title"]}))
        self.speak("and it goes like this ")
        self.speak(str({poem['content']}))

    @intent_handler(IntentBuilder("HelloWorldIntent").require("HelloWorldKeyword"))
    def handle_hello_world_intent(self, message):
        """This is an Adapt intent handler, it is triggered by a keyword.
        Skills can log useful information. These will appear in the CLI and
        the skills.log file."""
        self.log.info("There are five types of log messages: " "info, debug, warning, error, and exception.")
        self.speak_dialog("hello_world")

    @intent_handler(IntentBuilder("RoboticsLawsIntent").require("LawKeyword").build())
    def handle_robotic_laws_intent(self, message):
        """This is an Adapt intent handler, but using a RegEx intent."""
        # Optionally, get the RegEx group from the intent message
        # law = str(message.data.get("LawOfRobotics", "all"))
        self.speak_dialog("robotics")

    def stop(self):
        """Optional action to take when "stop" is requested by the user.
        This method should return True if it stopped something or
        False (or None) otherwise.
        If not relevant to your skill, feel free to remove.
        """
        return
