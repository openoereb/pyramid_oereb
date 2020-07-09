import logging
import sys
import unicodedata

log = logging.getLogger(__name__)


def unaccent_lower(text):
    """
    Replaces all special characters so that an alphabetical sorting can be done.

    Args:
        text (str): The text value.

    Returns:
        new_text (str): The text value converted to lower case and striped of special characters.
    """
    if text is None:
        return ''
    new_text = text.lower() if sys.version_info.major > 2 else unicode(text.lower())  # noqa
    return unicodedata.normalize('NFD', new_text)


class BaseSort(object):
    @staticmethod
    def sort(sub_themes, params):
        """
            Returns the sub themes unsorted (same as input).

            Args:
                sub_themes (list): Array of sub themes
                params (dict): Parameters for sorting algorithm, unused.

            Returns:
                list: Sorted array of sub themes
        """
        return sub_themes


class AlphabeticSort(BaseSort):
    @staticmethod
    def sort(sub_themes, params):
        """
            Returns the sub themes alphabetically sorted (by value of 'SubTheme').

            Args:
                sub_themes (list): Array of sub themes
                params (dict): Parameters for sorting algorithm, unused.

            Returns:
                list: Sorted array of sub themes
        """
        return sorted(sub_themes, key=lambda sub_theme: unaccent_lower(sub_theme['SubTheme']))


class ListSort(BaseSort):
    @staticmethod
    def sort(sub_themes, params):
        """
            Returns the sub themes sorted by an ordered list of sub theme titles.

            Args:
                sub_themes (list): Array of sub themes
                params (dict): Must contain property 'list' with a sorted list of sub theme titles

            Returns:
                list: Sorted array of sub themes
        """
        if 'list' not in params:
            log.error("Missing parameter 'list' for sub theme sorter ListSort")
            return sub_themes

        if not isinstance(params['list'], list):
            log.error("Invalid parameter 'list' for sub theme sorter ListSort")
            return sub_themes

        sorted_sub_themes = []
        for next_sub_theme_title in params['list']:
            matches = list(filter(lambda s: s['SubTheme'] == next_sub_theme_title, sub_themes))

            sorted_sub_themes += matches

            # remove matches from source
            for match in matches:
                sub_themes.remove(match)

        # add left over sub themes unsorted
        sorted_sub_themes += sub_themes

        return sorted_sub_themes
