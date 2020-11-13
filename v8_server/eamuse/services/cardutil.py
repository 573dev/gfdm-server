import logging
from typing import Any, Dict, List, Optional

from lxml import etree

from v8_server import db
from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.xml.utils import get_xml_attrib, load_xml_template
from v8_server.model.user import User, UserAccount, UserData
from v8_server.utils.convert import int_to_bool as itob


logger = logging.getLogger(__name__)


class Card(object):
    """
    Cardutil.Check.Card object
    """

    def __init__(self, root: etree) -> None:
        self.no = int(get_xml_attrib(root, "no"))
        self.refid = root.find("refid").text
        self.uid = root.find("uid").text

    def __repr__(self) -> str:
        return f'Card<no = {self.no}, refid = "{self.refid}", uid = "{self.uid}">'


class CheckStatus(object):
    """
    Status values for the Cardutil.Check response
    """

    NEW_USER = 0
    UNKNOWN = 1  # XXX: Unsure if this is used anywhere for anything
    EXISTING_USER = 2


class Check(object):
    """
    Handle the Cardutil.Check request.

    Checks to see if the card belongs to a new user or an existing registered user.

    <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
        <cardutil method="check">
            <card no="1">
                <refid __type="str">E9D2DD02072F05C5</refid>
                <uid __type="str">E00401007F7AD7A4</uid>
            </card>
        </cardutil>
    </call>
    """

    def __init__(self, req: ServiceRequest) -> None:
        self.card = Card(req.xml[0].find("card"))

    def __repr__(self) -> str:
        return f"Cardutil.Check<card = {self.card}>"

    def response(self) -> etree:
        user = User.from_refid(self.card.refid)

        new_user = (
            user is None or (account := UserAccount.from_userid(user.userid)) is None
        )

        # New User
        args: Dict[str, Any] = {"state": CheckStatus.NEW_USER}
        drop_children: Optional[Dict[str, List[str]]] = {
            "cardutil/card": [
                "name",
                "gdp",
                "skill",
                "all_skill",
                "chara",
                "syogo",
                "penalty",
            ],
        }

        # Existing User
        if not new_user and account is not None and user is not None:
            user_data = user.user_data
            # TODO: Add GDP, skill, all_skill here
            args = {
                "state": CheckStatus.EXISTING_USER,
                "name": account.name,
                "gdp": 0,
                "skill": 0,
                "all_skill": 0,
                "syogo": " ".join(map(str, user_data.syogo)),
                "chara": account.chara,
            }
            drop_children = None

        return load_xml_template("cardutil", "check", args, drop_children=drop_children)


class Data(object):
    """
    Cardutil.Regist.Data object
    """

    def __init__(self, root: etree) -> None:
        self.no = int(get_xml_attrib(root, "no"))
        self.refid = root.find("refid").text
        self.name = root.find("name").text
        self.chara = int(root.find("chara").text)
        self.uid = root.find("uid").text
        self.cabid = int(root.find("cabid").text)
        self.is_succession = itob(int(root.find("is_succession").text))

    def __repr__(self) -> str:
        return (
            f'Data<no = {self.no}, refid = "{self.refid}", name = "{self.name}", '
            f'chara = {self.chara}, uid = "{self.uid}", cabid = {self.cabid}, '
            f"is_succession = {self.is_succession}>"
        )


class Regist(object):
    """
    Handle the Cardutil Regist request.

    Register the data for a new user.

    <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
        <cardutil method="regist">
            <data no="1">
                <refid __type="str">E9D2DD02072F05C5</refid>
                <name __type="str">AAAA</name>
                <chara __type="u8">0</chara>
                <uid __type="str">E00401007F7AD7A4</uid>
                <cabid __type="u32">1</cabid>
                <is_succession __type="s8">0</is_succession>
            </data>
        </cardutil>
    </call>
    """

    def __init__(self, req: ServiceRequest) -> None:
        self.data = Data(req.xml[0].find("data"))

    def __repr__(self) -> str:
        return f"Cardutil.Regist<data = {self.data}>"

    def response(self) -> etree:
        user = User.from_refid(self.data.refid)
        if user is None:
            raise Exception("This user should theoretically exist here")
        if user.card.cardid != self.data.uid:
            raise Exception(
                f"Card ID is incorrect: {user.card.cardid} != {self.data.uid}"
            )

        user_account = UserAccount(
            userid=user.userid,
            name=self.data.name,
            chara=self.data.chara,
            is_succession=self.data.is_succession,
        )
        db.session.add(user_account)

        user_data = UserData(
            userid=user.userid,
            style=2097152,
            style_2=0,
            secret_music=[0 for _ in range(0, 32)],
            secret_chara=0,
            syogo=[0, 0],
            perfect=0,
            great=0,
            good=0,
            poor=0,
            miss=0,
            time=0,
        )
        db.session.add(user_data)
        db.session.commit()

        return load_xml_template("cardutil", "regist")
