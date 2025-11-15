from sqlalchemy import create_engine, event, select, func
from sqlalchemy.orm import sessionmaker
from app.models import Base, Game, Player, Visit
from app.config import DB_URL, SQL_ECHO

import os
from sqlalchemy import create_engine

DB_PATH = os.getenv("DB_PATH", "/data/players.db")
DB_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DB_URL, echo=False, connect_args={
                       "check_same_thread": False})


# Включаем внешние ключи в SQLite (для ondelete='CASCADE')


@event.listens_for(engine, "connect")
def _fk_on(dbapi_conn, _):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA foreign_keys=ON")
    cur.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False,
                            expire_on_commit=False, future=True)


def init_db():
    """Создаёт таблицы, если их ещё нет."""
    Base.metadata.create_all(engine)

# ---- простые утилиты ----


def get_games():
    with SessionLocal() as s:
        return s.scalars(select(Game)).all()


def get_game_by_id(game_id: int) -> Game | None:
    with SessionLocal() as s:
        return s.get(Game, game_id)


def add_game(name: str):
    with SessionLocal() as s:
        s.add(Game(name=name))
        s.commit()

# ---- сохранение визитов (ядро) ----


def _resolve_game(s, game_ref) -> Game | None:
    if isinstance(game_ref, Game):
        return game_ref
    if isinstance(game_ref, int):
        return s.get(Game, game_ref)
    if isinstance(game_ref, str):
        return s.scalar(select(Game).where(Game.name == game_ref))
    return None


def _resolve_player(s, username: str) -> Player:
    p = s.scalar(select(Player).where(Player.name == username))
    if p is None:
        p = Player(name=username)
        s.add(p)
        # flush не обязателен, т.к. Visit(player=p, ...) свяжет при commit,
        # но если нужно p.id немедленно — вызови s.flush()
    return p


def create_visits(data: dict):
    """
    data = {
      "game": Game | int(game_id) | str(game_name),
      "date": datetime.date,
      "player_list": list[str]
    }
    """
    s = SessionLocal()
    try:
        game = _resolve_game(s, data.get("game") or data.get("game_id"))
        if not game:
            raise ValueError("Game not found")

        when = data["date"]
        players = data["player_list"]

        for uname in players:
            p = _resolve_player(s, uname)
            s.add(Visit(player=p, game=game, date=when))

        s.commit()
    except Exception:
        s.rollback()
        raise
    finally:
        s.close()


def get_visits_stats(from_date, to_date):
    """
    Возвращает список (player_name, visits_count) за интервал [from_date, to_date]
    """
    with SessionLocal() as s:
        stmt = (
            select(
                Player.name,
                func.count(Visit.id)
            )
            .join(Visit, Visit.player_id == Player.id)
            .where(
                Visit.date >= from_date,
                Visit.date <= to_date,
            )
            .group_by(Player.id, Player.name)
            .order_by(func.count(Visit.id).desc())
        )
        rows = s.execute(stmt).all()
        # rows: list[tuple[str, int]]
        return rows
