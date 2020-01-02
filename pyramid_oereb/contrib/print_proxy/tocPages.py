# -*- coding: utf-8 -*-
import logging


from PIL import ImageFont

import textwrap
import os

log = logging.getLogger(__name__)

class TocPages():
    """
    This class is inspired by this example: 
    https://gist.github.com/turicas/1455973
    """
    FONT_CADASTRA_NORMAL =  os.path.dirname(os.path.abspath(__file__)) + '/fonts/Cadastra/Cadastra.ttf'
    FONT_CADASTRA_BOLD = os.path.dirname(os.path.abspath(__file__)) + '/fonts/Cadastra/CadastraBd.ttf'
    
    def __init__(self,extract):
        # variables taken from template toc.jrxml
        self.disposable_height = 842 - 70
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
        self.toc_title_height=15 + 62 + 12 # height + location + item starting position
        self.toc_item_height=20
        self.not_concerned_themes_title_height=15 + 26 # height + location
        self.not_concerned_themes_item_height=12
        self.theme_without_data_title_height=12
        self.theme_without_data_item_height=12
        self.extract = extract
        self.total_length = self.compute_total_lenght()
    
    def get_text_size(self, font_filename, font_size, text):
        font = ImageFont.truetype(font_filename, font_size)
        return font.getsize_multiline(text)

    def write_text_box(self, text, box_width, font_size, font_filename,
                       place='left'):
        lines = []
        line = []
        words = text.split()
        for word in words:
            new_line = ' '.join(line + [word])
            size = self.get_text_size(font_filename, font_size, new_line)
            if size[0] <= box_width:
                line.append(word)
            else:
                lines.append(line)
                line = [word]
        if line:
            lines.append(line)
        log.warning('lines : {}'.format(lines))
        lines = [' '.join(line) for line in lines if line]
        lines = '\n'.join(lines)
        (_, height) = self.get_text_size(font_filename, font_size, lines)
        return height
    
    def compute_d1(self):
        return self.d1_height
    
    def compute_d2(self):
        x = len(self.extract['ConcernedTheme'] * self.toc_item_height)
        if x > self.d2_height:
            return x
        else:
            return self.d2_height

    def compute_d3(self):
        x = self.not_concerned_themes_title_height + len(self.extract['NotConcernedTheme'] * self.not_concerned_themes_item_height)
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
        # FIXME: compute this one
        return 10

    @staticmethod
    def compute_length_of_wrapped_text(text, nb_char, font_size):
        return len(textwrap.wrap(text, nb_char)) * font_size

    def compute_d6_right(self):
        # variables taken from template exclusion_of_liability.jrxml
        space_above = 4
        space_title_content = 2
        content_min_size = 23
        title_font_size = 8
        content_font_size = 6
        total_size = 0
        for i in self.extract['ExclusionOfLiability']:
            total_size += space_above
            total_size += self.write_text_box(i['Title'][0]['Text'],
                                        self.d6_right_width,
                                        title_font_size,
                                        self.FONT_CADASTRA_BOLD)
            total_size += space_title_content
            total_size += self.write_text_box(i['Content'][0]['Text'],
                                        self.d6_right_width,
                                        content_font_size,
                                        self.FONT_CADASTRA_NORMAL)
        log.warning('total_size : {}'.format(total_size))
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
        log.warning('total page length : {}'.format(x))
        return x
    
    def getNbPages(self):
        return -(-self.total_length // self.disposable_height) # ceil number of pages needed  
