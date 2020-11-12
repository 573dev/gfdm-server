import logging

from lxml import etree

from v8_server.eamuse.services.services import ServiceRequest
from v8_server.eamuse.xml.utils import get_xml_attrib, load_xml_template
from v8_server.utils.convert import int_to_bool as itob


logger = logging.getLogger(__name__)


class SoundOptions(object):
    """
    Shopinfo.Regist.Shop.Testmode.SoundOptions object
    """

    def __init__(self, root: etree) -> None:
        self.volume_bgm = int(root.find("volume_bgm").text)
        self.volume_se_myself = int(root.find("volume_se_myself").text)

    def __repr__(self) -> str:
        return (
            f"SoundOptions<volume_bgm = {self.volume_bgm}, "
            f"volume_se_myself = {self.volume_se_myself}>"
        )


class StandAlone(object):
    """
    Shopinfo.Regist.Shop.Testmode.GameOptions.StandAlone object
    """

    def __init__(self, root: etree) -> None:
        self.difficulty_standard = int(root.find("difficulty_standard").text)
        self.max_stage_standard = int(root.find("max_stage_standard").text)
        self.long_music = int(root.find("long_music").text)

    def __repr__(self) -> str:
        return (
            f"StandAlone<difficulty_standard = {self.difficulty_standard}, "
            f"max_stage_standard = {self.max_stage_standard}, "
            f"long_music = {self.long_music}>"
        )


class Session(object):
    """
    Shopinfo.Regist.Shop.Testmode.GameOptions.Session object
    """

    def __init__(self, root: etree) -> None:
        self.game_joining_period = int(root.find("game_joining_period").text)

    def __repr__(self) -> str:
        return f"Session<game_joining_period = {self.game_joining_period}>"


class GameSettings(object):
    """
    Shopinfo.Regist.Shop.Testmode.GameOptions.GameSettings object
    """

    def __init__(self, root: etree) -> None:
        self.is_shop_close_on = int(root.find("is_shop_close_on").text)

    def __repr__(self) -> str:
        return f"GameSettings<is_shop_close_on = {self.is_shop_close_on}>"


class GameOptions(object):
    """
    Shopinfo.Regist.Shop.Testmode.GameOptions object
    """

    def __init__(self, root: etree) -> None:
        self.stand_alone = StandAlone(root.find("stand_alone"))
        self.session = Session(root.find("session"))
        self.game_settings = GameSettings(root.find("game_settings"))

    def __repr__(self) -> str:
        return (
            f"GameOptions<stand_alone = {self.stand_alone}, session = {self.session}, "
            f"game_settings = {self.game_settings}>"
        )


class CoinOptions(object):
    """
    Shopinfo.Regist.Shop.Testmode.CoinOptions object
    """

    def __init__(self, root: etree) -> None:
        self.coin_slot = int(root.find("coin_slot").text)

    def __repr__(self) -> str:
        return f"CoinOptions<coin_slot = {self.coin_slot}>"


class Bookkeeping(object):
    """
    Shopinfo.Regist.Shop.Testmode.Bookkeeping object
    """

    def __init__(self, root: etree) -> None:
        self.enable = itob(int(root.find("enable").text))

    def __repr__(self) -> str:
        return f"Bookkeeping<enable = {self.enable}>"


class Testmode(object):
    """
    Shopinfo.Regist.Shop.Testmode object
    """

    def __init__(self, root: etree) -> None:
        self.send = itob(int(get_xml_attrib(root, "send")))
        self.sound_options = SoundOptions(root.find("sound_options"))
        self.game_options = GameOptions(root.find("game_options"))
        self.coin_options = CoinOptions(root.find("coin_options"))
        self.bookkeeping = Bookkeeping(root.find("bookkeeping"))

    def __repr__(self) -> str:
        return (
            f"Testmode<send = {self.send}, sound_options = {self.sound_options}, "
            f"game_options = {self.game_options}, coin_options = {self.coin_options}, "
            f"bookkeeping = {self.bookkeeping}>"
        )


class Shop(object):
    """
    Shopinfo.Regist.Shop object
    """

    def __init__(self, root: etree) -> None:
        self.name = root.find("name").text
        self.pref = int(root.find("pref").text)
        self.systemid = root.find("systemid").text
        self.softwareid = root.find("softwareid").text
        self.hardwareid = root.find("hardwareid").text
        self.locationid = root.find("locationid").text
        self.testmode = Testmode(root.find("testmode"))

    def __repr__(self) -> str:
        return (
            f'Shop<name = "{self.name}", pref = {self.pref}, '
            f'systemid = "{self.systemid}", softwareid = "{self.softwareid}", '
            f'hardwareid = "{self.hardwareid}", locationid = "{self.locationid}", '
            f"testmode = {self.testmode}>"
        )


class Regist(object):
    """
    Handle the Shopinfo Regist request.

    Possibly just used to register machine info onto the server.

    <call model="K32:J:B:A:2011033000" srcid="00010203040506070809">
    <shopinfo method="regist">
        <shop>
            <name __type="str">あ</name>
            <pref __type="s8">2</pref>
            <systemid __type="str">00010203040506070809</systemid>
            <softwareid __type="str">012112345679</softwareid>
            <hardwareid __type="str">010074D435AAD895</hardwareid>
            <locationid __type="str">CA-123</locationid>
            <testmode send="1">
                <sound_options>
                    <volume_bgm __type="u8">20</volume_bgm>
                    <volume_se_myself __type="u8">20</volume_se_myself>
                </sound_options>
                <game_options>
                    <stand_alone>
                        <difficulty_standard __type="u8">7</difficulty_standard>
                        <max_stage_standard __type="u8">1</max_stage_standard>
                        <long_music __type="u8">5</long_music>
                    </stand_alone>
                    <session>
                        <game_joining_period __type="u8">15</game_joining_period>
                    </session>
                    <game_settings>
                        <is_shop_close_on __type="u8">0</is_shop_close_on>
                    </game_settings>
                </game_options>
                <coin_options>
                    <coin_slot __type="u8">1</coin_slot>
                </coin_options>
                <bookkeeping>
                    <enable __type="u8">0</enable>
                </bookkeeping>
            </testmode>
        </shop>
    </shopinfo>
    </call>

    """

    def __init__(self, req: ServiceRequest) -> None:
        self.shop = Shop(req.xml[0].find("shop"))

    def __repr__(self) -> str:
        return f"Shopinfo.Regist<shop = {self.shop}>"

    def response(self) -> etree:
        return load_xml_template("shopinfo", "regist")
