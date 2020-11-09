from v8_server.eamuse.xml.utils import load_xml_template


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

    @classmethod
    def list(cls):
        return load_xml_template("package", "list")
