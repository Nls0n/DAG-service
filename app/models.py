from .database import Base
from sqlalchemy import Column, Integer, VARCHAR, TIMESTAMP, text, ForeignKey
from sqlalchemy.orm import relationship


class Graphs(Base):
    __tablename__ = "graphs"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    nodes = relationship("Nodes", back_populates="graph")
    edges = relationship("Edges", back_populates="graph")


class Nodes(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    graph_id = Column(Integer, ForeignKey("graphs.id"))
    name = Column(VARCHAR(255), nullable=True)

    graph = relationship("Graphs", back_populates="nodes")


class Edges(Base):
    __tablename__ = "edges"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    graph_id = Column(Integer, ForeignKey("graphs.id"))
    source = Column(VARCHAR(255))
    target = Column(VARCHAR(255))

    graph = relationship("Graphs", back_populates="edges")

