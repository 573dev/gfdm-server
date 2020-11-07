from typing import Dict, Tuple

from flask import request

from v8_server import app
from v8_server.eamuse.services import (
    CardMng,
    DLStatus,
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


@app.route(f"{Services.SERVICE_ROUTE}/<int:route>/", methods=["POST"])
def service_service(route: int) -> FlaskResponse:
    # TODO: Ideally we want to simplify this where we send the request to some method
    # that handles checking the module/method/etc and dispaches it to the correct
    # function rather than having this if chain in here. I'd like to keep the view as
    # simple as possible
    req = ServiceRequest(request)

    if route == ServiceType.PCBTRACKER.value:
        if req.method == PCBTracker.ALIVE:
            response = PCBTracker.alive()
        else:
            raise Exception(f"Not sure how to handle this PCBTracker Request: {req}")
    elif route == ServiceType.MESSAGE.value:
        if req.method == Message.GET:
            response = Message.get()
        else:
            raise Exception(f"Not sure how to handle this Message Request: {req}")
    elif route == ServiceType.PCBEVENT.value:
        if req.method == PCBEvent.PUT:
            response = PCBEvent.put(req)
        else:
            raise Exception(f"Not sure how to handle this PCBEvent Request: {req}")
    elif route == ServiceType.PACKAGE.value:
        if req.method == Package.LIST:
            response = Package.list(req)
        else:
            raise Exception(f"Not sure how to handle this Package Request: {req}")
    elif route == ServiceType.FACILITY.value:
        if req.method == Facility.GET:
            response = Facility.get()
        else:
            raise Exception(f"Not sure how to handle this Facility Request: {req}")
    elif route == ServiceType.DLSTATUS.value:
        if req.method == DLStatus.PROGRESS:
            response = DLStatus.progress()
        else:
            raise Exception(f"Not sure how to handle this DLStatus Request: {req}")
    elif route == ServiceType.CARDMNG.value:
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
    elif route == ServiceType.LOCAL.value:
        if req.module == Local.SHOPINFO:
            response = Local.shopinfo(req)
        elif req.module == Local.DEMODATA:
            response = Local.demodata(req)
        elif req.module == Local.CARDUTIL:
            response = Local.cardutil(req)
        elif req.module == Local.GAMEINFO:
            response = Local.gameinfo(req)
        elif req.module == Local.GAMEEND:
            response = Local.gameend(req)
        elif req.module == Local.GAMETOP:
            response = Local.gametop(req)
        elif req.module == Local.CUSTOMIZE:
            response = Local.customize(req)
        else:
            raise Exception(f"Not sure how to handle this Local Request: {req}")
    else:
        raise Exception(f"Not sure how to handle this Request: {req}")
    return req.response(response)


@app.route(Services.SERVICES_ROUTE, methods=["POST"])
def services_service() -> FlaskResponse:
    req = ServiceRequest(request)
    services = Services().get_services()
    return req.response(services)
