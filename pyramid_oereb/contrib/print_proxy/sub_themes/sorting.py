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
        return sorted(sub_themes, key=lambda sub_theme: sub_theme['SubTheme'])


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
        assert 'list' in params
        assert type(params['list']) is list

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
