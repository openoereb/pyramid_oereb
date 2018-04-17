# -*- coding: utf-8 -*-
import os
from pyramid.path import AssetResolver
from mako.template import Template
from pyramid_oereb.standard import convert_camel_case_to_snake_case, convert_camel_case_to_text_form


def _create_oereblex_models_py_(code, geometry_type, absolute_path, schema=None, primary_key_is_string=False):
    """
    The simplest way to get a python file containing a database definition in sqlalchemy orm way. It will
    contain all necessary definitions to produce an extract as the specification defines for the new topic.
    It will create models for a configuration where documents are read out of OEREBlex.

    Args:
        code (str): The unique Code for the new model (see oereb specification for more details)
        geometry_type (str): A valid geometry type.
        absolute_path (str): The absolute Path where the genderated python file will be placed. It
            must bewriteable by the user running this command.
        schema (str): The schema name. If not specified, "name" will be used.
        primary_key_is_string (bool): The type of the primary key. You can use this to switch between STRING
            type or INTEGER type. Standard is to INTEGER => False
    """
    template = Template(
        filename=AssetResolver('pyramid_oereb').resolve(
            'contrib/templates/plr_oereb.py.mako'
        ).abspath()
    )
    name = convert_camel_case_to_snake_case(code)
    content = template.render(**{
        'topic': convert_camel_case_to_text_form(code),
        'schema_name': schema or name,
        'geometry_type': geometry_type,
        'primary_key_is_string': primary_key_is_string
    })
    models_path = '{path}/{name}.py'.format(
        path=absolute_path,
        name=name
    )
    models_path = os.path.abspath(models_path)
    if os.path.exists(models_path):
        os.remove(models_path)
    models_file = open(models_path, 'w+')
    models_file.write(content)
    models_file.close()
