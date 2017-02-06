import sqlalchemy.ext.declarative
import sqlalchemy as sa

Base = sqlalchemy.ext.declarative.declarative_base()


class Example(Base):
    __tablename__ = "example"
    __table_args__ = {"schema": 'public'}
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    value = sa.Column(sa.Text, nullable=False)
