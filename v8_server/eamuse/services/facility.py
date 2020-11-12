from lxml import etree

from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.xml.utils import get_xml_attrib, load_xml_template


class Get(object):
    """
    Handle the Facility Get request.

    This method expects to return a bunch of information about the arcade this cabinet
    is in, as well as some settings for URLs and the name of the Arcade.

    <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
        <facility encoding="SHIFT_JIS" method="get"/>
    </call>
    """

    def __init__(self, req: ServiceRequest) -> None:
        self.encoding = get_xml_attrib(req.xml[0], "encoding")

    def response(self) -> etree:
        # TODO: The facility data should be read in from a config file instead of being
        # hard coded here

        args = {
            "id": "CA-123",
            "country": "CA",
            "region": "MB",
            "name": "SenPi Arcade",
        }
        return load_xml_template("facility", "get", args)

    def __repr__(self) -> str:
        return f'Facility.Get<encoding = "{self.encoding}">'
