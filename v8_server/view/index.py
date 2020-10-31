import random
from typing import Dict, Tuple

from flask import request
from sqlalchemy.orm.exc import MultipleResultsFound

from v8_server import app
from v8_server.eamuse.services import (
    CardMng,
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


@Services.route(ServiceType.CARDMNG)
def cardmng() -> Tuple[bytes, Dict[str, str]]:
    req = ServiceRequest(request)

    if req.method == CardMng.INQUIRE:
        response = CardMng.inquire(req)
    elif req.method == CardMng.GETREFID:
        response = CardMng.getrefid(req)
    elif req.method == CardMng.AUTHPASS:
        response = CardMng.authpass(req)
    elif req.method == CardMng.BINDMODEL:
        response = CardMng.bindmodel(req)
    elif req.method == CardMng.GETKEEPSPAN:
        response = CardMng.getkeepspan()
    elif req.method == CardMng.GETDATALIST:
        response = CardMng.getdatalist()
    else:
        raise Exception(f"Not sure how to handle this Cardmng Request: {req}")

    return req.response(response)


@Services.route(ServiceType.LOCAL)
def local_service() -> FlaskResponse:
    req = ServiceRequest(request)

    if req.module == Local.SHOPINFO:
        response = Local.shopinfo(req)
    elif req.module == Local.DEMODATA:
        response = Local.demodata(req)
    elif req.module == Local.CARDUTIL:
        response = Local.cardutil(req)
    elif req.module == Local.GAMEINFO:
        response = Local.gameinfo(req)
    else:
        raise Exception(f"Not sure how to handle this Local Request: {req}")
    return req.response(response)


@app.route(Services.SERVICES_ROUTE, methods=["POST"])
def services_service() -> FlaskResponse:
    req = ServiceRequest(request)
    services = Services().get_services()
    return req.response(services)
