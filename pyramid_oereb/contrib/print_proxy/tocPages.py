# -*- coding: utf-8 -*-
import logging


from PIL import ImageFont

import textwrap
import os

log = logging.getLogger(__name__)

class TocPages():
    """
    This class is extremely highly inspired by this excellent example: 
    https://gist.github.com/turicas/1455973
    
    """
    FONT_CADASTRA_NORMAL =  os.path.dirname(os.path.abspath(__file__)) + '/fonts/Cadastra/Cadastra.ttf'
    FONT_CADASTRA_BOLD = os.path.dirname(os.path.abspath(__file__)) + '/fonts/Cadastra/CadastraBd.ttf'
    def __init__(self,extract):
        self.disposable_height = 842 - 70
        self.d1_height = 77
        self.d2_height = 29
        self.d3_height = 61
        self.d4_height = 44
        self.d5_height = 15
        self.d6_height = 90
        self.d6_right_height = 23
        self.d6_right_width = 233
        self.d6_left_height = 0  # FIXME: compute this
        self.title_size = 62
        self.toc_title_height=15
        self.toc_item_height=20
        self.not_concerned_themes_title_height=12
        self.not_concerned_themes_item_height=12
        self.theme_without_data_title_height=12
        self.theme_without_data_item_height=12
        self.extract = extract
        self.total_length = self.compute_total_lenght()

    def get_font_size(self, text, font, max_width=None, max_height=None):
        if max_width is None and max_height is None:
            raise ValueError('You need to pass max_width or max_height')
        font_size = 1
        text_size = self.get_text_size(font, font_size, text)
        if (max_width is not None and text_size[0] > max_width) or \
           (max_height is not None and text_size[1] > max_height):
            raise ValueError("Text can't be filled in only (%dpx, %dpx)" % \
                    text_size)
        while True:
            if (max_width is not None and text_size[0] >= max_width) or \
               (max_height is not None and text_size[1] >= max_height):
                return font_size - 1
            font_size += 1
            text_size = self.get_text_size(font, font_size, text)

    def write_text(self, text, font_filename, font_size=11,
                   max_width=None, max_height=None):
        if font_size == 'fill' and \
           (max_width is not None or max_height is not None):
            font_size = self.get_font_size(text, font_filename, max_width,
                                           max_height)
        log.warning('text : {}'.format(text))
        text_size = self.get_text_size(font_filename, font_size, text)
        return text_size
    
    def get_text_size(self, font_filename, font_size, text):
        #log.warning('text : {}'.format(text))
        font = ImageFont.FreeTypeFont(font_filename, font_size)
        return font.getsize(text)

    def write_text_box(self, text, box_width, font_size, font_filename,
                       place='left'):
        lines = []
        line = []
        words = text.split()
        for word in words:
            new_line = ' '.join(line + [word])
            size = self.get_text_size(font_filename, font_size, new_line)
            text_height = size[1]
            if size[0] <= box_width:
                line.append(word)
            else:
                lines.append(line)
                line = [word]
        if line:
            lines.append(line)
        lines = [' '.join(line) for line in lines if line]
        height = 0
        for index, line in enumerate(lines):
            height += text_height
            if place == 'left':
                self.write_text(line, font_filename, font_size)
            # TODO: if needed we can add here other implementations for text
            #       adjustment
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
        return 10
    @staticmethod
    def compute_length_of_wrapped_text(text, nb_char, font_size):
        return len(textwrap.wrap(text, nb_char)) * font_size
    def compute_d6_right(self):
        space_above = 4
        space_title_content = 2
        content_min_size = 23
        title_font_size = 8
        content_font_size = 6
        content_font_max_char = 74 # FIXME: should be computed based on real font
        total_size = 0
        for i in self.extract['ExclusionOfLiability']:
            total_size += space_above
            h = self.write_text_box(i['Title'][0]['Text'],
                                        self.d6_right_width,
                                        title_font_size,
                                        self.FONT_CADASTRA_BOLD)
            total_size += h
            total_size += space_title_content
            h = self.write_text_box(i['Content'][0]['Text'],
                                        self.d6_right_width,
                                        content_font_size,
                                        self.FONT_CADASTRA_NORMAL)
            total_size += h
            total_size +=  self.compute_length_of_wrapped_text(i['Content'][0]['Text'], content_font_max_char, content_font_size)
        if total_size > content_min_size:
            return total_size
        else:
            return content_min_size
            
        
    def compute_d6(self):
        x = max(self.compute_d6_left(),self.compute_d6_right())
        if x > self.d6_height:
            return x
        else:
            return self.d6_height
    def compute_total_lenght(self):
        return self.compute_d1() + \
                self.compute_d2() + \
                self.compute_d3() + \
                self.compute_d4() + \
                self.compute_d5() + \
                self.compute_d6()
    
    
    def getNbPages(self):
        return -(-self.total_length // self.disposable_height) # ceil number of pages needed  
