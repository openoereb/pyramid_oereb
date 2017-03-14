# -*- coding: utf-8 -*-

import sqlalchemy.ext.declarative
import sqlalchemy as sa

from geoalchemy2.types import Geometry
from sqlalchemy.orm import relationship

NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = sa.MetaData(naming_convention=NAMING_CONVENTION)
Base = sqlalchemy.ext.declarative.declarative_base()
NotAlembicBase = sqlalchemy.ext.declarative.declarative_base()

schema = 'plr'
srid_lv03 = 21781
srid_lv95 = 2056


class GeometryPointLv03(NotAlembicBase):
    id = sa.Column(sa.Integer, primary_key=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)
    metadata = sa.Column(sa.String, nullable=True) # TODO: Check translation
    geom = sa.Column(Geometry('POINT', srid=srid_lv03))


class GeometryPointLv95(GeometryPointLv03):
    geom = sa.Column(Geometry('POINT', srid=srid_lv95))


class GeometryLineLv03(GeometryPointLv03):
    geom = sa.Column(Geometry('LINESTRING', srid=srid_lv03))


class GeometryLineLv95(GeometryPointLv03):
    geom = sa.Column(Geometry('LINESTRING', srid=srid_lv95))


class GeometryAreaLv03(GeometryPointLv03):
    geom = sa.Column(Geometry('POLYGON', srid=srid_lv03))


class GeometryAreaLv95(GeometryPointLv03):
    geom = sa.Column(Geometry('POLYGON', srid=srid_lv95))


class PublicLawRestriction(NotAlembicBase):
    id = sa.Column(sa.Integer, primary_key=True)
    content = sa.Column(sa.String, nullable=False)
    topic = sa.Column(sa.String, nullable=False)
    subtopic = sa.Column(sa.String, nullable=True)
    additional_topic = sa.Column(sa.String, nullable=True)
    type_code = sa.Column(sa.String(40), nullable=True)
    type_code_list = sa.Column(sa.String, nullable=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)


class ViewService(NotAlembicBase):
    id = sa.Column(sa.Integer, primary_key=True)
    link_wms = sa.Column(sa.String, nullable=False)
    legend_web = sa.Column(sa.String, nullable=True)


class LegendEntry(NotAlembicBase):
    id = sa.Column(sa.Integer, primary_key=True)
    symbol = sa.Column(sa.Binary, nullable=False)
    legend_text = sa.Column(sa.String, nullable=False)
    type_code = sa.Column(sa.String(40), nullable=False)
    type_code_list = sa.Column(sa.String, nullable=False)
    topic = sa.Column(sa.String, nullable=False)
    subtopic = sa.Column(sa.String, nullable=True)
    additional_topic = sa.Column(sa.String, nullable=True)


class Authority(NotAlembicBase):
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)
    authority_web = sa.Column(sa.String, nullable=True)
    uid = sa.Column(sa.String(12), nullable=True)


class ReferenceDefinition(NotAlembicBase): # TODO: Check translation
    id = sa.Column(sa.Integer, primary_key=True)
    topic = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)


class DocumentBase(NotAlembicBase):
    id = sa.Column(sa.Integer, primary_key=True)
    text_web = sa.Column(sa.String, nullable=True)
    legal_state = sa.Column(sa.String, nullable=False)
    published_from = sa.Column(sa.Date, nullable=False)


class Document(DocumentBase):
    title = sa.Column(sa.String, nullable=False)
    official_title = sa.Column(sa.String, nullable=True)
    abbreviation = sa.Column(sa.String, nullable=True)
    official_number = sa.Column(sa.String, nullable=True)
    canton = sa.Column(sa.String(2), nullable=True)
    municipality = sa.Column(sa.Integer, nullable=True)
    document = sa.Column(sa.Binary, nullable=True)


class Article(DocumentBase):
    number = sa.Column(sa.String, nullable=False)
    text = sa.Column(sa.String, nullable=True)


class LegalProvision(Document):
    pass