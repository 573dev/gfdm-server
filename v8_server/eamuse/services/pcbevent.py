import logging
from datetime import datetime

from lxml import etree
from lxml.builder import E

from v8_server.eamuse.services.services import ServiceRequest


logger = logging.getLogger(__name__)


class PCBEventItem(object):
    """
    Contains the data for a PCBEvent Item

    Example:
        <item>
            <name __type="str">K32.mode.std</name>
            <value __type="s32">1</value>
            <time __type="time">1602992363</time>
        </item>
    """

    DATE_FMT = "%b/%d/%Y-%H:%M:%S"

    def __init__(self, xml_root: etree) -> None:
        # Build our data from the `item` xml root object
        self.name = xml_root.find("name").text
        self.value = int(xml_root.find("value").text)
        self.time = datetime.fromtimestamp(int(xml_root.find("time").text))

    def __repr__(self) -> str:
        return (
            f'PCBEventItem<name: "{self.name}", value: {self.value}, '
            f"time: {self.time.strftime(self.DATE_FMT)}>"
        )


class PCBEvent(object):
    """
    Handle the PCBEvent request.

    It is unknown as to what this does.

    Example:
        <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
            <pcbevent method="put">
                <time __type="time">1602992385</time>
                <seq __type="u32">4</seq>
                <item>
                    <name __type="str">K32.mode.std</name>
                    <value __type="s32">1</value>
                    <time __type="time">1602992363</time>
                </item>
                <item>
                    <name __type="str">K32.playcnt.t</name>
                    <value __type="s32">1</value>
                    <time __type="time">1602992363</time>
                </item>
                <item>
                    <name __type="str">game.e</name>
                    <value __type="s32">1</value>
                    <time __type="time">1602992371</time>
                </item>
            </pcbevent>
        </call>
    """

    DATE_FMT = "%b/%d/%Y-%H:%M:%S"

    def __init__(self, req: ServiceRequest) -> None:
        # Build our item from the data
        xml_root = req.xml[0]

        self.time = datetime.fromtimestamp(int(xml_root.find("time").text))
        self.seq = int(xml_root.find("seq").text)

        self.items = []
        for item in xml_root.findall("item"):
            self.items.append(PCBEventItem(item))

    # Methods
    PUT = "put"

    @classmethod
    def put(cls, req: ServiceRequest):
        """
        Example:
            <response>
                <pcbevent expire="600"/>
            </response>
        """
        # Log the event
        event = PCBEvent(req)
        logger.info(event)

        return E.response(E.pcbevent({"expire": "600"}))

    def __repr__(self) -> str:
        return (
            f"PCBEvent<time: {self.time.strftime(self.DATE_FMT)}, "
            f"seq: {self.seq}, items: {self.items}>"
        )
