from typing import Dict
import re
from i18n_l10n.en_us import LocalizationDictionaryEnUS


class Localization:
    """
    Facility for providing localized messages. This bridge should remain in place but the implementation may change
    to built-in Python localization eventually. I just don't have time to learn it right now.
    """
    class _SecretData:
        _message_dictionary: Dict[str, str] = LocalizationDictionaryEnUS.get_dictionary()

        @property
        def message_dictionary(self):
            return self._message_dictionary

        @message_dictionary.setter
        def message_dictionary(self, dictionary: Dict[str, str]) -> None:
            self._message_dictionary = dictionary

    _instance: _SecretData = _SecretData()

    @staticmethod
    def get_message(message_id: str, *args: str) -> str:
        """
        Fetches a localized version of a message and substitutes custom data into placeholders.
        Args:
            message_id: ID of the message to be displayed
            *args: custom data to insert into the placeholders, one data piece per parameter

        Returns:
            A localized version of the message.
        """
        dictionary: Dict[str, str] = Localization._instance.message_dictionary
        if message_id in dictionary.keys():
            skeleton_text: str = str(dictionary[message_id])

            def replace(match: re.Match) -> str:
                param_index: int = int(match.group(1))
                if param_index >= len(args):
                    return match.group(0)

                param_value: str = args[param_index]

                return ''.join([
                    match.group(0)[0:match.pos],
                    param_value,
                    match.group(0)[match.endpos:-1]
                ])

            return re.sub(r'%%(\d+)', replace, skeleton_text)
        else:
            raise KeyError(f'Message {message_id} localization not available. Provided custom text: {args}')

    @staticmethod
    def use_message_dictionary(dictionary: Dict[str, str]) -> None:
        """
        Assigns a locale dictionary with message ids as keys and localized text as values.

        Localized text may include numbered variables in the form %%n, where n is the zero-based index of custom text
        passed through the args parameter of get_message.
        Args:
            dictionary: the locale dictionary to use

        Returns:
            None
        """
        Localization._instance.message_dictionary = dictionary
