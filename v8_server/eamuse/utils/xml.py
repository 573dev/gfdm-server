from datetime import datetime
from typing import Optional

from lxml import etree


def get_xml_tag(xml: etree) -> str:
    return str(xml.tag)


def get_xml_attrib(xml: etree, name: str) -> str:
    return str(xml.attrib[name]) if name in xml.attrib else "None"


def format_date(timestamp: Optional[int]) -> str:
    if timestamp is None:
        return "None"

    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")
