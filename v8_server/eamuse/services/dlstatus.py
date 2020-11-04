from lxml.builder import E


class DLStatus(object):
    """
    Handle the DLStatus request.

    It is unknown as to what this does.

    Example:
        <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
        </call>
    """

    # Methods
    PROGRESS = "progress"

    @classmethod
    def progress(cls):
        """
        Example:
            <response>
                <dlstatus expire="600"/>
            </response>
        """
        return E.response(E.dlstatus({"expire": "600"}))
