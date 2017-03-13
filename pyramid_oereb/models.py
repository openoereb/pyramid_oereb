import sqlalchemy.ext.declarative
import sqlalchemy as sa

from geoalchemy2.types import Geometry

Base = sqlalchemy.ext.declarative.declarative_base()

schema ='plr'
srid =2056

class Example(Base):
    __tablename__ = "example"
    __table_args__ = {"schema": 'public'}
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    value = sa.Column(sa.Text, nullable=False)

class Authority(Base):
    __tablename__ = 'authority'
    __table_args__ = {'schema': schema}
    id = Column(sa.String, primary_key=True)
    name = Column(sa.String)
    url = Column(sa.String)

class Topic(Base):
    __tablename__ = 'topic'
    __table_args__ = {'schema': schema}
    id = Column(sa.Integer, primary_key=True)
    name = Column(sa.String)

#railway_construction_limits
class RailwayConstructionLimits(Base):
    __tablename__ = 'plr_97'
    __plr_id__ = 97
    __table_args__ = {'schema': schema}
    id = Column(sa.Integer, primary_key=True)
    tenor = Column(sa.String)
    topic_id = Column(sa.Integer, ForeignKey(Topic.id), nullable=False)
    # subtopic = Column(sa.String)
    # other_topic = Column(sa.String)
    code = Column(sa.String)
    legal_state  = Column(sa.String)
    publication_date = Column(sa.Date)
    authority_id = Column(sa.Integer, ForeignKey(Authority.id), nullable=False)
    geom = Column(Geometry('MULTILINESTRING', dimension=2, srid=srid))