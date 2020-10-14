from flask import request
from lxml.builder import E

from v8_server import app
from v8_server.utils.xml import eamuse_prepare_xml, eamuse_read_xml


@app.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@app.route("/<path:path>", methods=["GET", "POST"])
def catch_all(path):
    """
    This is currently my catch all route, for whenever a new endpoint pops up that isn't
    implemented
    """
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


def base_response(element, attributes=None):
    if attributes is None:
        attributes = {}
    return E.response(E(element, {**attributes, "expire": "600"}))


@app.route("/pcbtracker/service", methods=["POST"])
def pcbtracker():
    """
    Handle a PCBTracker.alive request. The only method of note is the "alive" method
    which returns whether PASELI should be active or not for this session.

    For V8 it should not be active.
    """
    method = eamuse_read_xml(request)[3]

    if method == "alive":
        response = base_response("pcbtracker", {"ecenable": "0"})
    else:
        # There shoulnd't really even be any other methods
        raise Exception("Not sure how to handle this PCBTracker Request")

    return eamuse_prepare_xml(response)


@app.route("/message/service", methods=["POST"])
def message():
    """
    Unknown what this does. Possibly for operator messages?
    """
    _ = eamuse_read_xml(request)
    response = base_response("message")
    return eamuse_prepare_xml(response)


@app.route("/pcbevent/service", methods=["POST"])
def pcbevent():
    """
    Handle a PCBEvent request. We do nothing for this aside from logging the event.
    """
    _ = eamuse_read_xml(request)

    # TODO: Log the data from `request_xml`

    response = base_response("pcbevent")
    return eamuse_prepare_xml(response)


@app.route("/facility/service", methods=["POST"])
def facility():
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
    return eamuse_prepare_xml(response)


@app.route("/package/service", methods=["POST"])
def package():
    """
    This is for supporting downloading of updates. We don't support this.
    """
    _ = eamuse_read_xml(request)

    response = base_response("package")
    return eamuse_prepare_xml(response)


@app.route("/service/services/services/", methods=["POST"])
def services():
    # We don't need to actually read the data here, but let's do it anyway as it saves a
    # copy
    _ = eamuse_read_xml(request)

    service_names = [
        "dlstatus",
        "eacoin",
        "facility",
        "local",
        "message",
        "netlog",
        "package",
        "pcbevent",
        "pcbtracker",
        "sidmgr",
        "traceroute",
        "userdata",
        "userid",
    ]

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
            *[E.item({"name": k, "url": services[k]}) for k in services],
        )
    )

    return eamuse_prepare_xml(response)
