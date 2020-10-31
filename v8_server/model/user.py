from __future__ import annotations

import random
from typing import Optional

from flask_sqlalchemy.model import DefaultMeta
from sqlalchemy import JSON, Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from v8_server import db


BaseModel: DefaultMeta = db.Model

DEFAULT_GAME = "GFDM"
DEFAULT_VERSION = "v8"


class User(BaseModel):
    """
    Table representing a user. Each user has a Unique ID and a pin which is used
    with all cards associated with the user's account.
    """

    __tablename__ = "users"

    userid = Column(Integer, nullable=False, primary_key=True)
    pin = Column(String(4), nullable=False)
    cards = relationship("Card", back_populates="user")
    extids = relationship("ExtID", back_populates="user")
    refids = relationship("RefID", back_populates="user")

    def __repr__(self) -> str:
        return f'User<userid: {self.userid}, pin: "{self.pin}">'

    @classmethod
    def from_cardid(cls, cardid: str) -> Optional[User]:
        card = db.session.query(Card).filter(Card.cardid == cardid).one_or_none()
        return card.user if card is not None else None


class Card(BaseModel):
    """
    Table representing a card associated with a user. Users may have zero or more cards
    associated with them. When a new card is used in a game, a new user will be created
    to asociate with a card.
    """

    __tablename__ = "cards"

    cardid = Column(String(16), nullable=False, primary_key=True)
    userid = Column(Integer, ForeignKey("users.userid"), nullable=False)
    user = relationship("User", back_populates="cards")

    def __repr__(self) -> str:
        return f'Card<cardid: "{self.cardid}", userid: {self.userid}>'


class ExtID(BaseModel):
    """
    Table representing and extid for a user across a game series. Each game series on
    the network gets its own extid (8 digit number) for each user.
    """

    __tablename__ = "extids"
    __table_args_ = (UniqueConstraint("game", "userid", name="game_userid"),)
    extid = Column(Integer, nullable=False, primary_key=True)
    game = Column(String(32), nullable=False)
    userid = Column(Integer, ForeignKey("users.userid"), nullable=False)
    user = relationship("User", back_populates="extids")

    def __repr__(self) -> str:
        return f'ExtID<extid: {self.extid}, game: "{self.game}", userid: {self.userid}>'

    @classmethod
    def create_with_userid(cls, userid: int) -> Optional[ExtID]:
        # First check if this user has an ExtID for GFDM
        extid = (
            db.session.query(ExtID)
            .filter(ExtID.userid == userid, ExtID.game == DEFAULT_GAME)
            .one_or_none()
        )

        if extid is None:
            # Create a new ExtID that is unique
            while True:
                extid_val = random.randint(0, 89999999) + 10000000
                count = db.session.query(ExtID).filter(ExtID.extid == extid_val).count()
                if count == 0:
                    break

            # Use this ExtID
            extid = ExtID(extid=extid_val, game=DEFAULT_GAME, userid=userid)
            db.session.add(extid)
            db.session.commit()

        return extid


class RefID(BaseModel):
    """
    Table representing a refid for a user. Each unique game on the network will need
    a refid for each user/game/version they have a profile for. If a user does not have
    a profile for a particular game, a new and unique refid will be generated for the
    user.

    Note that a user might have an extid/refid for a game without a profile, but a user
    can not have a profile without an extid/refid
    """

    __tablename__ = "refids"
    __table_args__ = (
        UniqueConstraint("game", "version", "userid", name="game_version_userid"),
    )
    refid = Column(String(16), nullable=False, primary_key=True)
    game = Column(String(32), nullable=False)
    version = Column(Integer, nullable=False)
    userid = Column(Integer, ForeignKey("users.userid"), nullable=False)
    user = relationship("User", back_populates="refids")

    def __repr__(self) -> str:
        return (
            f'RefID<refid: {self.refid}, game: "{self.game}", version: {self.version} '
            f"userid: {self.userid}>"
        )

    @classmethod
    def from_userid(cls, userid: int) -> Optional[RefID]:
        refid = (
            db.session.query(RefID)
            .filter(
                RefID.userid == userid,
                RefID.game == DEFAULT_GAME,
                RefID.version == DEFAULT_VERSION,
            )
            .one_or_none()
        )

        return refid

    @classmethod
    def create_with_userid(cls, userid: int) -> RefID:
        # Create the ExtID
        # This method will return an already existing ExtID or create a new one and
        # return it. In this case we don't care what it returns
        _ = ExtID.create_with_userid(userid)

        # Create a new RefID that is unique
        while True:
            refid_val = "".join(random.choice("0123456789ABCDEF") for _ in range(16))
            count = db.session.query(RefID).filter(RefID.refid == refid_val).count()
            if count == 0:
                break

        # Use our newly created RefID
        refid = RefID(
            refid=refid_val, game=DEFAULT_GAME, version=DEFAULT_VERSION, userid=userid
        )
        db.session.add(refid)
        db.session.commit()

        return refid


class Profile(BaseModel):
    """
    Table for storing JSON profile blobs, indexed by refid
    """

    __tablename__ = "profiles"
    refid = Column(
        String(16), ForeignKey("refids.refid"), nullable=False, primary_key=True
    )
    data = Column(JSON, nullable=False)

    @classmethod
    def from_refid(cls, refid: str) -> Optional[Profile]:
        return db.session.query(Profile).filter(Profile.refid == refid).one_or_none()

    @classmethod
    def from_userid(cls, userid: int) -> Optional[Profile]:
        """
        Returns a user profile if it exists, or None if it doesn't
        """
        refid = RefID.from_userid(userid)

        if refid is None:
            return None

        return Profile.from_refid(refid.refid)
