from lxml.builder import E

from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.xml.utils import get_xml_attrib


class Package(object):
    """
    Handle the Package request.

    This is for supporting downloading of updates. We do not support this.

    Example:
        <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
            <package method="list" pkgtype="all"/>
        </call>
    """

    # Methods
    LIST = "list"

    # PKGTypes
    PKGTYPE_ALL = "all"

    @classmethod
    def list(cls, req: ServiceRequest):
        """
        Example:
            <response>
                <package expire="600"/>
            </response>
        """
        # Grab the pkgtype in case we ever need it
        pkgtype = get_xml_attrib(req.xml[0], "pkgtype")

        if pkgtype == cls.PKGTYPE_ALL:
            response = E.response(E.package({"expire": "600"}))
        else:
            raise Exception(
                "Not sure how to handle this package request. "
                f'pkgtype "{pkgtype}" is unknown for request: {req}'
            )

        return response
