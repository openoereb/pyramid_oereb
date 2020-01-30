# -*- coding: utf-8 -*-
import logging
import textwrap

log = logging.getLogger(__name__)


class TocPages():

    def __init__(self, extract):
        # variables taken from template toc.jrxml
        self.disposable_height = 842 - 70  # A4 size - (footer + header)
        self.d1_height = 77
        self.d2_height = 29
        self.d3_height = 61
        self.d4_height = 44
        self.d5_height = 15
        self.d6_height = 90
        self.d6_right_height = 23
        self.d6_right_width = 233
        self.d6_stuff_y_location = 39
        self.d6_left_height = 0  # FIXME: compute this
        self.title_size = 62
        self.toc_title_height = 15 + 62 + 12  # height + location + item starting position
        self.toc_item_height = 20
        self.not_concerned_themes_title_height = 15 + 26  # height + location
        self.not_concerned_themes_item_height = 12
        self.theme_without_data_title_height = 12
        self.theme_without_data_item_height = 12
        self.extract = extract
        self.total_length = self.compute_total_lenght()

    def compute_d1(self):
        return self.d1_height

    def compute_d2(self):
        x = len(self.extract['ConcernedTheme'] * self.toc_item_height)
        if x > self.d2_height:
            return x
        else:
            return self.d2_height

    def compute_d3(self):
        x = self.not_concerned_themes_title_height + len(self.extract['NotConcernedTheme'] * self.not_concerned_themes_item_height)  # noqa
        if x > self.d3_height:
            return x
        else:
            return self.d3_height

    def compute_d4(self):
        return self.d4_height

    def compute_d5(self):
        x = len(self.extract['ThemeWithoutData'] * self.theme_without_data_item_height)
        if x > self.d5_height:
            return x
        else:
            return self.d5_height

    def compute_d6_left(self):
        content_min_size = 10 + 10 + 5 + 10 + 10  # spacing between paragraphs
        total_size = 39
        paragraph_space = 11
        for i in self.extract['GeneralInformation']:
            total_size += paragraph_space
            total_size += self.compute_length_of_wrapped_text(i['Text'],
                                                              78,
                                                              10)
        total_size += 5
        for i in self.extract['BaseData']:
            total_size += paragraph_space
            total_size += self.compute_length_of_wrapped_text(i['Text'],
                                                              78,
                                                              10)
        log.debug('d6 left total_size : {}'.format(total_size))
        if total_size > content_min_size:
            return total_size
        else:
            return content_min_size

    @staticmethod
    def compute_length_of_wrapped_text(text, nb_char, font_size):
        t = textwrap.wrap(text, nb_char)
        return len(t) * font_size

    def compute_d6_right(self):
        # variables taken from template exclusion_of_liability.jrxml
        space_above = 4
        space_title_content = 2
        content_min_size = 23
        total_size = 0
        for i in self.extract['ExclusionOfLiability']:
            total_size += space_above
            total_size += self.compute_length_of_wrapped_text(i['Title'][0]['Text'],
                                                              65,
                                                              14)
            total_size += space_title_content
            total_size += self.compute_length_of_wrapped_text(i['Content'][0]['Text'],
                                                              78,
                                                              10)
        log.debug('d6 ritght total_size : {}'.format(total_size))
        if total_size > content_min_size:
            return total_size
        else:
            return content_min_size

    def compute_d6(self):
        x = max(self.compute_d6_left(), self.compute_d6_right()) + self.d6_stuff_y_location
        if x > self.d6_height:
            return x
        else:
            return self.d6_height

    def compute_total_lenght(self):
        x = self.compute_d1() + \
            self.compute_d2() + \
            self.compute_d3() + \
            self.compute_d4() + \
            self.compute_d5() + \
            self.compute_d6()
        log.debug('TOC total page length : {}'.format(x))
        return x

    def getNbPages(self):
        return -(-self.total_length // self.disposable_height)  # ceil number of pages needed
