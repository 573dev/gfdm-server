from lxml import etree

from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.xml.utils import get_xml_attrib, load_xml_template


class List(object):
    """
    Handle the Package List request.

    This is for supporting downloading of updates.
    We do not support this.

    <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
        <package method="list" pkgtype="all"/>
    </call>
    """

    def __init__(self, req: ServiceRequest) -> None:
        self.pkgtype = get_xml_attrib(req.xml[0], "pkgtype")

    def response(self) -> etree:
        return load_xml_template("package", "list")

    def __repr__(self) -> str:
        return f'Package.List<pkgtype="{self.pkgtype}">'
