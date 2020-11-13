import logging

from lxml import etree

from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.utils.crc import calculate_crc8
from v8_server.eamuse.xml.utils import get_xml_attrib, load_xml_template
from v8_server.model.user import User


logger = logging.getLogger(__name__)


class Request(object):
    """
    Gametop.Get.Player.Request object
    """

    def __init__(self, root: etree) -> None:
        self.kind = int(root.find("kind").text)
        self.offset = int(root.find("offset").text)
        self.music_nr = int(root.find("music_nr").text)
        self.cabid = int(root.find("cabid").text)

    def __repr__(self) -> str:
        return (
            f"Request<kind = {self.kind}, offset = {self.offset}, "
            f"music_nr = {self.music_nr}, cabid = {self.cabid}>"
        )


class Player(object):
    """
    Gametop.Get.Player object
    """

    def __init__(self, root: etree) -> None:
        self.card = get_xml_attrib(root, "card")
        self.no = int(get_xml_attrib(root, "no"))
        self.refid = root.find("refid").text
        self.request = Request(root.find("request"))

    def __repr__(self) -> str:
        return (
            f'Player<card = "{self.card}", no = {self.no}, refid = "{self.refid}", '
            f"request = {self.request}>"
        )


class Get(object):
    """
    Handle the Gametop.Get request.

    This requests saved user data when using eAmuse.

    <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
        <gametop method="get">
            <player card="use" no="1">
                <refid __type="str">E9D2DD02072F05C5</refid>
                <request>
                    <kind __type="u8">0</kind>
                    <offset __type="u16">0</offset>
                    <music_nr __type="u16">250</music_nr>
                    <cabid __type="u32">1</cabid>
                </request>
            </player>
        </gametop>
    </call>
    """

    def __init__(self, req: ServiceRequest) -> None:
        self.player = Player(req.xml[0].find("player"))

    def __repr__(self) -> str:
        return f"Gametop.Get<player = {self.player}>"

    def response(self) -> etree:
        # Grab user_data
        user = User.from_refid(self.player.refid)
        if user is None:
            raise Exception("User should not be none here")

        user_data = user.user_data

        # Generate history rounds (blank for now)
        history_rounds = ""
        for _ in range(0, 10):
            history_rounds += etree.tostring(
                load_xml_template("gametop", "get.history.round")
            ).decode("UTF-8")

        music_hist_rounds = ""
        for _ in range(0, 20):
            music_hist_rounds += etree.tostring(
                load_xml_template("gametop", "get.music_hist.round")
            ).decode("UTF-8")

        secret_music = user_data.secret_music
        secret_chara = user_data.secret_chara
        tag = calculate_crc8(str(sum(secret_music) + secret_chara))

        args = {
            "secret_music": " ".join(map(str, secret_music)),
            "style": user_data.style,
            "style_2": user_data.style_2,
            "secret_chara": secret_chara,
            "tag": tag,
            "history_rounds": history_rounds,
            "music_hist_rounds": music_hist_rounds,
        }

        return load_xml_template("gametop", "get", args)


# TODO: We haven't ever received a request for rival data, so we can implement this in
# the future
"""
        elif req.method == cls.GAMETOP_GET_RIVAL:
            response = load_xml_template(
                "gametop", "get_rival", {"name": "name", "chara": 0}
            )
        else:
            raise Exception(
                "Not sure how to handle this gametop request. "
                f'method "{req.method}" is unknown for request: {req}'
            )

        return response
"""
