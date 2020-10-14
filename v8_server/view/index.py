from collections import OrderedDict

from flask import request
from lxml import etree as ET
from lxml.builder import E

from v8_server import app
from v8_server.utils.xml import eamuse_prepare_xml, eamuse_read_xml


@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    d = f"""
    {request.args}
    {request.form}
    {request.files}
    {request.values}
    {request.json}
    {request.data}
    {request.headers}
    """
    print(d)
    return "You want path: %s" % path


@app.route("/pcbtracker/service", methods=["POST"])
def pcbtracker():
    """
    Handle a PCBTracker.alive request. The only method of note is the "alive" method
    which returns whether PASELI should be active or not for this session.

    For V8 it should not be active.
    """
    request_xml, model, module, method, command = eamuse_read_xml(request)

    if method == "alive":
        response = E.response(E.pcbtracker(OrderedDict(ecenable="0", expire="600")))
        response_body, headers = eamuse_prepare_xml(response)
    else:
        # There shoulnd't really even be any other methods
        raise Exception("Not sure how to handle this PCBTracker Request")

    return response_body, headers


@app.route("/message/service", methods=["POST"])
def message():
    """
    Unknown what this does. Possibly for operator messages?
    """
    request_xml, model, module, method, command = eamuse_read_xml(request)

    response = E.response(E.message(OrderedDict(expire="600")))
    response_body, headers = eamuse_prepare_xml(response)

    return response_body, headers


@app.route("/pcbevent/service", methods=["POST"])
def pcbevent():
    """
    Handle a PCBEvent request. We do nothing for this aside from logging the event.
    """
    request_xml, model, module, method, command = eamuse_read_xml(request)

    response = E.response(E.pcbevent(OrderedDict(expire="600")))
    response_body, headers = eamuse_prepare_xml(response)

    return response_body, headers


@app.route("/facility/service", methods=["POST"])
def facility():
    """
    Handle a facility request. The only method of note is the "get" request,
    which expects to return a bunch of information about the arcade this cabinet is in,
    as well as some settings for URLs and the name of the cab.
    """
    request_xml, model, module, method, command = eamuse_read_xml(request)

    response = E.response(
        E.facility(
            E.location(
                E.id("US-123"),
                E.country("US"),
                E.region("."),
                E.name("H"),
                E.type("0", {"__type": "u8"}),
            ),
            E.line(E.id("."), E("class", "0", {"__type": "u8"}),),
            E.portfw(
                E.globalip("192.168.1.139", {"__type": "ip4", "__count": "1"}),
                E.globalport("80", {"__type": "u16"}),
                E.privateport("80", {"__type": "u16"}),
            ),
            E.public(
                E.flag("1", {"__type": "u8"}),
                E.name("."),
                E.latitude("0"),
                E.longitude("0"),
            ),
            E.share(
                E.eacoin(
                    E.notchamount("3000", {"__type": "s32"}),
                    E.notchcount("3", {"__type": "s32"}),
                    E.supplylimit("10000", {"__type": "s32"}),
                ),
                E.eapass(E.valid("365", {"__type": "u16"})),
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

    response_body, headers = eamuse_prepare_xml(response)

    return response_body, headers


@app.route("/package/service", methods=["POST"])
def package():
    """
    This is for supporting downloading of updates. We don't support this.
    """
    request_xml, model, module, method, command = eamuse_read_xml(request)

    response = E.response(E.package())
    response_body, headers = eamuse_prepare_xml(response)

    return response_body, headers


@app.route("/service/services/services/", methods=["POST"])
def services():
    # We don't need to actually read the data here, but let's do it anyway as it saves a
    # copy
    _ = eamuse_read_xml(request)

    service_names = [
        "pcbtracker",
        "pcbevent",
        "facility",
        "message",
        "package",
        "userdata",
        "userid",
        "dlstatus",
        "traceroute",
        "eacoin",
        "netlog",
        "sidmgr",
    ]

    """
        "binary",
        "cardmng",
        "dlstatus",
        "eacoin",
        "eemall",
        "facility",
        "info",
        "lobby",
        "local",
        "netlog",
        "numbering",
        "pcbevent",
        "pkglist",
        "posevent",
        "reference",
        "shopinf",
        "sidmgr",
        "userdata",
        "userid",
    """

    services = {
        "ntp": "ntp://pool.ntp.org",
        "keepalive": (
            "http://eamuse.konami.fun/"
            "keepalive?pa=127.0.0.1&ia=127.0.0.1&ga=127.0.0.1&ma=127.0.0.1&t1=2&t2=10"
        ),
        **{k: f"http://eamuse.konami.fun/{k}/service" for k in service_names},
    }

    response = E.response(
        E.services(
            expire="600",
            method="get",
            mode="operation",
            status="0",
            *[E.item(OrderedDict(name=k, url=services[k])) for k in services],
        )
    )

    response_body, headers = eamuse_prepare_xml(response)

    return response_body, 200, headers
