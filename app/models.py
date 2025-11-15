from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Date, UniqueConstraint, Index

Base = declarative_base()


class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    visits = relationship("Visit", back_populates="game")


class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    visits = relationship("Visit", back_populates="player")


class Visit(Base):
    __tablename__ = "visits"
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey(
        "players.id", ondelete="CASCADE"), nullable=False)
    game_id = Column(Integer, ForeignKey(
        "games.id",   ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)

    player = relationship("Player", back_populates="visits")
    game = relationship("Game",   back_populates="visits")

    __table_args__ = (
        UniqueConstraint("player_id", "game_id", "date",
                         name="uq_visit_player_game_date"),
        Index("ix_visit_game_date", "game_id", "date"),
    )
