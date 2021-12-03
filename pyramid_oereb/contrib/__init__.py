# -*- coding: utf-8 -*-

import logging

log = logging.getLogger(__name__)


def eliminate_duplicated_document_records(main_document_records, plr_document_records):
    """ Filtering of document records that are associated to a plr.

    Document records associated to a plr are eliminated if a record associated to a theme exists
    for the same document. Document records associated to a theme have priority.
    Records are considered to handle the same document if:
    - indices are equal, and
    - document_type codes are equal, and
    - official_numbers correspond

    Correct data is expected.
    """

    # basic rules (one or the other source does not provide any document records)
    if main_document_records is None and len(plr_document_records) > 0:
        return plr_document_records
    if main_document_records is not None and len(plr_document_records) == 0:
        return main_document_records

    # list which indicates duplicated documents
    plr_document_is_duplicated_list = [False] * len(plr_document_records)

    # document per document comparison
    for doc1 in main_document_records:
        for index2, doc2 in enumerate(plr_document_records):
            if plr_document_is_duplicated_list[index2] is False:
                # comparison of indices
                if doc1.index != doc2.index:
                    continue
                # comparison of document_type
                if doc1.document_type.code != doc2.document_type.code:
                    continue
                # comparison of number
                # - Note: official number is NOT mandatory
                # - possibility of not corresponding languages
                docs_have_same_number = False
                if doc1.official_number is not None and doc2.official_number is not None:
                    for key, value in doc1.official_number.items():
                        if doc2.official_number.get(key):
                            if doc2.official_number.get(key) == value:
                                docs_have_same_number = True
                                break
                    if docs_have_same_number:
                        plr_document_is_duplicated_list[index2] = True

    unique_document_indexes = [i for i, val in enumerate(plr_document_is_duplicated_list) if val is False]
    unique_document_records = [plr_document_records[i] for i in unique_document_indexes]

    # logging message if document record was removed
    if len(unique_document_records) != len(plr_document_records):
        dupl_doc_indexes = [i for i, val in enumerate(plr_document_is_duplicated_list) if val is True]
        for i in dupl_doc_indexes:
            log.info(
                '''PLR document record removed from extract as it is already provided by the main doc records
                (title: {title}, number: {number}, index: {index})'''.format(
                    title=plr_document_records[i].title,
                    number=plr_document_records[i].official_number,
                    index=plr_document_records[i].index
                )
            )

    return main_document_records + unique_document_records
