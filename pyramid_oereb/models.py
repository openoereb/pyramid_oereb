import sqlalchemy.ext.declarative
import sqlalchemy as sa

from geoalchemy2.types import Geometry

Base = sqlalchemy.ext.declarative.declarative_base()

schema = 'plr'
srid = 2056


class Example(Base):
    __tablename__ = "example"
    __table_args__ = {"schema": 'public'}
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    value = sa.Column(sa.Text, nullable=False)


class Authority(Base):
    __tablename__ = 'authority'
    __table_args__ = {'schema': schema}
    id = sa.Column(sa.String, primary_key=True)
    name = sa.Column(sa.String)
    url = sa.Column(sa.String)


class Topic(Base):
    __tablename__ = 'topic'
    __table_args__ = {'schema': schema}
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)


# railway_construction_limits
class RailwayConstructionLimits(Base):
    __tablename__ = 'plr_97'
    __plr_id__ = 97
    __table_args__ = {'schema': schema}
    id = sa.Column(sa.Integer, primary_key=True)
    tenor = sa.Column(sa.String)
    topic_id = sa.Column(sa.Integer, sa.ForeignKey(Topic.id), nullable=False)
    # subtopic = sa.Column(sa.String)
    # other_topic = sa.Column(sa.String)
    code = sa.Column(sa.String)
    legal_state = sa.Column(sa.String)
    publication_date = sa.Column(sa.Date)
    authority_id = sa.Column(sa.Integer, sa.ForeignKey(Authority.id), nullable=False)
    geom = sa.Column(Geometry('MULTILINESTRING', dimension=2, srid=srid))
