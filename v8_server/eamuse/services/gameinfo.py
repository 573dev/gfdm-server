import logging

from lxml import etree

from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.utils.crc import calculate_crc8
from v8_server.eamuse.xml.utils import load_xml_template


logger = logging.getLogger(__name__)


class Shop(object):
    """
    Gameinfo.Get.Shop object
    """

    def __init__(self, root: etree) -> None:
        self.locationid = root.find("locationid").text
        self.cabid = int(root.find("cabid").text)

    def __repr__(self) -> str:
        return f"Shop<locationid = {self.locationid}, cabid = {self.cabid}>"


class Get(object):
    """
    Handle the Gameinfo Get request.

    Returns various game data at the start of a game session.

    <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
        <gameinfo method="get">
            <shop>
                <locationid __type="str">CA-123</locationid>
                <cabid __type="u32">1</cabid>
            </shop>
        </gameinfo>
    </call>
    """

    def __init__(self, req: ServiceRequest) -> None:
        self.shop = Shop(req.xml[0].find("shop"))

    def __repr__(self) -> str:
        return f"Gameinfo.Get<shop = {self.shop}>"

    def response(self) -> etree:
        # tag is the crc8 checksum of free_music and free_chara
        # I also don't actually know what these free_music/chara values mean
        args = {
            "free_music": 262143,
            "free_chara": 1824,
            "tag": calculate_crc8(str(262143 + 1824)),
            "division": 14,
        }
        return load_xml_template("gameinfo", "get", args)
