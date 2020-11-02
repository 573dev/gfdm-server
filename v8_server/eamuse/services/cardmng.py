from lxml.builder import E

from v8_server import db
from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.utils.xml import get_xml_attrib
from v8_server.model.user import Card, Profile, RefID, User


class CardMng(object):
    """
    Handle the CardMng (Card Manage) request.

    This is for supporting eAmuse card interaction.
    """

    # List of statuses we return to the game for various card related reasons
    SUCCESS = 0
    NO_PROFILE = 109
    NOT_ALLOWED = 110
    NOT_REGISTERED = 112
    INVALID_PIN = 116

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
        Example Request:
            <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
                <cardmng
                    cardid="E0040100DE52896C"
                    cardtype="1"
                    method="inquire"
                    update="1"
                />
            </call>

        Example Response:
            <response>
                <cardmng
                    refid="ADE0FE0B14AEAEFC"
                    dataid="ADE0FE0B14AEAEFC"
                    newflag="1"
                    binded="0"
                    expired="0"
                    ecflag="0"
                    useridflag="1"
                    extidflag="1"
                />
            </response>
        """
        # Grab the card id
        cardid = get_xml_attrib(req.xml[0], "cardid")

        # Check if a user with this card id already exists
        user = User.from_cardid(cardid)

        if user is None:
            # The user doesn't exist, force system to create a new account
            response = E.response(
                E.cardmng(
                    {
                        "newflag": "1",
                        "binded": "0",
                        "status": str(CardMng.NOT_REGISTERED),
                    }
                )
            )
        else:
            refid = RefID.from_userid(user.userid)
            bound = Profile.from_userid(user.userid) is not None

            if refid is None:
                raise Exception("RefID Should not be None here!")

            response = E.response(
                E.cardmng(
                    {
                        "refid": refid.refid,
                        "dataid": refid.refid,
                        "newflag": "0",
                        "binded": "1" if bound else "0",
                        "expired": "0",
                        "exflag": "0",
                        "useridflag": "1",
                        "extidflag": "1",
                        "status": str(CardMng.SUCCESS),
                    }
                )
            )

        return response

    @classmethod
    def getrefid(cls, req: ServiceRequest):
        """"""
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

        return E.response(E.cardmng({"dataid": refid.refid, "refid": refid.refid}))

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
        valid = user.pin == pin

        return E.response(
            E.cardmng(
                {"status": str(CardMng.SUCCESS if valid else CardMng.INVALID_PIN)}
            )
        )

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

        return E.response(E.cardmng({"dataid": refid.refid}))

    @classmethod
    def getkeepspan(cls):
        """
        Unclear what this method does, return an arbitrary span
        """
        return E.response(E.cardmng({"keepspan": "30"}))

    @classmethod
    def getdatalist(cls):
        """
        Unclear what this method does, return a dummy response
        """
        return E.response(E.cardmng())
