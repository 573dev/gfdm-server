import random
from typing import Dict, Tuple

from flask import request
from sqlalchemy.orm.exc import MultipleResultsFound

from v8_server import app
from v8_server.eamuse.services import (
    Facility,
    Local,
    Message,
    Package,
    PCBEvent,
    PCBTracker,
    ServiceRequest,
    Services,
    ServiceType,
)
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


@Services.route(ServiceType.PCBTRACKER)
def pcbtracker_service() -> FlaskResponse:
    req = ServiceRequest(request)

    if req.method == PCBTracker.ALIVE:
        response = PCBTracker.alive()
    else:
        raise Exception(f"Not sure how to handle this PCBTracker Request: {req}")

    return req.response(response)


@Services.route(ServiceType.MESSAGE)
def message_service() -> FlaskResponse:
    req = ServiceRequest(request)

    if req.method == Message.GET:
        response = Message.get()
    else:
        raise Exception(f"Not sure how to handle this Message Request: {req}")

    return req.response(response)


@Services.route(ServiceType.PCBEVENT)
def pcbevent_service() -> FlaskResponse:
    req = ServiceRequest(request)
    event = PCBEvent(req)
    app.logger.info(event)

    if req.method == PCBEvent.PUT:
        response = PCBEvent.put()
    else:
        raise Exception(f"Not sure how to handle this PCBEvent Request: {req}")

    return req.response(response)


@Services.route(ServiceType.PACKAGE)
def package_service() -> FlaskResponse:
    req = ServiceRequest(request)

    if req.method == Package.LIST:
        response = Package.list(req)
    else:
        raise Exception(f"Not sure how to handle this Package Request: {req}")

    return req.response(response)


@Services.route(ServiceType.FACILITY)
def facility_service() -> FlaskResponse:
    req = ServiceRequest(request)

    if req.method == Facility.GET:
        response = Facility.get()
    else:
        raise Exception(f"Not sure how to handle this Facility Request: {req}")

    return req.response(response)


'''
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
'''


@Services.route(ServiceType.LOCAL)
def local_service() -> FlaskResponse:
    req = ServiceRequest(request)

    if req.module == Local.SHOPINFO:
        response = Local.shopinfo(req)
    elif req.module == Local.DEMODATA:
        response = Local.demodata(req)
    elif req.module == Local.CARDUTIL:
        response = Local.cardutil(req)
    else:
        raise Exception(f"Not sure how to handle this Local Request: {req}")
    return req.response(response)


@app.route(Services.SERVICES_ROUTE, methods=["POST"])
def services_service() -> FlaskResponse:
    req = ServiceRequest(request)
    services = Services().get_services()
    return req.response(services)
