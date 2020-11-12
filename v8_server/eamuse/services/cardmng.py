from typing import Any, Dict, List, Optional

from lxml import etree

from v8_server import db
from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.xml.utils import get_xml_attrib, load_xml_template
from v8_server.model.user import Card, RefID, User, UserAccount
from v8_server.utils.convert import bool_to_int as btoi, int_to_bool as itob


class CardStatus(object):
    """
    Possible Card Status Values
    """

    SUCCESS = 0
    NO_PROFILE = 109
    NOT_ALLOWED = 110
    NOT_REGISTERED = 112
    INVALID_PIN = 116


class Inquire(object):
    """
    Handle the CardMng Inquire request.

    Given the Card ID, determine if we have a brand new user or a returning one.

    <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
        <cardmng
            cardid="E00401007F7AD7A4"
            cardtype="1"
            method="inquire"
            model="HCV:J:A:A"
            update="1"
        />
    </call>
    """

    def __init__(self, req: ServiceRequest) -> None:
        self.cardid = get_xml_attrib(req.xml[0], "cardid")
        self.cardtype = int(get_xml_attrib(req.xml[0], "cardtype"))
        self.update = int(get_xml_attrib(req.xml[0], "update"))

        # Model doesn't always exist in the request, unsure what it's used for
        model_value = get_xml_attrib(req.xml[0], "model")
        self.model = model_value if model_value != "None" else None

    def response(self) -> etree:
        """
        Modifyable XML Text Replacements:
            refid: The RefID.refid value for an existing user
            newflag: Set to true for a new user, else 0
            binded: Set to true if the user has a profile/account, else 0
            status: See CardMng status consts at the top of this class
        """
        # New unregistered user
        args: Dict[str, Any] = {
            "newflag": 1,
            "binded": 0,
            "status": CardStatus.NOT_REGISTERED,
        }
        drop_attributes: Optional[Dict[str, List[str]]] = {
            "cardmng": [
                "refid",
                "dataid",
                "expired",
                "exflag",
                "useridflag",
                "extidflag",
            ]
        }

        # We have a returning user
        if (user := User.from_cardid(self.cardid)) is not None:
            refid = RefID.from_userid(user.userid)
            bound = UserAccount.from_userid(user.userid) is not None

            if refid is None:
                # TODO: better exception?
                raise Exception("RefID Should not be None here!")

            args = {
                "refid": refid.refid,
                "newflag": 0,
                "binded": btoi(bound),
                "status": CardStatus.SUCCESS,
            }
            drop_attributes = None

        return load_xml_template(
            "cardmng", "inquire", args, drop_attributes=drop_attributes
        )

    def __repr__(self) -> str:
        return (
            f'CardMng.Inquire<cardid = "{self.cardid}", cardtype = {self.cardtype}, '
            f'update = {self.update}, model = "{self.model}">'
        )


class Getrefid(object):
    """
    Handle the CardMng Getrefid request.

    Given the Card ID, password, etc, generate a new RefID for the user and return it

    <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
        <cardmng
            cardid="E00401007F7AD7A4"
            cardtype="1"
            method="getrefid"
            newflag="0"
            passwd="1234"
        />
    </call>
    """

    def __init__(self, req: ServiceRequest) -> None:
        self.cardid = get_xml_attrib(req.xml[0], "cardid")
        self.cardtype = int(get_xml_attrib(req.xml[0], "cardtype"))
        self.newflag = itob(int(get_xml_attrib(req.xml[0], "newflag")))
        self.passwd = get_xml_attrib(req.xml[0], "passwd")

    def response(self) -> etree:
        # Create a new user object with the given pin
        user = User(pin=self.passwd)
        db.session.add(user)
        db.session.commit()

        # Create the card, tie it to the user account
        card = Card(cardid=self.cardid, userid=user.userid)
        db.session.add(card)
        db.session.commit()

        # Generate the refid and return it
        refid = RefID.create_with_userid(user.userid)

        return load_xml_template("cardmng", "getrefid", {"refid": refid.refid})

    def __repr__(self) -> str:
        return (
            f'CardMng.Getrefid<cardid = "{self.cardid}", cardtype = {self.cardtype}, '
            f'newflag = {self.newflag}, passwd = "{self.passwd}">'
        )


class Authpass(object):
    """
    Handle the CardMng Authpass request.

    Given the RefID, and password, verify that the password given is correct for that
    user

    <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
        <cardmng method="authpass" pass="1234" refid="E9D2DD02072F05C5"/>
    </call>
    """

    def __init__(self, req: ServiceRequest) -> None:
        self.passwd = get_xml_attrib(req.xml[0], "pass")
        self.refid = get_xml_attrib(req.xml[0], "refid")

    def response(self) -> etree:
        # Grab the refid
        refid = db.session.query(RefID).filter(RefID.refid == self.refid).one_or_none()

        if refid is None:
            raise Exception("RefID Is None Here!")

        # Check if the pin is valid for the user
        user = refid.user
        status = (
            CardStatus.SUCCESS if user.pin == self.passwd else CardStatus.INVALID_PIN
        )

        return load_xml_template("cardmng", "authpass", {"status": status})

    def __repr__(self) -> str:
        return f'CardMng.Authpass<passwd = "{self.passwd}", refid = "{self.refid}">'


class Bindmodel(object):
    """
    Handle the CardMng Bindmodel request.

    Given the RefID, and a newflag, bind the user to the current game.

    XXX: Partially unsure what this actually needs to do

    <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
        <cardmng method="bindmodel" newflag="0" refid="A01D0C781F132DBC"/>
    </call>
    """

    def __init__(self, req: ServiceRequest) -> None:
        self.refid = get_xml_attrib(req.xml[0], "refid")
        self.newflag = itob(int(get_xml_attrib(req.xml[0], "newflag")))

    def response(self) -> etree:
        refid = db.session.query(RefID).filter(RefID.refid == self.refid).one_or_none()

        if refid is None:
            raise Exception("RefID is None Here!")

        return load_xml_template("cardmng", "bindmodel", {"refid": refid.refid})

    def __repr__(self) -> str:
        return f'CardMng.Bindmodel<refid = "{self.refid}", newflag = {self.newflag}>'


# TODO: figure out if these are actually used or not
'''
    @classmethod
    def getkeepspan(cls):
        """
        Unclear what this method does, return an arbitrary span
        """

        keepspan = 30
        return load_xml_template("cardmng", "getkeepspan", {"keepspan": keepspan})

    @classmethod
    def getdatalist(cls):
        """
        Unclear what this method does, return a dummy response
        """
        return load_xml_template("cardmng", "cardmng")
'''
