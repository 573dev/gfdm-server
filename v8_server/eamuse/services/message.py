from lxml import etree

from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.xml.utils import load_xml_template


class Get(object):
    """
    Handle the Message Get request.

    It is unknown as to what this does. Possibly it's for operator messages

    <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
        <message method="get"/>
    </call>
    """

    def __init__(self, req: ServiceRequest) -> None:
        pass

    def response(self) -> etree:
        return load_xml_template("message", "get")

    def __repr__(self) -> str:
        return "Message.Get<>"
