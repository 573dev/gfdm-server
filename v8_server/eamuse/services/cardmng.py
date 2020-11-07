from v8_server import db
from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.xml.utils import (
    drop_attributes,
    get_xml_attrib,
    load_xml_template,
)
from v8_server.model.user import Card, Profile, RefID, User, UserAccount
from v8_server.utils.convert import bool_to_int as btoi


class CardStatus(object):
    """
    Possible Card Status Values
    """

    SUCCESS = 0
    NO_PROFILE = 109
    NOT_ALLOWED = 110
    NOT_REGISTERED = 112
    INVALID_PIN = 116


class CardMng(object):
    """
    Handle the CardMng (Card Manage) request.

    This is for supporting eAmuse card interaction.
    """

    # Methods
    INQUIRE = "inquire"
    GETREFID = "getrefid"
    AUTHPASS = "authpass"
    BINDMODEL = "bindmodel"
    GETKEEPSPAN = "getkeepspan"
    GETDATALIST = "getdatalist"

    @classmethod
    def inquire(cls, req: ServiceRequest):
        """
        Handle a Card Manage Inquire Request

        Either the given card id is a brand new user, or a returning user.

        Modifyable XML Text Replacements:
            refid: The RefID.refid value for an existing user
            newflag: Set to true for a new user, else 0
            binded: Set to true if the user has a profile/account, else 0
            status: See CardMng status consts at the top of this class
        """

        # Grab the card id
        cardid = get_xml_attrib(req.xml[0], "cardid")

        # Default result for a new unregistered user
        args = {
            "refid": "",
            "newflag": 1,
            "binded": 0,
            "status": CardStatus.NOT_REGISTERED,
        }

        # Check if a user with this card id already exists
        user = User.from_cardid(cardid)

        # We have a returning user
        if user is not None:
            refid = RefID.from_userid(user.userid)
            bound = UserAccount.from_userid(user.userid) is not None

            if refid is None:
                # TODO: better exception?
                raise Exception("RefID Should not be None here!")

            args["refid"] = refid.refid
            args["newflag"] = 0
            args["binded"] = btoi(bound)
            args["status"] = CardStatus.SUCCESS

        result = load_xml_template("cardmng", "inquire", args)

        # If we have a brand new user, we can remove unnecessary xml attributes from the
        # cardmng node
        if user is None:
            drop_attributes(
                result.find("cardmng"),
                ["refid", "dataid", "expired", "exflag", "useridflag", "extidflag"],
            )

        return result

    @classmethod
    def getrefid(cls, req: ServiceRequest):
        # Grab the card id and pin
        cardid = get_xml_attrib(req.xml[0], "cardid")
        pin = get_xml_attrib(req.xml[0], "passwd")

        # Create a new user object with the given pin
        user = User(pin=pin)
        db.session.add(user)
        db.session.commit()

        # Create the card, tie it to the user account
        card = Card(cardid=cardid, userid=user.userid)
        db.session.add(card)
        db.session.commit()

        # Generate the refid and return it
        refid = RefID.create_with_userid(user.userid)

        return load_xml_template("cardmng", "getrefid", {"refid": refid.refid})

    @classmethod
    def authpass(cls, req: ServiceRequest):
        """"""
        # Grab the refid and pin
        refid_str = get_xml_attrib(req.xml[0], "refid")
        pin = get_xml_attrib(req.xml[0], "pass")

        # Grab the refid
        refid = db.session.query(RefID).filter(RefID.refid == refid_str).one_or_none()

        if refid is None:
            raise Exception("RefID Is None Here!")

        # Check if the pin is valid for the user
        user = refid.user
        status = CardStatus.SUCCESS if user.pin == pin else CardStatus.INVALID_PIN

        return load_xml_template("cardmng", "authpass", {"status": status})

    @classmethod
    def bindmodel(cls, req: ServiceRequest):
        """"""
        # Grab the refid
        refid_str = get_xml_attrib(req.xml[0], "refid")
        refid = db.session.query(RefID).filter(RefID.refid == refid_str).one_or_none()

        if refid is None:
            raise Exception("RefID is None Here!")

        # Just bind some garbage here for now
        profile = Profile(refid=refid.refid, data={"data": "something"})
        db.session.add(profile)
        db.session.commit()

        return load_xml_template("cardmng", "bindmodel", {"refid": refid.refid})

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
