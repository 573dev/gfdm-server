import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from lxml import etree


logger = logging.getLogger(__name__)

FORMAT_VALUE_RE = re.compile(r"\{(.*)\}")


def load_xml_template(
    service: str,
    method: str,
    args: Optional[Dict[str, Any]] = None,
    /,
    drop_attributes: Optional[Dict[str, List[str]]] = None,
    drop_children: Optional[Dict[str, List[str]]] = None,
) -> etree:
    """
    Given a service and a method, load the appropriate XML template and return it

    Args:
        service (str): eAmuse Service Name
        method (str): eAmuse Method Name
        args (Dict[str, Any]): Used for formatting the xml string

    Keyword Args:
        drop_attributes (Optional[Dict[str, List[str]]]) = None: For each xpath str in
            the dict key, remove all attributes listed from that node.
        drop_children (Optional[Dict[str, List[str]]]) = None: For each xpath str in
            the dict key, remove all children nodes listed from that node.

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
        # Put in default args for format strings that we don't have a value for
        # in `args`
        for value in FORMAT_VALUE_RE.findall(xml_str):
            if value not in args:
                args[value] = ""
        xml_str = xml_str.format(**args)

    xml_root = etree.fromstring(xml_str.encode("UTF-8"))

    if drop_attributes is not None:
        for xpath, attributes in drop_attributes.items():
            drop_attributes_from_node(xml_root.find(xpath), attributes)

    if drop_children is not None:
        for xpath, children in drop_children.items():
            drop_children_from_node(xml_root.find(xpath), children)

    return xml_root


def drop_attributes_from_node(element: etree, attributes: List[str]) -> None:
    for attribute in attributes:
        element.attrib.pop(attribute)


def drop_children_from_node(element: etree, children: List[str]) -> None:
    for child in children:
        element.remove(element.find(child))


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
