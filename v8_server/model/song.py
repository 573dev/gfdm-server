from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List

from flask_sqlalchemy.model import DefaultMeta
from sqlalchemy import Column, ForeignKey, PrimaryKeyConstraint, event, func, text
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime, Integer, String

from v8_server import db


BaseModel: DefaultMeta = db.Model
logger = logging.getLogger(__name__)


class Song(BaseModel):
    """
    Table representing the song data
    """

    __tablename__ = "songs"
    musicid = Column(Integer, nullable=False, primary_key=True)
    bpm = Column(Integer, nullable=False)
    title_ascii = Column(String(16), nullable=False)
    hitcharts = relationship("HitChart", back_populates="song")

    def __repr__(self) -> str:
        return (
            f"Song<musicid: {self.musicid}, bpm: {self.bpm}, "
            f'title_ascii: "{self.title_ascii}">'
        )


class HitChart(BaseModel):
    """
    Table representing the song hit chart
    """

    __tablename__ = "hitchart"
    __table_args__ = (PrimaryKeyConstraint("musicid", "playdate"),)
    musicid = Column(Integer, ForeignKey("songs.musicid"), nullable=False)
    playdate = Column(DateTime, nullable=False)
    song = relationship("Song", back_populates="hitcharts")

    def __repr__(self) -> str:
        return f"HitChart<musicid: {self.musicid}, playdate: {self.playdate}>"

    @classmethod
    def get_ranking(cls, count) -> List[int]:
        items = (
            db.session.query(
                HitChart.musicid, func.count(HitChart.musicid).label("count")
            )
            .group_by(HitChart.musicid)
            .order_by(text("count DESC"))
            .order_by(HitChart.musicid.desc())
            .limit(count)
            .all()
        )

        results = []
        for item in items:
            results.append(item[0])

        return results


def insert_initial_song_data(target, connection, **kwargs) -> None:
    # Make sure both Song and HitChart have been created
    try:
        db.session.execute("SELECT * FROM songs")
        db.session.execute("SELECT * FROM hitchart")
    except Exception:
        return

    # Load up the mdb.json file
    data_path = Path(__file__).parent / "data" / "mdb.json"
    with data_path.open() as f:
        json_data = json.loads(f.read())

    for key, song in json_data["musicdb"]["songs"].items():
        song_obj = Song(musicid=key, bpm=song["bpm"], title_ascii=song["title_ascii"])
        db.session.add(song_obj)

    db.session.commit()

    # Insert initial hitchart data, just add one entry for every song with the current
    # timestamp
    now = datetime.now()
    for key, song in json_data["musicdb"]["songs"].items():
        hc = HitChart(musicid=key, playdate=now)
        db.session.add(hc)

    db.session.commit()


event.listen(Song.__table__, "after_create", insert_initial_song_data)
event.listen(HitChart.__table__, "after_create", insert_initial_song_data)
