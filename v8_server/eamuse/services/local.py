import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from lxml import etree

from v8_server import db
from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.utils.crc import calculate_crc8
from v8_server.eamuse.xml.utils import fill, get_xml_attrib, load_xml_template
from v8_server.model.song import HitChart
from v8_server.model.user import User, UserAccount


logger = logging.getLogger(__name__)


class Local(object):
    """
    Handle the Local request.

    This request handles most of the game specific requests.
    """

    # Methods
    SHOPINFO = "shopinfo"
    SHOPINFO_REGIST = "regist"

    DEMODATA = "demodata"
    DEMODATA_GET = "get"

    CARDUTIL = "cardutil"
    CARDUTIL_CHECK = "check"
    CARDUTIL_REGIST = "regist"

    GAMEINFO = "gameinfo"
    GAMEINFO_GET = "get"

    GAMEEND = "gameend"
    GAMEEND_REGIST = "regist"

    GAMETOP = "gametop"
    GAMETOP_GET = "get"
    GAMETOP_GET_RIVAL = "get_rival"

    CUSTOMIZE = "customize"
    CUSTOMIZE_REGIST = "regist"

    ASSERT_REPORT = "assert_report"
    ASSERT_REPORT_REGIST = "regist"

    # Not sure about this one yet
    INCREMENT = "increment"

    @classmethod
    def customize(cls, req: ServiceRequest) -> etree:
        if req.method == cls.CUSTOMIZE_REGIST:
            response = load_xml_template("customize", "regist")
        else:
            raise Exception(
                "Not sure how to handle this customize request. "
                f'method "{req.method}" is unknown for request: {req}'
            )

        return response

    @classmethod
    def shopinfo(cls, req: ServiceRequest) -> etree:
        if req.method == cls.SHOPINFO_REGIST:
            response = load_xml_template("shopinfo", "regist")
        else:
            raise Exception(
                "Not sure how to handle this shopinfo request. "
                f'method "{req.method}" is unknown for request: {req}'
            )

        return response

    @classmethod
    def demodata(cls, req: ServiceRequest) -> etree:
        dtfmt = "%Y-%m-%d %H:%M:%S%z"

        if req.method == cls.DEMODATA_GET:
            hitchart_number = int(req.xml[0].find("hitchart_nr").text)
            rank_items = HitChart.get_ranking(hitchart_number)

            # Generate all hitchart data xml
            hitchart_xml_str = ""
            for rank_item in rank_items:
                hitchart_xml_str += etree.tostring(
                    load_xml_template(
                        "demodata", "get.data", {"musicid": rank_item, "last1": 0}
                    )
                ).decode("UTF-8")

            args = {
                "hitchart_nr": hitchart_number,
                "start": datetime.now().strftime(dtfmt),
                "end": datetime.now().strftime(dtfmt),
                "hitchart_data": hitchart_xml_str,
                "division": 14,
                "message": "SenPi's Kickass DrumMania V8 Machine",
            }

            response = load_xml_template("demodata", "get", args)
        else:
            raise Exception(
                "Not sure how to handle this demodata request. "
                f'method "{req.method}" is unknown for request: {req}'
            )

        return response

    @classmethod
    def cardutil(cls, req: ServiceRequest) -> etree:
        if req.method == cls.CARDUTIL_CHECK:
            refid = req.xml[0].find("card/refid").text
            user = User.from_refid(refid)

            new_user = (
                user is None
                or (account := UserAccount.from_userid(user.userid)) is None
            )

            # New User
            args: Dict[str, Any] = {"state": 0}
            drop_children: Optional[Dict[str, List[str]]] = {
                "cardutil/card": [
                    "name",
                    "gdp",
                    "skill",
                    "all_skill",
                    "chara",
                    "syogo",
                    "penalty",
                ],
            }

            # Existing User
            if not new_user and account is not None:
                args = {
                    "state": 2,
                    "name": account.name,
                    "chara": account.chara,
                }
                drop_children = None

            response = load_xml_template(
                "cardutil", "check", args, drop_children=drop_children
            )
        elif req.method == cls.CARDUTIL_REGIST:
            root = req.xml[0].find("data")
            refid = root.find("refid").text
            name = root.find("name").text
            chara = root.find("chara").text
            cardid = root.find("uid").text
            is_succession = root.find("is_succession").text

            user = User.from_refid(refid)
            if user is None:
                raise Exception("This user should theoretically exist here")
            if user.card.cardid != cardid:
                raise Exception(f"Card ID is incorrect: {user.card.cardid} != {cardid}")

            user_account = UserAccount(
                userid=user.userid,
                name=name,
                chara=int(chara),
                is_succession=True if is_succession == "1" else False,
            )
            db.session.add(user_account)
            db.session.commit()

            response = load_xml_template("cardutil", "regist")
        else:
            raise Exception(
                "Not sure how to handle this cardutil request. "
                f'method "{req.method}" is unknown for request: {req}'
            )

        return response

    @classmethod
    def gameinfo(cls, req: ServiceRequest) -> etree:
        if req.method == cls.GAMEINFO_GET:
            # tag is the crc8 checksum of free_music and free_chara
            # I also don't actually know what these free_music/chara values mean
            args = {
                "free_music": 262143,
                "free_chara": 1824,
                "tag": calculate_crc8(str(262143 + 1824)),
                "division": 14,
            }
            response = load_xml_template("gameinfo", "get", args)
        else:
            raise Exception(
                "Not sure how to handle this gameinfo request. "
                f'method "{req.method}" is unknown for request: {req}'
            )

        return response

    @classmethod
    def gametop(cls, req: ServiceRequest) -> etree:
        if req.method == cls.GAMETOP_GET:
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

            secret_music = fill(32)
            secret_chara = 0
            tag = calculate_crc8(
                str(sum(int(x) for x in secret_music.split()) + secret_chara)
            )

            args = {
                "secret_music": secret_music,
                "style": 2097152,
                "secret_chara": secret_chara,
                "tag": tag,
                "history_rounds": history_rounds,
                "music_hist_rounds": music_hist_rounds,
            }

            response = load_xml_template("gametop", "get", args)
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

    @classmethod
    def gameend(cls, req: ServiceRequest) -> etree:
        """
        Handle a GameEnd request.

        For now just save the hitchart data
        """
        dtfmt = "%Y-%m-%d %H:%M:%S%z"

        if req.method == cls.GAMEEND_REGIST:
            # Grab the hitchart data
            hc_root = req.xml[0].find("hitchart")

            for mid in hc_root.findall("musicid"):
                musicid = int(mid.text)
                hc = HitChart(musicid=musicid, playdate=datetime.now())
                logger.debug(f"Saving HitChart: {hc}")
                db.session.add(hc)
            db.session.commit()

            # Just send back a dummy object for now
            gamemode = get_xml_attrib(req.xml[0].find("gamemode"), "mode")
            card = get_xml_attrib(req.xml[0].find("player"), "card")
            no = get_xml_attrib(req.xml[0].find("player"), "no")
            now_time = datetime.now().strftime(dtfmt)

            # Generate history rounds (blank for now)
            history_rounds = ""
            for _ in range(0, 10):
                history_rounds += etree.tostring(
                    load_xml_template("gameend", "regist.history.round")
                ).decode("UTF-8")

            music_hist_rounds = ""
            for _ in range(0, 20):
                music_hist_rounds += etree.tostring(
                    load_xml_template("gameend", "regist.music_hist.round")
                ).decode("UTF-8")

            args = {
                "gamemode": gamemode,
                "player_card": card,
                "player_no": no,
                "now_time": now_time,
                "history_rounds": history_rounds,
                "music_hist_rounds": music_hist_rounds,
            }

            response = load_xml_template("gameend", "regist", args)
        else:
            raise Exception(
                "Not sure how to handle this gameend request. "
                f'method "{req.method}" is unknown for request: {req}'
            )

        return response
