import logging

from lxml import etree

from v8_server import db
from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.xml.utils import get_xml_attrib, load_xml_template
from v8_server.model.user import User


logger = logging.getLogger(__name__)


class Get(object):
    """
    Customize.Regist.Player.Syogodata.Get object
    """

    def __init__(self, root: etree) -> None:
        self.syogo = [int(x.text) for x in root.findall("syogo")]

    def __repr__(self) -> str:
        return f"Get<syogo = {self.syogo}>"


class Syogodata(object):
    """
    Customize.Regist.Player.Syogodata object
    """

    def __init__(self, root: etree) -> None:
        self.get = Get(root.find("get"))

    def __repr__(self) -> str:
        return f"Syogodata<get = {self.get}>"


class Player(object):
    """
    Customize.Regist.Player object
    """

    def __init__(self, root: etree) -> None:
        self.no = int(get_xml_attrib(root, "no"))
        self.refid = root.find("refid").text
        self.syogodata = Syogodata(root.find("syogodata"))

    def __repr__(self) -> str:
        return (
            f'Player<no = {self.no}, refid = "{self.refid}", '
            f"syogodata = {self.syogodata}>"
        )


class Regist(object):
    """
    Handle the Customize Regist request.

    Possibly just used to save some customizations for the user after the game ends.
    Such as giving the user a new title.

    <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
        <customize method="regist">
            <player no="1">
                <refid __type="str">E9D2DD02072F05C5</refid>
                <syogodata>
                    <get>
                        <syogo __type="s16">4</syogo>
                        <syogo __type="s16">0</syogo>
                    </get>
                </syogodata>
            </player>
        </customize>
    </call>
    """

    def __init__(self, req: ServiceRequest) -> None:
        self.players = [Player(x) for x in req.xml[0].findall("player")]

    def __repr__(self) -> str:
        return f"Customize.Regist<players = {self.players}>"

    def response(self) -> etree:
        # Save the syogo data (assume single player right now)
        user = User.from_refid(self.players[0].refid)
        if user is None:
            raise Exception("user should not be none")

        user_data = user.user_data
        user_data.syogo = self.players[0].syogodata.get.syogo
        db.session.commit()

        return load_xml_template("customize", "regist")
