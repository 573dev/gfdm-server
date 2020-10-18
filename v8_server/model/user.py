from sqlalchemy import JSON, Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from v8_server.model.connection import Base


class User(Base):
    """
    Table representing a user. Each user has a Unique ID and a pin which is used
    with all cards associated with the user's account.
    """

    __tablename__ = "users"

    uid = Column(Integer, nullable=False, primary_key=True)
    pin = Column(String(4), nullable=False)
    cards = relationship("Card", back_populates="user")
    extids = relationship("ExtID", back_populates="user")
    refids = relationship("RefID", back_populates="user")

    def __repr__(self) -> str:
        return f'User<uid: {self.uid}, pin: "{self.pin}">'


class Card(Base):
    """
    Table representing a card associated with a user. Users may have zero or more cards
    associated with them. When a new card is used in a game, a new user will be created
    to asociate with a card.
    """

    __tablename__ = "cards"

    uid = Column(String(16), nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.uid"), nullable=False)
    user = relationship("User", back_populates="cards")

    def __repr__(self) -> str:
        return f'Card<uid: "{self.uid}", user_id: {self.user_id}>'


class ExtID(Base):
    """
    Table representing and extid for a user across a game series. Each game series on
    the network gets its own extid (8 digit number) for each user.
    """

    __tablename__ = "extids"
    __table_args_ = (UniqueConstraint("game", "user_id", name="game_user_id"),)
    uid = Column(Integer, nullable=False, primary_key=True)
    game = Column(String(32), nullable=False)
    user_id = Column(Integer, ForeignKey("users.uid"), nullable=False)
    user = relationship("User", back_populates="extids")

    def __repr__(self) -> str:
        return f'ExtID<uid: {self.uid}, game: "{self.game}", user_id: {self.user_id}>'


class RefID(Base):
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
        UniqueConstraint("game", "version", "user_id", name="game_version_user_id"),
    )
    uid = Column(String(16), nullable=False, primary_key=True)
    game = Column(String(32), nullable=False)
    version = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.uid"), nullable=False)
    user = relationship("User", back_populates="refids")

    def __repr__(self) -> str:
        return (
            f'RefID<uid: {self.uid}, game: "{self.game}", version: {self.version} '
            f"user_id: {self.user_id}>"
        )


class Profile(Base):
    """
    Table for storing JSON profile blobs, indexed by refid
    """

    __tablename__ = "profiles"
    ref_id = Column(
        String(16), ForeignKey("refids.uid"), nullable=False, primary_key=True
    )
    data = Column(JSON, nullable=False)
