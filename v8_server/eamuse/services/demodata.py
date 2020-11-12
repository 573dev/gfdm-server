import logging
from datetime import datetime

from lxml import etree

from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.xml.utils import load_xml_template
from v8_server.model.song import HitChart


logger = logging.getLogger(__name__)


class Shop(object):
    """
    Demodata.Get.Shop object
    """

    def __init__(self, root: etree) -> None:
        self.locationid = root.find("locationid").text

    def __repr__(self) -> str:
        return f'Shop<locationid = "{self.locationid}">'


class Get(object):
    """
    Handle the Demodata Get request.

    Return demo data for the hitchart, etc.

    <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
        <demodata method="get">
            <shop>
                <locationid __type="str">CA-123</locationid>
            </shop>
            <hitchart_nr __type="u16">100</hitchart_nr>
        </demodata>
    </call>
    """

    DT_FMT = "%Y-%m-%d %H:%M:%S%z"

    def __init__(self, req: ServiceRequest) -> None:
        self.shop = Shop(req.xml[0].find("shop"))
        self.hitchart_nr = int(req.xml[0].find("hitchart_nr").text)

    def __repr__(self) -> str:
        return f"Demodata.Get<shop = {self.shop}, hitchart_nr = {self.hitchart_nr}>"

    def response(self) -> etree:
        rank_items = HitChart.get_ranking(self.hitchart_nr)

        # Generate all hitchart data xml
        hitchart_xml_str = ""
        for rank_item in rank_items:
            hitchart_xml_str += etree.tostring(
                load_xml_template(
                    "demodata", "get.data", {"musicid": rank_item, "last1": 0}
                )
            ).decode("UTF-8")

        args = {
            "hitchart_nr": self.hitchart_nr,
            "start": datetime.now().strftime(self.DT_FMT),
            "end": datetime.now().strftime(self.DT_FMT),
            "hitchart_data": hitchart_xml_str,
            "division": 14,
            "message": "SenPi's Kickass DrumMania V8 Machine",
        }

        return load_xml_template("demodata", "get", args)
