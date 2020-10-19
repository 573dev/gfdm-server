from lxml.builder import E


class PCBTracker(object):
    """
    Handle the PCBTracker request.

    The only method of note is the "alive" method which returns whether PASELI should be
    active or not for this session.

    Example:
        <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
            <pcbtracker hardid="010074D435AAD895" method="alive" softid=""/>
        </call>
    """

    # We don't support PASELI on GFDM: V8
    PASELI_ACTIVE = False

    # Methods
    ALIVE = "alive"

    @classmethod
    def alive(cls):
        return E.response(E.pcbtracker({"ecenable": "1" if cls.PASELI_ACTIVE else "0"}))
