import json
from copy import deepcopy
from enum import IntEnum
from os import path
from translate import Translator
import unicodedata

import requests_html

from classes.Nationality import Nationality, FREE_NATION
from config import FILES_DIR
from util import get_bits

FILES_DIRECTORY = path.join(path.dirname(path.abspath(__file__)), '..', FILES_DIR, '')

BLOCK_LENGTH = 124
DEFAULT_ENCODING = 'utf-8'
NAME_ENCODING = 'utf-16-le'


class PlayerFoot(IntEnum):
    RIGHT = 0
    LEFT = 1


class PlayerInjuryResistance(IntEnum):
    C = 0
    B = 1
    A = 2


class PlayerImprovement(IntEnum):
    FAST = 0x09             # 00001001
    FAST_CONST = 0x33       # 00110011
    NORMAL = 0x37           # 00000011
    NORMAL_COST = 0x0B      # 00001011
    SLOW = 0x08             # 00001000
    SLOW_COST = 0x0A        # 00001010
    DEFAULT = 0x00          # 00000000


class PlayerSide(IntEnum):
    FAVOURITE_FOOT = 0
    OPPOSITE_FOOT = 1
    BOTH = 2


class PlayerFavouritePosition(IntEnum):
    POR =  0
    LIB =  2
    DC  =  3
    TER =  4
    MED =  5
    EB  =  6
    CC  =  7
    CL  =  8
    TRQ =  9
    EA  = 10
    SP  = 11
    P   = 12


class PlayerAllPosition:
    POR : bool = False
    LIB : bool = False
    DC  : bool = False
    TER : bool = False
    MED : bool = True
    EB  : bool = False
    CC  : bool = True
    CL  : bool = False
    TRQ : bool = False
    EA  : bool = False
    SP  : bool = False
    P   : bool = False


class PlayerNameSettings:
    _name: str = 'SLC'
    _shirt_name: str = 'S L C'
    announced_name: bytearray = bytearray(b'\xFF\xFF')  # ID or 0xFF (---)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if type(value) == str:
            self._name = value.encode(NAME_ENCODING)[:30].decode(NAME_ENCODING)
        elif type(value) in [bytes, bytearray]:
            self._name = value[:30].decode(NAME_ENCODING).replace('\x00', '')

    @property
    def shirt_name(self):
        return self._shirt_name

    @shirt_name.setter
    def shirt_name(self, value):
        if type(value) == str:
            self._shirt_name = value.encode(DEFAULT_ENCODING)[:15].decode(DEFAULT_ENCODING)
        elif type(value) in [bytes, bytearray]:
            self._shirt_name = value[:15].decode(DEFAULT_ENCODING).replace('\x00', '')


class PlayerBasicSettings:
    _age: int = 15
    _favourite_foot: int = PlayerFoot.RIGHT  # PlayerFoot
    _injury_resistance: int = PlayerInjuryResistance.B  # PlayerInjuryResistance
    dribbling_style: int = 1
    free_kick_style: int = 1
    penalty_style: int = 1
    goal_kick_style: int = 1
    celebration_1: int = 0
    celebration_2: int = 0
    _improvement: int = PlayerImprovement.NORMAL  # PlayerImprovement

    @property
    def age(self):
        return self._age

    @age.setter
    def age(self, value: int):
        self._age = max(15, min(46, value))

    @property
    def favourite_foot(self):
        return PlayerFoot(self._favourite_foot).name

    @favourite_foot.setter
    def favourite_foot(self, value):
        self._favourite_foot = value

    @property
    def injury_resistance(self):
        return PlayerInjuryResistance(self._injury_resistance).name

    @injury_resistance.setter
    def injury_resistance(self, value: int):
        self._injury_resistance = value

    @property
    def improvement(self):
        return PlayerImprovement(self._improvement).name

    @improvement.setter
    def improvement(self, value: int):
        self._improvement = value


class PlayerPositionSettings:
    _side: int = PlayerSide.BOTH  # PlayerSide
    _favourite: int = PlayerFavouritePosition.MED  # PlayerFavouritePosition
    _all: PlayerAllPosition = PlayerAllPosition()  # PlayerAllPosition

    def __init__(self):
        _all = PlayerAllPosition()

    @property
    def side(self):
        return PlayerSide(self._side).name

    @side.setter
    def side(self, value: PlayerSide):
        self._side = value

    @property
    def favourite(self):
        return PlayerFavouritePosition(self._favourite).name

    @favourite.setter
    def favourite(self, value: PlayerFavouritePosition):
        self._favourite = value

    @property
    def all(self):
        return self._all

    @all.setter
    def all(self, values: dict):
        for key in values.keys():
            try:
                self._all.__getattribute__(key)
                self._all.__setattr__(key, values[key] == 1)
            except AttributeError:
                pass


# class PlayerAppearanceHead:
#     face: bytearray
#     hair: bytearray


class PlayerAppearancePhysique:
    height: int = 180
    weight: int = 70
    # physique: bytearray


# class PlayerAppearanceShoes:
#     s_type: int = 1


class PlayerAppearanceSettings:
    # head: PlayerAppearanceHead = PlayerAppearanceHead()
    physique: PlayerAppearancePhysique = PlayerAppearancePhysique()
    # shoes: int
    # accessories: int

    def __init__(self):
        self.physique = PlayerAppearancePhysique()


class PlayerSkillsSettings:
    offense: int = 70
    defense: int = 70
    body_balance: int = 70
    stamina: int = 70
    top_speed: int = 70
    acceleration: int = 70
    responsiveness: int = 70
    agility: int = 70
    dribble_prec: int = 70
    dribble_speed: int = 70
    short_pass_acc: int = 70
    short_pass_speed: int = 70
    long_pass_acc: int = 70
    long_pass_speed: int = 70
    shot_acc: int = 70
    shot_power: int = 70
    shot_technique: int = 70
    free_kick_acc: int = 70
    swerve: int = 70
    header: int = 70
    jump: int = 70
    technique: int = 70
    aggression: int = 70
    mentality: int = 70
    goalkeeping: int = 70
    teamwork: int = 70
    condition: int = 4  # 1 - 8
    weak_foot_accuracy: int = 4  # 1 - 8
    weak_foot_frequency: int = 4  # 1 - 8


class PlayerSpecialSkillsSettings:
    dribbling: bool = False
    possession: bool = False
    positioning: bool = False
    reaction: bool = False
    playmaker: bool = False
    passing: bool = False
    scoring: bool = False
    one_on_one_shot: bool = False
    post_player: bool = False
    df_positioning: bool = False
    long_shots: bool = False
    side: bool = False
    center: bool = False
    penalties: bool = False
    one_touch_pass: bool = False
    outside_kick: bool = False
    marking: bool = False
    sliding: bool = False
    covering: bool = False
    dc_com: bool = False
    penalty_stopper: bool = False
    one_on_one_stopper: bool = False
    long_throw: bool = False


class PlayerUnknownSettings:
    res_50_51: bytearray = bytearray(b'\x07\x00')
    res_80_b012: int = 0
    res_85: int = 0x37
    res_86_87: bytearray = bytearray(b'\x8E\x10')
    res_88_b7: int = 0
    res_89_b7: int = 0
    res_90_111: bytearray = bytearray(b'\x70\x77\x01\x00\x00\x00\x3E\x00\x00\x00\x17\x00\x34\x13\x21\x77\x77\x77\x77'
                                      b'\x17\x00\x00')
    res_113_b67: int = 0
    res_113_b0: int = 0
    res_114_123: bytearray = bytearray(b'\x00\x00\x60\xDB\xB6\x61\x60\xC3\x86\x6D')


class Player:
    id: int = -1
    _name: PlayerNameSettings
    basic_settings: PlayerBasicSettings
    position: PlayerPositionSettings
    nationality: int = 0x64  # FREE Nation
    appearance: PlayerAppearanceSettings
    _skills: PlayerSkillsSettings
    special_skills: PlayerSpecialSkillsSettings
    club: str

    unknown: PlayerUnknownSettings

    def __init__(self):
        self._name = PlayerNameSettings()
        self.basic_settings = PlayerBasicSettings()
        self.position = PlayerPositionSettings()
        self.appearance = PlayerAppearanceSettings()
        self._skills = PlayerSkillsSettings()
        self.special_skills = PlayerSpecialSkillsSettings()
        self.unknown = PlayerUnknownSettings()

    def __str__(self):
        return self.name

    @property
    def name(self):
        return self._name.name

    @name.setter
    def name(self, value):
        self._name.name = value

    @property
    def shirt_name(self):
        return self._name.shirt_name

    @shirt_name.setter
    def shirt_name(self, value):
        self._name.shirt_name = value

    @property
    def announced_name(self):
        return self._name.announced_name

    @announced_name.setter
    def announced_name(self, value):
        self._name.announced_name = value

    @property
    def skills(self):
        return self._skills

    @skills.setter
    def skills(self, value):
        self._skills = value

    @classmethod
    def from_id(cls, _id: int):

        with open(FILES_DIRECTORY + 'ID00051_000', 'rb') as ID00051_000:
            ID00051_000.seek(BLOCK_LENGTH * _id)
            block = ID00051_000.read(BLOCK_LENGTH)

        p = Player.from_block(block)

        if p is not None:
            p.id = _id

        return p

    @classmethod
    def from_name(cls, name: str):
        return [x for x in Player.get_all() if name.upper() in x.name.upper()]

    @classmethod
    def from_block(cls, block: bytes):
        p = cls()

        if len(block) < BLOCK_LENGTH:
            return None

        # Unknown
        p.unknown.res_50_51 = block[50:52]
        p.unknown.res_80_b012 = get_bits(block[80], 0, 2)
        p.unknown.res_86_87 = block[86:88]
        p.unknown.res_88_b7 = get_bits(block[88], 7)
        p.unknown.res_89_b7 = get_bits(block[89], 7)
        p.unknown.res_90_111 = block[90:112]
        p.unknown.res_113_b67 = get_bits(block[113], 6, 7)
        p.unknown.res_113_b0 = get_bits(block[113], 0)
        p.unknown.res_114_123 = block[114:124]

        # Known
        p.name = block[0:32]
        p.shirt_name = block[32:48]
        p.announced_name = block[48:50]

        p.basic_settings.penalty_style = get_bits(block[52], 5, 7) + 1
        p.basic_settings.free_kick_style = get_bits(block[52], 1, 4) + 1
        p.basic_settings.favourite_foot = get_bits(block[52], 0)

        p.position.favourite = get_bits(block[53], 4, 7)
        p.basic_settings.goal_kick_style = get_bits(block[53], 2, 3) + 1
        p.basic_settings.dribbling_style = get_bits(block[53], 0, 1) + 1

        p.position.all = {x: y for (x, y) in zip(
            ['POR', 'LIB', 'DC', 'TER', 'MED', 'EB', 'CC', 'CL', 'TRQ', 'EA', 'SP', 'P'],
            [get_bits(block[z], 7) for z in range(54, 66)]
        )}

        p.skills.offense                = get_bits(block[54], 0, 6)
        p.skills.defense                = get_bits(block[55], 0, 6)
        p.skills.body_balance           = get_bits(block[56], 0, 6)
        p.skills.stamina                = get_bits(block[57], 0, 6)
        p.skills.top_speed              = get_bits(block[58], 0, 6)
        p.skills.acceleration           = get_bits(block[59], 0, 6)
        p.skills.responsiveness         = get_bits(block[60], 0, 6)
        p.skills.agility                = get_bits(block[61], 0, 6)
        p.skills.dribble_prec           = get_bits(block[62], 0, 6)
        p.skills.dribble_speed          = get_bits(block[63], 0, 6)
        p.skills.short_pass_acc         = get_bits(block[64], 0, 6)
        p.skills.short_pass_speed       = get_bits(block[65], 0, 6)
        p.skills.long_pass_acc          = get_bits(block[66], 0, 6)
        p.skills.long_pass_speed        = get_bits(block[67], 0, 6)
        p.skills.shot_acc               = get_bits(block[68], 0, 6)
        p.skills.shot_power             = get_bits(block[69], 0, 6)
        p.skills.shot_technique         = get_bits(block[70], 0, 6)
        p.skills.free_kick_acc          = get_bits(block[71], 0, 6)
        p.skills.swerve                 = get_bits(block[72], 0, 6)
        p.skills.header                 = get_bits(block[73], 0, 6)
        p.skills.jump                   = get_bits(block[74], 0, 6)
        p.skills.teamwork               = get_bits(block[75], 0, 6)
        p.skills.technique              = get_bits(block[76], 0, 6)
        p.skills.aggression             = get_bits(block[77], 0, 6)
        p.skills.mentality              = get_bits(block[78], 0, 6)
        p.skills.goalkeeping            = get_bits(block[79], 0, 6)
        p.skills.weak_foot_frequency    = get_bits(block[80], 3, 5) + 1
        p.skills.weak_foot_accuracy     = get_bits(block[81], 3, 5) + 1
        p.skills.condition              = get_bits(block[81], 0, 2) + 1

        p.special_skills.penalties          = get_bits(block[66], 7) == 1
        p.special_skills.center             = get_bits(block[67], 7) == 1
        p.special_skills.dribbling          = get_bits(block[68], 7) == 1
        p.special_skills.possession         = get_bits(block[69], 7) == 1
        p.special_skills.positioning        = get_bits(block[70], 7) == 1
        p.special_skills.reaction           = get_bits(block[71], 7) == 1
        p.special_skills.playmaker          = get_bits(block[72], 7) == 1
        p.special_skills.passing            = get_bits(block[73], 7) == 1
        p.special_skills.scoring            = get_bits(block[74], 7) == 1
        p.special_skills.one_on_one_shot    = get_bits(block[75], 7) == 1
        p.special_skills.post_player        = get_bits(block[76], 7) == 1
        p.special_skills.df_positioning     = get_bits(block[77], 7) == 1
        p.special_skills.long_shots         = get_bits(block[78], 7) == 1
        p.special_skills.side               = get_bits(block[79], 7) == 1
        p.special_skills.one_on_one_stopper = get_bits(block[82], 7) == 1
        p.special_skills.penalty_stopper    = get_bits(block[82], 6) == 1
        p.special_skills.dc_com             = get_bits(block[82], 5) == 1
        p.special_skills.covering           = get_bits(block[82], 4) == 1
        p.special_skills.sliding            = get_bits(block[82], 3) == 1
        p.special_skills.marking            = get_bits(block[82], 2) == 1
        p.special_skills.outside_kick       = get_bits(block[82], 1) == 1
        p.special_skills.one_touch_pass     = get_bits(block[82], 0) == 1
        p.special_skills.long_throw         = get_bits(block[84], 7) == 1

        p.basic_settings.injury_resistance = get_bits(block[80], 6, 7)

        p.basic_settings.celebration_1 = block[83]
        p.basic_settings.celebration_2 = get_bits(block[84], 0, 6)

        if block[85] in [x.value for x in PlayerImprovement]:
            p.basic_settings.improvement = block[85]
        else:
            p.basic_settings.improvement = PlayerImprovement.DEFAULT
            p.unknown.res_85 = block[85]

        p.appearance.physique.height = get_bits(block[88], 0, 6) + 148
        p.appearance.physique.weight = get_bits(block[89], 0, 6)

        p.nationality = block[112]
        p.basic_settings.age = get_bits(block[113], 1, 5) + 15

        return p

    @classmethod
    def get_all(cls) -> list:
        players = []
        _id = 1

        while True:
            player = Player.from_id(_id)

            if player is None:
                break

            _id += 1
            players.append(player)

        return players

    @staticmethod
    def generate_shirt_name(name: str) -> str:
        if name[1:3] == '. ':
            name = name[3:]

        name = ''.join(
            c for c in unicodedata.normalize('NFD', name) if unicodedata.category(c) != 'Mn' and not c.isdigit()
        )
        name = name.upper()

        if len(name) < 5:
            name = ''.join(c + ' ' for c in name)

        return name

    def get_block(self) -> bytearray:
        res = bytearray(BLOCK_LENGTH)

        # Name
        res[0:32] = (self.name.encode(NAME_ENCODING).ljust(32, b'\x00'))[:32]
        res[32:48] = (self.shirt_name.encode(DEFAULT_ENCODING).ljust(16, b'\x00'))[:16]
        res[48:50] = self.announced_name

        res[50:52] = self.unknown.res_50_51

        res[52] = (self.basic_settings.penalty_style - 1)           * pow(2, 5) + \
                  (self.basic_settings.free_kick_style - 1)         * pow(2, 1) + \
                  PlayerFoot[self.basic_settings.favourite_foot]

        res[53] = (self.basic_settings.goal_kick_style - 1)         * pow(2, 2) + \
                  PlayerFavouritePosition[self.position.favourite]  * pow(2, 4) + \
                  (self.basic_settings.dribbling_style - 1)

        res[54] = (1 if self.position.all.POR else 0)               * pow(2, 7) + \
                  self.skills.offense

        res[55] = (1 if self.position.all.LIB else 0)               * pow(2, 7) + \
                  self.skills.defense

        res[56] = (1 if self.position.all.DC else 0)                * pow(2, 7) + \
                  self.skills.body_balance

        res[57] = (1 if self.position.all.TER else 0)               * pow(2, 7) + \
                  self.skills.stamina

        res[58] = (1 if self.position.all.MED else 0)               * pow(2, 7) + \
                  self.skills.top_speed

        res[59] = (1 if self.position.all.EB else 0)                * pow(2, 7) + \
                  self.skills.acceleration

        res[60] = (1 if self.position.all.CC else 0)                * pow(2, 7) + \
                  self.skills.responsiveness

        res[61] = (1 if self.position.all.CL else 0)                * pow(2, 7) + \
                  self.skills.agility

        res[62] = (1 if self.position.all.TRQ else 0)               * pow(2, 7) + \
                  self.skills.dribble_prec

        res[63] = (1 if self.position.all.EA else 0)                * pow(2, 7) + \
                  self.skills.dribble_speed

        res[64] = (1 if self.position.all.SP else 0)                * pow(2, 7) + \
                  self.skills.short_pass_acc

        res[65] = (1 if self.position.all.P else 0)                 * pow(2, 7) + \
                  self.skills.short_pass_speed

        res[66] = (1 if self.special_skills.penalties else 0)       * pow(2, 7) + \
                  self.skills.long_pass_acc

        res[67] = (1 if self.special_skills.center else 0)          * pow(2, 7) + \
                  self.skills.long_pass_speed

        res[68] = (1 if self.special_skills.dribbling else 0)       * pow(2, 7) + \
                  self.skills.shot_acc

        res[69] = (1 if self.special_skills.possession else 0)      * pow(2, 7) + \
                  self.skills.shot_power

        res[70] = (1 if self.special_skills.positioning else 0)     * pow(2, 7) + \
                  self.skills.shot_technique

        res[71] = (1 if self.special_skills.reaction else 0)        * pow(2, 7) + \
                  self.skills.free_kick_acc

        res[72] = (1 if self.special_skills.playmaker else 0)       * pow(2, 7) + \
                  self.skills.swerve

        res[73] = (1 if self.special_skills.passing else 0)         * pow(2, 7) + \
                  self.skills.header

        res[74] = (1 if self.special_skills.scoring else 0)         * pow(2, 7) + \
                  self.skills.jump

        res[75] = (1 if self.special_skills.one_on_one_shot else 0) * pow(2, 7) + \
                  self.skills.teamwork

        res[76] = (1 if self.special_skills.post_player else 0)     * pow(2, 7) + \
                  self.skills.technique

        res[77] = (1 if self.special_skills.df_positioning else 0)  * pow(2, 7) + \
                  self.skills.aggression

        res[78] = (1 if self.special_skills.long_shots else 0)      * pow(2, 7) + \
                  self.skills.mentality

        res[79] = (1 if self.special_skills.side else 0)            * pow(2, 7) + \
                  self.skills.goalkeeping

        res[80] = PlayerInjuryResistance[self.basic_settings.injury_resistance] * pow(2, 6) + \
                  (self.skills.weak_foot_frequency - 1)             * pow(2, 3) + \
                  self.unknown.res_80_b012

        res[81] = PlayerSide[self.position.side]                    * pow(2, 6) + \
                  (self.skills.weak_foot_accuracy - 1)              * pow(2, 3) + \
                  (self.skills.condition - 1)

        res[82] = self.special_skills.one_on_one_stopper            * pow(2, 7) + \
                  self.special_skills.penalty_stopper               * pow(2, 6) + \
                  self.special_skills.dc_com                        * pow(2, 5) + \
                  self.special_skills.covering                      * pow(2, 4) + \
                  self.special_skills.sliding                       * pow(2, 3) + \
                  self.special_skills.marking                       * pow(2, 2) + \
                  self.special_skills.outside_kick                  * pow(2, 1) + \
                  self.special_skills.one_touch_pass

        res[83] = self.basic_settings.celebration_1

        res[84] = self.special_skills.long_throw                    * pow(2, 7) + \
                  self.basic_settings.celebration_2

        tmp = PlayerImprovement[self.basic_settings.improvement]
        res[85] = tmp if tmp else self.unknown.res_85

        res[86:88] = self.unknown.res_86_87

        res[88] = self.unknown.res_88_b7 * pow(2, 7) + \
                  self.appearance.physique.height - 148

        res[89] = self.unknown.res_89_b7 * pow(2, 7) + \
                  self.appearance.physique.weight

        res[90:112] = self.unknown.res_90_111

        res[112] = self.nationality

        res[113] = self.unknown.res_113_b67 * pow(2, 6) + \
                   (self.basic_settings.age - 15) * pow(2, 1) + \
                   self.unknown.res_113_b0

        res[114:124] = self.unknown.res_114_123

        return res

    def add(self):
        with open(FILES_DIRECTORY + 'ID00051_000', 'rb+') as ID00051_000:
            content = ID00051_000.read()
            _id = len(content) // BLOCK_LENGTH

            ID00051_000.seek(_id * BLOCK_LENGTH)
            ID00051_000.write(self.get_block())

            self.id = _id
            return _id

    def save(self):
        if self.id > 0:
            with open(FILES_DIRECTORY + 'ID00051_000', 'rb+') as ID00051_000:
                ID00051_000.seek(self.id * BLOCK_LENGTH)

                if ID00051_000.read(BLOCK_LENGTH) != b'':
                    ID00051_000.seek(self.id * BLOCK_LENGTH)
                    ID00051_000.write(self.get_block())
                    return self.id

        self.add()

    @staticmethod
    def remove_last(n: int = 1):
        with open(FILES_DIRECTORY + 'ID00051_000', 'rb') as ID00051_000:
            content = ID00051_000.read()

        n_players = len(content) // BLOCK_LENGTH

        with open(FILES_DIRECTORY + 'ID00051_000', 'wb') as ID00051_000:
            ID00051_000.write(content[:max(0, (n_players - n)) * BLOCK_LENGTH])

    def update_from_pes_master(self) -> bool:
        session = requests_html.HTMLSession()
        results_page = session.get('https://www.pesmaster.com/it/pes-2021/', params={'q': self.name})

        # Se apre direttamente la pagina
        if results_page.html.find('.content-container'):
            players = [(from_pes_master(results_page, self), results_page.url)]

        else:
            results_container = results_page.html.find('.player-card-container', first=True)

            if not results_container:
                return False

            results_cards = results_container.find('.player-card')
            players = []

            for c in results_cards:
                player_page = session.get([*c.absolute_links][0])

                info_container = player_page.html.find('table.player-info > tbody > tr')

                card_type = [x.find('td')[1].text for x in info_container if x.find('td', first=True).text == 'Tipo'][0]

                if card_type != 'Predefinito':
                    continue

                player = (from_pes_master(player_page, self), player_page.url)

                c1 = player[0].nationality == self.nationality
                c2 = player[0].basic_settings.age >= self.basic_settings.age

                if c1 and c2:
                    players.append(player)

            del player

        if len(players) == 0:
            return False

        if len(players) == 1:
            player = players[0]

        else:
            print()
            print(f'Risultati per {self.name}:')
            for i in range(len(players)):
                print(' | '.join([
                    f'{i:3}',
                    f'{players[i][0].name}',
                    f'{players[i][1]}'
                ]))
            print()

            while True:
                try:
                    x = int(
                        input(
                            'Inserisci il valore corrispondente al giocatore che vuoi aggiungere (-1 per annullare): ')
                    )

                    if -1 <= x < len(players):
                        print()
                        break

                except ValueError:
                    pass

            if x == -1:
                return False

            player = players[x]

        self = player[0]
        return True

    def clean_name(self) -> str:
        if '. ' == self.name[1:3]:
            return self.name[3:]

        return self.name

    def update(self):
        session = requests_html.HTMLSession()

        results_json = session.get('https://www.pes6.es/stats/api/players.php', params={'str': self.clean_name()})
        json_dec = json.JSONDecoder()
        results = json_dec.decode(results_json.text)

        if self.name[1:3] == '. ' and len(results) > 1:
            results = [r for r in results if r['value'][0] == self.name[0]]

        if len(results) == 0:
            return False

        if len(results) == 1:
            so_fifa_id = results[0]['soFifaId']

        else:
            print(f'\nRisultati per {self.name}', f'({self.club})' if self.club else '', ':')
            for i in range(len(results)):
                print(' | '.join([
                    f'{i:3}',
                    f'{results[i]["value"]:40}',
                    f'{results[i].get("team") or "Free"}'
                ]))
            print()

            while True:
                try:
                    x = int(
                        input(
                            'Inserisci il valore corrispondente al giocatore che vuoi aggiungere (-1 per annullare): ')
                    )

                    if -1 <= x < len(results):
                        print()
                        break

                except ValueError:
                    pass

            if x == -1:
                return False

            so_fifa_id = results[x]['soFifaId']

        player_json = session.get(
            'https://www.pes6.es/stats/api/statsBySoFifaId.php',
            params={'soFifaId': so_fifa_id}
        )

        self = from_pes6es(json_dec.decode(player_json.text), self)
        return True


def from_pes6es(obj: dict, player: Player = None) -> Player:
    player = Player() if player is None else deepcopy(player)

    translator = Translator(to_lang="it")
    player.nationality = Nationality.from_name(translator.translate(obj.get('nationality')))

    # TODO: Substitute name with initial letter
    # player.name = obj.get('name')

    player.appearance.physique.height = obj.get('height')
    player.appearance.physique.weight = obj.get('weight')

    player.basic_settings.age = obj.get('age')
    player.basic_settings.injury_resistance = PlayerInjuryResistance[obj.get('injury tolerance')]
    player.basic_settings.favourite_foot = PlayerFoot.LEFT if obj.get('foot') == 'L' else PlayerFoot.RIGHT
    player.basic_settings.free_kick_style = obj['free kick style']
    player.basic_settings.goal_kick_style = obj['drop kick style']
    player.basic_settings.dribbling_style = obj['dribbling style']
    player.basic_settings.penalty_style = obj['penalty style']

    player.skills.offense = obj['attack']
    player.skills.defense = obj['defence']
    player.skills.body_balance = obj['balance']
    player.skills.stamina = obj['stamina']
    player.skills.top_speed = obj['speed']
    player.skills.acceleration = obj['acceleration']
    player.skills.responsiveness = obj['response']
    player.skills.agility = obj['agility']
    player.skills.dribble_prec = obj['dribble accuracy']
    player.skills.dribble_speed = obj['dribble speed']
    player.skills.short_pass_acc = obj['short pass accuracy']
    player.skills.short_pass_speed = obj['short pass speed']
    player.skills.long_pass_acc = obj['long pass accuracy']
    player.skills.long_pass_speed = obj['long pass speed']
    player.skills.shot_acc = obj['shot accuracy']
    player.skills.shot_power = obj['shot power']
    player.skills.shot_technique = obj['shot technique']
    player.skills.free_kick_acc = obj['free kick accuracy']
    player.skills.swerve = obj['swerve']
    player.skills.header = obj['heading']
    player.skills.jump = obj['jump']
    player.skills.technique = obj['technique']
    player.skills.aggression = obj['aggression']
    player.skills.mentality = obj['mentality']
    player.skills.goalkeeping = obj['gk skills']
    player.skills.teamwork = obj['team work']
    player.skills.condition = obj['condition']
    player.skills.weak_foot_accuracy = obj['weak foot accuracy']
    player.skills.weak_foot_frequency = obj['weak foot frequency']

    positions_dict = {
        'GK' : 'POR',
        'SW' : 'LIB',
        'CB' : 'DC',
        'CBT': 'DC',
        'SB' : 'TER',
        'DM' : 'MED',
        'WB' : 'EB',
        'CM' : 'CC',
        'AM' : 'TRQ',
        'SM' : 'CL',
        'WF' : 'EA',
        'SS' : 'SP',
        'CF' : 'P',
        'ST' : 'P'
    }

    player.position.favourite = positions_dict[obj['position_prefered_team']]
    player.position.all = {positions_dict[pos]: True for pos in obj['positions']}

    if obj['side'] == 'B':
        player.position.side = PlayerSide.BOTH
    elif obj['side'] == obj['foot']:
        player.position.side = PlayerSide.FAVOURITE_FOOT
    else:
        player.position.side = PlayerSide.OPPOSITE_FOOT

    special_skills = [sp_ability.lower() for sp_ability in obj['special abilities']]
    player.special_skills.penalties = 'penalties' in special_skills
    player.special_skills.center = 'centre' in special_skills
    player.special_skills.dribbling = 'dribbling' in special_skills
    player.special_skills.possession = 'tactical dribble' in special_skills
    player.special_skills.positioning = 'positioning' in special_skills
    player.special_skills.reaction = 'reaction' in special_skills
    player.special_skills.playmaker = 'playmaking' in special_skills
    player.special_skills.passing = 'passing' in special_skills
    player.special_skills.scoring = 'scoring' in special_skills
    player.special_skills.one_on_one_shot = '1-1 scoring' in special_skills
    player.special_skills.post_player = 'post player' in special_skills
    player.special_skills.df_positioning = 'd-line control' in special_skills
    player.special_skills.long_shots = 'middle shooting' in special_skills
    player.special_skills.side = 'side' in special_skills
    player.special_skills.one_on_one_stopper = '1-on-1 stopper' in special_skills
    player.special_skills.penalty_stopper = 'penalty stopper' in special_skills
    player.special_skills.dc_com = ''
    player.special_skills.covering = 'covering' in special_skills
    player.special_skills.sliding = 'sliding' in special_skills
    player.special_skills.marking = 'marking' in special_skills
    player.special_skills.outside_kick = 'outside' in special_skills
    player.special_skills.one_touch_pass = '1-touch pass' in special_skills
    player.special_skills.long_throw = 'long throw' in special_skills

    # Other values:
    # team, number_team, number_selection, contract_valid_until,
    # skin_color, face_type, preset_face, body_type
    # number_classic

    return player


def from_pes_master(player_page, player: Player = None) -> Player:
    player = Player() if player is None else deepcopy(player)

    info_container = player_page.html.find('table.player-info > tbody > tr')
    positions_container = player_page.html.find('.player-positions-new', first=True)
    skills_blocks = player_page.html.find('.stats-block')
    skills_container = player_page.html.find('.stats-block table.player-stats-modern > tbody > tr')
    special_skills_container = player_page.html.find('.player-index-list > li')

    # Name Settings
    player.name = get_player_name(player_page)
    player.shirt_name = Player.generate_shirt_name(player.name)
    player.basic_settings.age = int(
        [x.find('td')[1].text for x in info_container if x.find('td', first=True).text == 'Età'][0]
    )

    # Basic Settings
    fav_foot = [x.find('td')[1].text for x in info_container if x.find('td', first=True).text == 'Piede preferito'][0]
    player.basic_settings.favourite_foot = PlayerFoot.RIGHT if fav_foot == 'Destra' else PlayerFoot.LEFT

    player.basic_settings.injury_resistance = [
                                                  int(x.find('td > span', first=True).text) for x in skills_container
                                                  if x.find('td:not(.stat)', first=True).text == 'Resistenza infortuni'
                                              ][0] - 1

    # Position Settings
    player_pos = {
        'PT': PlayerFavouritePosition.POR,
        'DC': PlayerFavouritePosition.DC,
        'TS': PlayerFavouritePosition.TER,
        'TD': PlayerFavouritePosition.TER,
        'MED': PlayerFavouritePosition.MED,
        'CC': PlayerFavouritePosition.CC,
        'CLS': PlayerFavouritePosition.CL,
        'CLD': PlayerFavouritePosition.CL,
        'TRQ': PlayerFavouritePosition.TRQ,
        'ESA': PlayerFavouritePosition.EA,
        'EDA': PlayerFavouritePosition.EA,
        'SP': PlayerFavouritePosition.SP,
        'P': PlayerFavouritePosition.P
    }

    player.position.favourite = player_pos.get(positions_container.find('.main > span', first=True).text)

    positions = [
        x.find('span', first=True).text for x in
        positions_container.find('.fw-1, .fw-2, .mf-2, .mf-1, .df-2, .df-1, .gk-2, .gk-1')
    ]
    player.position.all = {
        'POR': 1 if 'PT' in positions else 0,
        'LIB': 1 if 'LIB' in positions else 0,
        'DC': 1 if 'DC' in positions else 0,
        'TER': 1 if any(x in positions for x in ['TER', 'TS', 'TD']) else 0,
        'MED': 1 if 'MED' in positions else 0,
        'EB': 1 if 'EB' in positions else 0,
        'CC': 1 if 'CC' in positions else 0,
        'CL': 1 if any(x in positions for x in ['CL', 'CLS', 'CLD']) else 0,
        'TRQ': 1 if 'TRQ' in positions else 0,
        'EA': 1 if any(x in positions for x in ['EA', 'ESA', 'EDA']) else 0,
        'SP': 1 if 'SP' in positions else 0,
        'P': 1 if 'P' in positions else 0
    }

    both_c0 = not any(x in positions for x in ['TS', 'TD', 'CLS', 'CLD', 'ESA', 'EDA'])
    both_c1 = all(x in positions for x in ['TS', 'TD'])
    both_c2 = all(x in positions for x in ['CLS', 'CLD'])
    both_c3 = all(x in positions for x in ['ESA', 'EDA'])

    if both_c0 or both_c1 or both_c2 or both_c3:
        player.position.side = PlayerSide.BOTH
    else:
        fav_l = player.basic_settings.favourite_foot == PlayerFoot.LEFT
        pos_r = player.position.favourite in ['TD', 'CLD', 'EDA']
        pos_l = player.position.favourite in ['TS', 'CLS', 'ESA']

        if (fav_l and pos_l) or not (fav_l and pos_r):
            player.position.side = PlayerSide.FAVOURITE_FOOT
        else:
            player.position.side = PlayerSide.OPPOSITE_FOOT

    # Nationality
    nationality = [x.find('td')[1].text for x in info_container if x.find('td', first=True).text == 'Nazionalità'][0]
    player.nationality = get_nationality_id(nationality)

    # Appearance
    player.appearance.physique.height = int(
        [x.find('td')[1].text for x in info_container if x.find('td', first=True).text == 'Altezza (cm)'][0]
    )

    player.appearance.physique.weight = int(
        [x.find('td')[1].text for x in info_container if x.find('td', first=True).text == 'Peso'][0]
    )

    # Skills
    skills = {x.find('td')[1].text: int(x.find('td > span', first=True).text) for x in skills_container}
    skills['Attacco GEN'] = int(skills_blocks[0].find('h4 > span', first=True).text)
    skills['Dribbling GEN'] = int(skills_blocks[1].find('h4 > span', first=True).text)
    skills['Difesa GEN'] = int(skills_blocks[2].find('h4 > span', first=True).text)
    skills['Passaggio GEN'] = int(skills_blocks[3].find('h4 > span', first=True).text)
    skills['Fisico GEN'] = int(skills_blocks[4].find('h4 > span', first=True).text)

    ovr_gk = int(skills_blocks[5].find('h4 > span', first=True).text)
    skills['Portiere GEN'] = ovr_gk if ovr_gk != 40 else 50

    player.skills.offense = skills['Attacco GEN']
    player.skills.defense = skills['Difesa GEN']
    player.skills.body_balance = skills['Saldo']
    player.skills.stamina = skills['Resistenza']
    player.skills.top_speed = skills['Velocità']
    player.skills.acceleration = skills['Accelerazione']
    player.skills.responsiveness = int(
        0.5 * skills['Accelerazione'] +
        0.5 * skills['Contatto fisico']
    )
    player.skills.agility = int(
        0.33 * skills['Accelerazione'] +
        0.33 * skills['Saldo'] +
        0.34 * skills['Velocità']
    )
    player.skills.dribble_prec = skills['Controllo palla']
    player.skills.dribble_speed = skills['Possesso stretto']
    player.skills.short_pass_acc = skills['Passaggio rasoterra']
    player.skills.short_pass_speed = skills['Passaggio rasoterra']
    player.skills.long_pass_acc = skills['Passaggio alto']
    player.skills.long_pass_speed = skills['Passaggio alto']
    player.skills.shot_acc = skills['Finalizzazione']
    player.skills.shot_power = skills['Potenza di tiro']
    player.skills.shot_technique = int(
        0.5 * skills['Tiro a giro'] +
        0.5 * skills['Finalizzazione']
    )
    player.skills.free_kick_acc = skills['Calci piazzati']
    player.skills.swerve = skills['Tiro a giro']
    player.skills.header = skills['Colpo di testa']
    player.skills.jump = skills['Elevazione']
    player.skills.teamwork = int(
        0.5 * skills['Passaggio GEN'] +
        0.5 * skills['Recupero palla']
    )
    player.skills.technique = int(
        0.5 * skills['Passaggio GEN'] +
        0.5 * skills['Dribbling GEN']
    )
    player.skills.aggression = int(
        0.3 * skills['Aggressività'] +
        0.7 * skills['Comportamento offensivo']
    )

    mentality_dict = {
        PlayerFavouritePosition.POR: [0.2, 0.0, 0.8, 0.0],
        PlayerFavouritePosition.DC: [0.8, 0.1, 0.0, 0.1],
        PlayerFavouritePosition.TER: [0.6, 0.3, 0.0, 0.1],
        PlayerFavouritePosition.MED: [0.6, 0.2, 0.0, 0.2],
        PlayerFavouritePosition.CC: [0.4, 0.4, 0.0, 0.2],
        PlayerFavouritePosition.CL: [0.3, 0.6, 0.0, 0.1],
        PlayerFavouritePosition.TRQ: [0.2, 0.7, 0.0, 0.1],
        PlayerFavouritePosition.EA: [0.1, 0.8, 0.0, 0.1],
        PlayerFavouritePosition.SP: [0.1, 0.8, 0.0, 0.1],
        PlayerFavouritePosition.P: [0.1, 0.9, 0.0, 0.0]
    }

    mentality_array = mentality_dict[PlayerFavouritePosition[player.position.favourite]]

    player.skills.mentality = int(
        mentality_array[0] * skills['Comportamento difensivo'] +
        mentality_array[1] * skills['Comportamento offensivo'] +
        mentality_array[2] * skills['Comportamento PT'] +
        mentality_array[3] * skills['Saldo']
    )

    player.skills.goalkeeping = skills['Portiere GEN']
    player.skills.weak_foot_frequency = skills['Frequenza piede debole']
    player.skills.weak_foot_accuracy = skills['Precisione piede debole']
    player.skills.condition = skills['Forma fisica']

    # Special Skills
    special_skills = [x.text for x in special_skills_container if x.text != '-']
    player.special_skills.penalties = 'Specialista dei rigori' in special_skills
    player.special_skills.center = 'Talio al centro' in special_skills
    player.special_skills.dribbling = any(x in special_skills for x in [
        'Elastico',
        'Finta doppio passo',
        'Finta portoghese',
        'Funambolo',
        'Serpentina',
        'Sombrero'
    ])
    player.special_skills.possession = any(x in special_skills for x in [
        'Opportunista',
        'Taglio alle spalle e giro'
    ])
    player.special_skills.positioning = any(x in special_skills for x in [
        'Astuzia',
        'Onnipresente',
        'Senza palla'
    ])
    player.special_skills.reaction = 'Incontrista' in special_skills
    player.special_skills.playmaker = any(x in special_skills for x in [
        'Classico #10',
        'Fulcro di gioco',
        'Giocatore chiave'
        'No-look',
        'Passaggio filtrante',
        'Regista creativo',
        'Tra le linee'
    ])
    player.special_skills.passing = any(x in special_skills for x in [
        'Doppio tocco',
        'Passaggio a scavalcare',
        'Passaggio calibrato'
    ])
    player.special_skills.scoring = any(x in special_skills for x in [
        'Finalizzazione acrobatica',
        'Opportunista',
        'Tiro di collo',
        'Tiro di prima'
    ])
    player.special_skills.one_on_one_shot = any(x in special_skills for x in [
        'Pallonetto mirato',
        'Rapace dell\'area',
        'Rimbalzo interno'
    ])
    player.special_skills.post_player = 'Collante' in special_skills
    player.special_skills.df_positioning = 'Sviluppo' in special_skills
    player.special_skills.long_shots = any(x in special_skills for x in [
        'Tiratore',
        'Tiri a salire',
        'Tiri a scendere',
        'Tiro da lontano'
    ])
    player.special_skills.side = any(x in special_skills for x in [
        'Ala prolifica',
        'Cross calibrato',
        'Specialista dei cross'
    ])
    player.special_skills.one_on_one_stopper = 'Portiere difensivo' in special_skills
    player.special_skills.penalty_stopper = 'Para-rigori' in special_skills
    player.special_skills.dc_com = any(x in special_skills for x in [
        'Disimpegno acrobatico',
        'Intercettazione'
    ])
    player.special_skills.covering = 'Tornante' in special_skills
    player.special_skills.sliding = 'Spirito combattivo' in special_skills
    player.special_skills.marking = any(x in special_skills for x in [
        'Colpo di testa',
        'Marcatore'
    ])
    player.special_skills.outside_kick = any(x in special_skills for x in [
        'Esterno a giro',
        'Tiri a salire',
        'Tiri a scendere'
    ])
    player.special_skills.one_touch_pass = any(x in special_skills for x in [
        'Colpo di tacco',
        'Passaggio di prima'
    ])
    player.special_skills.long_throw = any(x in special_skills for x in [
        'Rimessa lunga PT',
        'Rimessa profonda PT',
    ])

    # Extra
    player.club = [x.find('td')[1].text for x in info_container if x.find('td', first=True).text == 'Squadra'][0]

    return player


def get_player_name(player_page) -> str:
    info_container = player_page.html.find('table.player-info > tbody > tr')
    real_name = [x.find('td')[1].text for x in info_container if x.find('td', first=True).text == 'Vero Nome']
    name = player_page.html.find('.top-header > span:not(:first-child)', first=True).text

    return real_name[0] if real_name else name


def get_nationality_id(nationality: str) -> int:
    nationalities = Nationality.from_name(nationality)

    if len(nationalities) == 0:
        return FREE_NATION

    if len(nationalities) == 1:
        return nationalities[0].id

    print(f'Sono state trovate {len(nationalities)} nazionalità:')
    print(f'\n'.join(f'{i:3} | {nationalities[i].name}' for i in range(len(nationalities))))
    print()

    while True:
        try:
            x = int(input(
                'Digita il numero corrispondente alla nazionalità che vuoi selezionare (-1 per nessuna nazionalità): '))

            if -1 <= x < len(nationalities):
                break
        except ValueError:
            pass

    return FREE_NATION if x == -1 else nationalities[x].id
