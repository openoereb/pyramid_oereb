# -*- coding: utf-8 -*-
import logging
import textwrap
from pyramid_oereb import Config

log = logging.getLogger(__name__)


class TocPages:
    def __init__(self, extract):
        print_config = Config.get('print', {})
        # 842: regular A4 page size in px
        # inlcude adjustable buffer, taking a earlier page break of MPF
        # into consideration for unknown reasons
        page_break_difference = 10
        if print_config.get('page_break_difference') is not None:
            page_break_difference = print_config.get('page_break_difference')
        self.total_height = 842 - page_break_difference
        self.header_height = self.compute_header()
        self.footer_height = self.compute_footer()
        self.disposable_height = (
            self.total_height - self.header_height - self.footer_height
        )  # A4 size - (footer + header)
        self.d1_height = 77  # toc.jrxml
        self.d2_height = 32  # toc.jrxml
        self.d3_height = 58  # toc.jrxml
        self.d4_height = 44  # toc.jrxml
        self.d5_height = 15  # toc.jrxml
        self.d6_height = 64  # toc.jrxml
        self.d6_left_height = 38  # toc.jrxml
        self.d6_right_height = 20  # toc.jrxml
        self.extract = extract
        self.display_qrcode = self.extract["Display_QRCode"]
        self.total_length = self.compute_total_length()

    def compute_header(self):
        total_size = 0
        page_top_margin = 28  # toc.jrxml
        header_height = 60  # toc.jrxml
        total_size += page_top_margin + header_height
        log.debug(f"header total_size: {total_size}")
        return total_size

    def compute_footer(self):
        total_size = 0
        page_bottom_margin = 20  # toc.jrxml
        footer_height = 10  # toc.jrxml
        total_size += page_bottom_margin + footer_height
        log.debug(f"footer total_size: {total_size}")
        return total_size

    def compute_d1(self):
        # The ConcernedTheme-Heading cannot be calculated at runtime. The used label
        # is defined in the mfp-templates which are not accessible here. Therefore
        # we assume one line without a line break.
        log.debug(f"d1 total_size: {self.d1_height}")
        return self.d1_height

    def compute_d2(self):
        total_size = 0
        blank_space_above = 2  # toc.jrxml
        page_label_height = 10  # toc.jrxml
        total_size += blank_space_above + page_label_height
        toc_item_height = 20  # toc.jrxml (20 in tocConcernedTheme.jrxml)
        unique_concerned_themes = []
        for concerned_theme in self.extract["ConcernedTheme"]:
            if concerned_theme not in unique_concerned_themes:
                unique_concerned_themes.append(concerned_theme)
        total_size += len(unique_concerned_themes) * toc_item_height
        if total_size > self.d2_height:
            log.debug(f"d2 total_size: {total_size}")
            return total_size
        else:
            log.debug(f"d2 total_size: {self.d2_height}")
            return self.d2_height

    def compute_d3(self):
        total_size = 0
        blank_space_above = 26  # toc.jrxml
        not_concerned_themes_title_height = 15  # toc.jrxml
        blank_space_between = 2  # toc.jrxml
        not_concerned_themes_item_height = 12  # toc.jrxml (12 in themelist.jrxml)
        total_size += (
            blank_space_above + not_concerned_themes_title_height + blank_space_between
        )
        total_size += (
            len(self.extract["NotConcernedTheme"]) * not_concerned_themes_item_height
        )
        if total_size > self.d3_height:
            log.debug(f"d3 total_size: {total_size}")
            return total_size
        else:
            log.debug(f"d3 total_size: {self.d3_height}")
            return self.d3_height

    def compute_d4(self):
        # The NoDataTheme-Heading cannot be calculated at runtime. The used label
        # is defined in the mfp-templates which are not accessible here. Therefore
        # we assume one line without a line break.
        log.debug(f"d4 total_size: {self.d4_height}")
        return self.d4_height

    def compute_d5(self):
        total_size = 0
        theme_without_data_item_height = 12  # themelist.jrxml
        total_size += (
            len(self.extract["ThemeWithoutData"])
        ) * theme_without_data_item_height
        if total_size > self.d5_height:
            log.debug(f"d5 total_size: {total_size}")
            return total_size
        else:
            log.debug(f"d5 total_size: {self.d5_height}")
            return self.d5_height

    def compute_d6_left(self):
        total_size = 0

        blank_space_above_d6 = 26
        total_size += blank_space_above_d6

        # General Information (1 title, multiple items)
        general_information_title_height = 8  # general_info_and_disclaimer.jrxml
        general_information_item_line_heigth = 8  # general_info_and_disclaimer.jrxml
        total_size += general_information_title_height
        for i in self.extract.get("GeneralInformation", []):
            total_size += self.compute_length_of_wrapped_text(
                i["Info"], 73, general_information_item_line_heigth
            )

        space_between_info_and_disclaimer = 6  # general_info_and_disclaimer.jrxml
        total_size += space_between_info_and_disclaimer

        # LandRegister-Disclaimer (1 title, 1 item)
        land_register_disclaimer_title_line_height = (
            8  # general_info_and_disclaimer.jrxml
        )
        land_register_disclaimer_item_line_height = (
            8  # general_info_and_disclaimer.jrxml
        )

        total_size += self.compute_length_of_wrapped_text(
            self.extract.get("DisclaimerLandRegister_Title", ""),
            65,
            land_register_disclaimer_title_line_height,
        )
        total_size += self.compute_length_of_wrapped_text(
            self.extract.get("DisclaimerLandRegister_Content", ""),
            73,
            land_register_disclaimer_item_line_height,
        )
        if total_size > self.d6_left_height:
            log.debug("d6 left total_size: {}".format(total_size))
            return total_size
        else:
            log.debug("d6 left total_size: {}".format(self.d6_left_height))
            return self.d6_left_height

    @staticmethod
    def compute_length_of_wrapped_text(text, nb_char, line_height):
        t = textwrap.wrap(text, nb_char)
        return len(t) * line_height

    def compute_d6_right(self):
        total_size = 0

        blank_space_above_d6 = 26
        total_size += blank_space_above_d6

        blank_space_below_disclaimers = 6  # disclaimer_and_qrcode.jrxml
        disclaimer_title_line_height = 8  # disclaimer_and_qrcode.jrxml
        disclaimer_item_line_height = 8  # disclaimer_and_qrcode.jrxml
        blank_space_above_qrcode = 13  # disclaimer_and_qrcode.jrxml
        qr_code_size = 56  # disclaimer_and_qrcode.jrxml

        # Disclaimers (multiple items)
        for i in self.extract.get("Disclaimer", []):
            total_size += self.compute_length_of_wrapped_text(
                i["Title"], 65, disclaimer_title_line_height
            )
            total_size += self.compute_length_of_wrapped_text(
                i["Content"], 73, disclaimer_item_line_height
            )
            total_size += blank_space_below_disclaimers

        # QR-Code (optional)
        if self.display_qrcode:
            total_size += blank_space_above_qrcode + qr_code_size

        if total_size > self.d6_right_height:
            log.debug("d6 right total_size: {}".format(total_size))
            return total_size
        else:
            log.debug("d6 right total_size: {}".format(self.d6_right_height))
            return self.d6_right_height

    def compute_d6(self):
        total_size = max(self.compute_d6_left(), self.compute_d6_right())
        if total_size > self.d6_height:
            log.debug(f"d6 total_size: {total_size}")
            return total_size
        else:
            log.debug(f"d6 total_size: {self.d6_height}")
            return self.d6_height

    def compute_total_length(self):
        x = (
            self.compute_d1()
            + self.compute_d2()
            + self.compute_d3()
            + self.compute_d4()
            + self.compute_d5()
            + self.compute_d6()
        )
        log.debug("TOC total page length : {}".format(x))
        log.debug(f"disposable height: {self.disposable_height}")
        return x

    def getNbPages(self):
        number_of_pages = -(
            -self.total_length // self.disposable_height
        )  # ceil number of pages needed
        log.debug(f"number of pages: {number_of_pages}")
        return number_of_pages
