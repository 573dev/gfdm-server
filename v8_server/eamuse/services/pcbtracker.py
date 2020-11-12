from lxml import etree

from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.xml.utils import get_xml_attrib, load_xml_template
from v8_server.utils.convert import bool_to_int as btoi


class Alive(object):
    """
    Handle the PCBTracker Alive request.

    This method which returns whether PASELI should be active or not for this session.

    <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
        <pcbtracker hardid="010074D435AAD895" method="alive" softid=""/>
    </call>
    """

    def __init__(self, req: ServiceRequest) -> None:
        self.hardid = get_xml_attrib(req.xml[0], "hardid")
        self.softid = get_xml_attrib(req.xml[0], "softid")

        # Most likely you'd determine this value from the hardware id?
        # Right now we don't support paseli
        self.paseli_active = False

    def response(self) -> etree:
        return load_xml_template(
            "pcbtracker", "alive", {"ecenable": btoi(self.paseli_active)}
        )

    def __repr__(self) -> str:
        return (
            f'PCBTracker.Alive<hardid="{self.hardid}", softid="{self.softid}", '
            f"paseli_active = {self.paseli_active}>"
        )
