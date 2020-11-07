import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from lxml import etree


logger = logging.getLogger(__name__)


def load_xml_template(
    service: str, method: str, args: Optional[Dict[str, Any]], /  # noqa: W504
) -> etree:
    """
    Given a service and a method, load the appropriate XML template and return it

    Args:
        service (str): eAmuse Service Name
        method (str): eAmuse Method Name
        args (Dict[str, Any]): Used for formatting the xml string

    Returns:
        etree: Resulting XML etree
    """
    template_path = Path(__file__).parent / "templates"
    filepath = template_path / service / f"{method}.xml"

    try:
        xml_str = filepath.open().read()
    except Exception:
        raise

    if args is not None:
        xml_str = xml_str.format(**args)

    return etree.fromstring(xml_str.encode("UTF-8"))


def drop_attributes(element: etree, attributes: List[str]) -> None:
    for attribute in attributes:
        element.attrib.pop(attribute)


def fill(count: int, value: str = "0") -> str:
    return " ".join(value for _ in range(0, count))


class XMLBinTypes(object):
    s8 = "s8"
    u8 = "u8"
    s16 = "s16"
    u16 = "u16"
    s32 = "s32"
    u32 = "u32"
    s64 = "s64"
    u64 = "u64"
    ip4 = "ip4"
    time = "time"
    str = "str"


def e_type(_type, count: Optional[int] = None) -> Dict[str, str]:
    result = {"__type": _type}
    if count is not None:
        result["__count"] = str(count)
    return result


def get_xml_tag(xml: etree) -> str:
    return str(xml.tag)


def get_xml_attrib(xml: etree, name: str) -> str:
    return str(xml.attrib[name]) if name in xml.attrib else "None"


def format_date(timestamp: Optional[int]) -> str:
    if timestamp is None:
        return "None"

    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")
