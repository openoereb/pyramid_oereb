# -*- coding: utf-8 -*-

def from_multilingual_text_to_dict(de=None, fr=None, it=None, rm=None, en=None):
    if de is None and fr is None and it is None and rm is None and en is None:
        return None
    else:
        dict_var = dict()
        if de is not None:
            dict_var['de'] = de
        if fr is not None:
            dict_var['fr'] = fr
        if it is not None:
            dict_var['it'] = it
        if rm is not None:
            dict_var['rm'] = rm
        if en is not None:
            dict_var['en'] = en
        return dict_var


def from_multilingual_uri_to_dict(obj):
    """
    obj (pyramid_oereb.contrib.models.models.MultilingualUri)
    """
    for ml_uris in obj:
        var_dict = dict()
        for row in ml_uris.localised_uri:
            var_dict[row.language] = row.text
        return var_dict


def from_multilingual_blob_to_dict(obj):
    """
    obj (pyramid_oereb.contrib.models.models.MultilingualBlob)
    """
    for ml_blobs in obj:
        var_dict = dict()
        for row in ml_blobs.localised_blob:
            var_dict[row.language] = row.blob
        return var_dict
