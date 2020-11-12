import logging
from datetime import datetime

from lxml import etree

from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.xml.utils import load_xml_template


logger = logging.getLogger(__name__)


class PCBEventPutItem(object):
    """
    Contains the data for a PCBEvent Item

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
            f'PCBEventPutItem<name: "{self.name}", value: {self.value}, '
            f"time: {self.time.strftime(self.DATE_FMT)}>"
        )


class Put(object):
    """
    Handle the PCBEvent request.

    It is unknown as to what this does.

    <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
        <pcbevent method="put">
            <time __type="time">1602992385</time>
            <seq __type="u32">4</seq>
            <item>
                <name __type="str">K32.mode.std</name>
                <value __type="s32">1</value>
                <time __type="time">1602992363</time>
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
            self.items.append(PCBEventPutItem(item))

        # Log the event
        logger.info(self)

    def response(self) -> etree:
        return load_xml_template("pcbevent", "put")

    def __repr__(self) -> str:
        return (
            f"PCBEvent.Put<time: {self.time.strftime(self.DATE_FMT)}, "
            f"seq: {self.seq}, items: {self.items}>"
        )
