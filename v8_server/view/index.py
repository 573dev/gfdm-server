import importlib
from typing import Dict, Tuple

from flask import request

from v8_server import app
from v8_server.eamuse.services import ServiceRequest, Services


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

    if req.method is not None:
        method = req.method.title().replace("_", "")
        try:
            module = importlib.import_module(f"v8_server.eamuse.services.{req.module}")
        except ModuleNotFoundError:
            app.logger.error(f"No Module found for request: {req}")
            raise

        try:
            cls = getattr(module, method)
        except AttributeError:
            app.logger.error(f"No Class found for request: {req}")
            raise

        inst = cls(req)
        app.logger.debug(inst)
        response = inst.response()
    else:
        print(route)
        raise Exception(f"Not sure how to handle this Request: {req}")

    return req.response(response)


@app.route(Services.SERVICES_ROUTE, methods=["POST"])
def services_service() -> FlaskResponse:
    req = ServiceRequest(request)
    services = Services().get_services()
    return req.response(services)
