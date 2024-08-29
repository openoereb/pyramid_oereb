# -*- coding: utf-8 -*-
import logging
import textwrap

log = logging.getLogger(__name__)


class TocPages():

    def __init__(self, extract, display_qrcode):
        self.disposable_height = 842 - 70  # A4 size - (footer + header); toc.jrxml
        self.d1_height = 77 # toc.jrxml
        self.d2_height = 29 # toc.jrxml
        self.d3_height = 61 # toc.jrxml
        self.d4_height = 44 # toc.jrxml
        self.d5_height = 93 # toc.jrxml
        self.d6_height = 38 # toc.jrxml
        self.d6_left_height = 38 # toc.jrxml
        self.d6_right_height = 20 # toc.jrxml
        self.extract = extract
        self.display_qrcode = display_qrcode
        self.total_length = self.compute_total_lenght()

    def compute_d1(self):
        # The ConcernedTheme-Heading cannot be calculated at runtime. The used label
        # is defined in the mfp-templates which are not accessible here. Therefore
        # we assume one line without a line break.
        return self.d1_height

    def compute_d2(self):
        total_size = 0
        blank_space_above = 2 # toc.jrxml
        page_label_height = 10 # toc.jrxml
        total_size += blank_space_above + page_label_height
        toc_item_height = 17 # toc.jrxml (20 in tocConcernedTheme.jrxml)
        total_size += len(self.extract['ConcernedTheme']) * toc_item_height
        if total_size > self.d2_height:
            return total_size
        else:
            return self.d2_height

    def compute_d3(self):
        total_size = 0
        blank_space_above = 26 # toc.jrxml
        not_concerned_themes_title_height = 15 # toc.jrxml
        blank_space_between = 5 # toc.jrxml
        not_concerned_themes_item_height = 15 # toc.jrxml (12 in themelist.jrxml)
        total_size += blank_space_above + not_concerned_themes_title_height + blank_space_between
        total_size += len(self.extract['NotConcernedTheme']) * not_concerned_themes_item_height
        
        if total_size > self.d3_height:
            return total_size
        else:
            return self.d3_height

    def compute_d4(self):
        # The NoDataTheme-Heading cannot be calculated at runtime. The used label
        # is defined in the mfp-templates which are not accessible here. Therefore
        # we assume one line without a line break.
        return self.d4_height

    def compute_d5(self):
        total_size = 0
        theme_without_data_item_height = 15 # toc.jrxml (12 in themelist.jrxml)
        total_size += len(self.extract['ThemeWithoutData'] * theme_without_data_item_height)
        if total_size > self.d5_height:
            return total_size
        else:
            return self.d5_height

    def compute_d6_left(self):
        total_size = 0

        # General Information (1 title, multiple items)
        general_information_title_height = 8 # general_info_and_disclaimer.jrxml
        general_information_item_line_heigth = 8 # general_info_and_disclaimer.jrxml
        total_size += general_information_title_height
        for i in self.extract.get('GeneralInformation', []):
            total_size += self.compute_length_of_wrapped_text(i[0]['Text'],
                                                              78,
                                                              general_information_item_line_heigth)
        # LandRegister-Disclaimer (1 title, 1 item)
        land_register_disclaimer_title_line_height = 8 # general_info_and_disclaimer.jrxml
        land_register_disclaimer_item_line_height = 8 # general_info_and_disclaimer.jrxml
        for i in self.extract.get('DisclaimerLandRegister', []):
            total_size += self.compute_length_of_wrapped_text(i['Title'][0]['Text'],
                                                              65,
                                                              land_register_disclaimer_title_line_height)
            total_size += self.compute_length_of_wrapped_text(i['Content'][0]['Text'],
                                                              78,
                                                              land_register_disclaimer_item_line_height)
        log.debug('d6 left total_size : {}'.format(total_size))
        if total_size > self.d6_left_height:
            return total_size
        else:
            return self.d6_left_height

    @staticmethod
    def compute_length_of_wrapped_text(text, nb_char, line_height):
        t = textwrap.wrap(text, nb_char)
        return len(t) * line_height

    def compute_d6_right(self):
        total_size = 0

        blank_space_below_disclaimers = 6 # disclaimer_and_qrcode.jrxml
        disclaimer_title_line_height = 8 # disclaimer_and_qrcode.jrxml
        disclaimer_item_line_height = 8 # disclaimer_and_qrcode.jrxml
        blank_space_above_qrcode = 13 # disclaimer_and_qrcode.jrxml
        qr_code_size = 56 # disclaimer_and_qrcode.jrxml

        # Disclaimers (multiple items)
        for i in self.extract.get('Disclaimer', []):
            total_size += self.compute_length_of_wrapped_text(i['Title'][0]['Text'],
                                                              65,
                                                              disclaimer_title_line_height)
            total_size += self.compute_length_of_wrapped_text(i['Content'][0]['Text'],
                                                              78,
                                                              disclaimer_item_line_height)
        total_size += blank_space_below_disclaimers

        # QR-Code (optional)
        if self.display_qrcode:
            total_size += blank_space_above_qrcode + qr_code_size
        
        log.debug('d6 right total_size : {}'.format(total_size))
        if total_size > self.d6_right_height:
            return total_size
        else:
            return self.d6_right_height

    def compute_d6(self):
        total_size = max(self.compute_d6_left(), self.compute_d6_right())
        if total_size > self.d6_height:
            return total_size
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
