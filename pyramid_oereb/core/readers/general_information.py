# -*- coding: utf-8 -*-
from pyramid.path import DottedNameResolver


class GeneralInformationReader(object):
    """
    The central reader for the OEREB general information. It is directly bound to a so called source
    which is defined by a pythonic dotted string to the class definition of this source.
    An instance of the passed source will be created on instantiation of this reader class by passing through
    the parameter kwargs.
    """

    def __init__(self, dotted_source_class_path, **params):
        """
        Args:
            dotted_source_class_path
                (str or pyramid_oereb.core.sources.general_information.GeneralInformationBaseSource): The path
                to the class which represents the source used by this reader. This class must
                exist and it must implement basic source behaviour of the
                :ref:`api-pyramid_oereb-core-sources-general_information-generalinformationbasesource`.
            (kwargs): kwargs, which are necessary as configuration parameter for the above by
                dotted name defined class.
        """
        source_class = DottedNameResolver().maybe_resolve(dotted_source_class_path)
        self._source_ = source_class(**params)

    def read(self):
        """
        The central read accessor method to get all desired records from configured source.

        Note:
            If you subclass this class your implementation needs to offer this method in the same
            signature. Means the parameters must be the same and the return must be a list of
            :ref:`api-pyramid_oereb-core-records-general_information-generalinformationrecord`.
            Otherwise the API like way the server works would be broken.

        Returns:
            list of pyramid_oereb.core.records.general_information.GeneralInformationRecord:
                The list of found records. Since these are not filtered by any criteria the list simply
                contains all records delivered by the source.
        """
        self._source_.read()
        return self._source_.records
