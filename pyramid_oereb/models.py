import sqlalchemy.ext.declarative
import sqlalchemy as sa

from geoalchemy2.types import Geometry

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
    __tablename__ = 'geometry_point_lv03'
    id = sa.Column(sa.Integer, primary_key=True)
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


class Topic(Base):
    __tablename__ = 'topic'
    __table_args__ = {'schema': 'common'}
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, nullable=False)


class PublicLawRestriction(Base):
    __tablename__ = 'public_law_restriction'
    __table_args__ = {'schema': 'plr_97'}
    id = sa.Column(sa.Integer, primary_key=True)
    tenor = sa.Column(sa.String, nullable=False)
    topic_id = sa.Column(sa.Integer, sa.ForeignKey(Topic.id))

