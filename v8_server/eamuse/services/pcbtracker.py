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
        """
        Example (if Paseli is not active):
            <response>
                <pcbtracker ecenable="0"/>
            </response>

        Potentially if Paseli is active, the response might look like so:
            <response>
                <pcbtracker time="" limit="" ecenable="1" eclimit=""/>
            </response>

        I am unsure what the `time`, `limit`, and `eclimit` responses would be.
        """
        return E.response(E.pcbtracker({"ecenable": "1" if cls.PASELI_ACTIVE else "0"}))
