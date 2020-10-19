import random
from typing import Dict, Tuple

from flask import request
from lxml import etree as ET  # noqa: N812
from lxml.builder import E
from sqlalchemy.orm.exc import MultipleResultsFound

from v8_server import app
from v8_server.eamuse.services.pcbtracker import PCBTracker
from v8_server.eamuse.services.services import ServiceRequest, Services, ServiceType
from v8_server.eamuse.utils.eamuse import e_type
from v8_server.eamuse.utils.xml import get_xml_attrib
from v8_server.model.connection import Database
from v8_server.model.user import Card, ExtID, Profile, RefID, User


FlaskResponse = Tuple[bytes, Dict[str, str]]


@app.route("/", defaults={"u_path": ""}, methods=["GET", "POST"])
@app.route("/<path:u_path>", methods=["GET", "POST"])
def catch_all(u_path: str) -> str:
    """
    This is currently my catch all route, for whenever a new endpoint pops up that isn't
    implemented
    """
    headers = request.headers

    header_str = ""
    for header in headers:
        header_str += f"{header[0]:>15}: {header[1]}\n"

    args = "None" if len(request.args) == 0 else request.args
    data = request.data
    d = (
        "*** Unknown Request ***\n"
        f"           Args: {args}\n"
        f"    Data Length: {len(data)}\n"
        f"{header_str[:-1]}\n"
    )
    app.logger.debug(d)
    return "You want path: %s" % u_path


def base_response(element: str, attributes: Dict[str, str] = None) -> ET:
    if attributes is None:
        attributes = {}
    return E.response(E(element, {**attributes, "expire": "600"}))


@Services.route(app, ServiceType.PCBTRACKER)
def pcbtracker_service() -> FlaskResponse:
    req = ServiceRequest(request)

    if req.method == PCBTracker.ALIVE:
        response = PCBTracker.alive()
    else:
        raise Exception(f"Not sure how to handle this PCBTracker Request: {req}")

    return req.response(response)


'''
@app.route("/message/service", methods=["POST"])
def message() -> Tuple[bytes, Dict[str, str]]:
    """
    Unknown what this does. Possibly for operator messages?
    """
    _ = eamuse_read_xml(request)
    response = base_response("message")
    return eamuse_prepare_xml(response, request)


@app.route("/pcbevent/service", methods=["POST"])
def pcbevent() -> Tuple[bytes, Dict[str, str]]:
    """
    Handle a PCBEvent request. We do nothing for this aside from logging the event.
    """
    _ = eamuse_read_xml(request)
    response = base_response("pcbevent")
    return eamuse_prepare_xml(response, request)


@app.route("/facility/service", methods=["POST"])
def facility() -> Tuple[bytes, Dict[str, str]]:
    """
    Handle a facility request. The only method of note is the "get" request,
    which expects to return a bunch of information about the arcade this cabinet is in,
    as well as some settings for URLs and the name of the cab.
    """
    _ = eamuse_read_xml(request)

    response = E.response(
        E.facility(
            E.location(
                E.id("US-123"),
                E.country("US"),
                E.region("."),
                E.name("H"),
                E.type("0", e_type("u8")),
            ),
            E.line(E.id("."), E("class", "0", e_type("u8"))),
            E.portfw(
                E.globalip("192.168.1.139", e_type("ip4", count=1)),
                E.globalport("80", e_type("u16")),
                E.privateport("80", e_type("u16")),
            ),
            E.public(
                E.flag("1", e_type("u8")),
                E.name("."),
                E.latitude("0"),
                E.longitude("0"),
            ),
            E.share(
                E.eacoin(
                    E.notchamount("3000", e_type("s32")),
                    E.notchcount("3", e_type("s32")),
                    E.supplylimit("10000", e_type("s32")),
                ),
                E.eapass(E.valid("365", e_type("u16"))),
                E.url(
                    E.eapass("www.ea-pass.konami.net"),
                    E.arcadefan("www.konami.jp/am"),
                    E.konaminetdx("http://am.573.jp"),
                    E.konamiid("http://id.konami.net"),
                    E.eagate("http://eagate.573.jp"),
                ),
            ),
            {"expire": "600"},
        )
    )
    return eamuse_prepare_xml(response, request)


@app.route("/package/service", methods=["POST"])
def package() -> Tuple[bytes, Dict[str, str]]:
    """
    This is for supporting downloading of updates. We don't support this.
    """
    _ = eamuse_read_xml(request)

    response = base_response("package")
    return eamuse_prepare_xml(response, request)


class CardStatus(object):
    """
    List of statuses we return to the game for various reasons
    """

    SUCCESS = 0
    NO_PROFILE = 109
    NOT_ALLOWED = 110
    NOT_REGISTERED = 112
    INVALID_PIN = 116


def create_refid(user_id: int) -> str:
    with Database() as db:
        # Create a new extid that is unique
        while True:
            e_id = random.randint(0, 89999999) + 10000000
            if db.session.query(ExtID).filter(ExtID.uid == e_id).count() == 0:
                break

        # Use that ext_id
        ext_id = ExtID(uid=e_id, game="GFDM", user_id=user_id)

        try:
            db.session.add(ext_id)
        except Exception:
            # Most likely a duplicate error as this user already has an ExtID for this
            # game series
            pass

        # Create a new refid that is unique
        while True:
            r_id = "".join(random.choice("0123456789ABCDEF") for _ in range(16))
            if db.session.query(RefID).filter(RefID.uid == r_id).count() == 0:
                break

        # Use that ref_id
        ref_id = RefID(uid=r_id, game="GFDM", version=8, user_id=user_id)
        db.session.add(ref_id)
        db.session.commit()

        uid = ref_id.uid

    return uid


def has_profile(user_id: int) -> bool:
    result = False
    with Database() as db:
        ref_id = (
            db.session.query(RefID)
            .filter(RefID.game == "GFDM", RefID.version == 8, RefID.user_id == user_id)
            .one()
        )
        result = (
            db.session.query(Profile).filter(Profile.ref_id == ref_id.uid).count() != 0
        )
    return result


@app.route("/cardmng/service", methods=["POST"])
def cardmng() -> Tuple[bytes, Dict[str, str]]:
    """
    This is for dealing with the card management
    """
    xml, model_str, module, method, command = eamuse_read_xml(request)

    if method == "inquire":
        card_id = get_xml_attrib(xml[0], "cardid")

        with Database() as db:
            # Check if the user already exists
            try:
                card = db.session.query(Card).filter(Card.uid == card_id).one_or_none()
            except MultipleResultsFound:
                app.logger.error(f"Multiple Cards found for Card ID: {card_id}")
                raise

            if card is None:
                # This user doesn't exist, force the system to create a new account
                response = E.response(
                    E.cardmng({"status": str(CardStatus.NOT_REGISTERED)})
                )
            else:
                # Special handing for looking up whether the previous game's profile
                # existed
                user = db.session.query(User).filter(User.uid == card.user_id).one()
                bound = has_profile(user.uid)
                expired = False

                ref_id = (
                    db.session.query(RefID)
                    .filter(
                        RefID.game == "GFDM",
                        RefID.version == 8,
                        RefID.user_id == user.uid,
                    )
                    .one()
                )
                paseli_enabled = False

                response = E.response(
                    E.cardmng(
                        {
                            "refid": ref_id.uid,
                            "dataid": ref_id.uid,
                            "newflag": "1",  # A;ways seems to be set to 1
                            "binded": "1" if bound else "0",
                            "expired": "1" if expired else "0",
                            "ecflag": "1" if paseli_enabled else "0",
                            "useridflag": "1",
                            "extidflag": "1",
                        }
                    )
                )
    elif method == "getrefid":
        # Given a card_id, and a pin, register the card with the system and generate a
        # new data_id/ref_id + ext_id
        card_id = get_xml_attrib(xml[0], "cardid")
        pin = get_xml_attrib(xml[0], "passwd")

        with Database() as db:
            # Create the user object
            user = User(pin=pin)
            db.session.add(user)

            # We must commit to assign a uid
            db.session.commit()
            user_id = user.uid

            # Now insert the card, tying it to the account
            card = Card(uid=card_id, user_id=user_id)
            db.session.add(card)
            db.session.commit()

        ref_id = create_refid(user_id)
        response = E.response(E.cardmng({"dataid": ref_id, "refid": ref_id}))
    elif method == "authpass":
        # Given a data_id/ref_id previously found via inquire, verify the pin
        ref_id = get_xml_attrib(xml[0], "refid")
        pin = get_xml_attrib(xml[0], "pass")

        with Database() as db:
            refid = db.session.query(RefID).filter(RefID.uid == ref_id).one()
            user = (
                db.session.query(User).filter(User.uid == refid.user_id).one_or_none()
            )

            if user is not None:
                valid = pin == user.pin
            else:
                valid = False

            response = E.response(
                E.cardmng(
                    {
                        "status": str(
                            CardStatus.SUCCESS if valid else CardStatus.INVALID_PIN
                        )
                    }
                )
            )
    elif method == "bindmodel":
        # Given a refid, bind the user's card to the current version of the game
        # TODO: Not implemented right now. do it later
        ref_id = get_xml_attrib(xml[0], "refid")
        response = E.response(E.cardmng({"dataid": ref_id}))
    elif method == "getkeepspan":
        # Unclear what this method does, return an arbitrary span
        response = E.response(E.cardmng({"keepspan", "30"}))
    elif method == "getdatalist":
        # Unclear what this method does, return a dummy response
        response = base_response(module)
    else:
        response = base_response(module)
    return eamuse_prepare_xml(response, request)


@app.route("/local/service", methods=["POST"])
def local() -> Tuple[bytes, Dict[str, str]]:
    """
    This is probably a big chunk of implementation. Handle all "local" service requests
    which might have a whole bunch of stuff going on
    """

    xml, model, module, method, command = eamuse_read_xml(request)

    if module == "shopinfo":
        if method == "regist":
            response = E.response(
                E.shopinfo(
                    E.data(
                        E.cabid("1", e_type("u32")),
                        E.locationid("nowhere"),
                        E.is_send("1", e_type("u8")),
                    )
                )
            )
    elif module == "demodata":
        # TODO: Not really sure what to return here
        if method == "get":
            response = base_response(module)
    elif module == "cardutil":
        # TODO: Not really sure what to return here
        if method == "check":
            # Return the users game information

            # If the user doesn't have any game information yet:
            response = E.response(
                E.cardutil(E.card(E.kind("0", e_type("s8")), {"no": "1", "state": "0"}))
            )

            # Else get the user info and send that you idiot
    else:
        response = base_response(module)

    return eamuse_prepare_xml(response, request)

'''


@app.route(Services.SERVICES_ROUTE, methods=["POST"])
def services_service() -> Tuple[bytes, Dict[str, str]]:
    s_req = ServiceRequest(request)
    services = Services().get_services()
    return s_req.response(services)
