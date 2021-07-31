import unicodedata
from enum import IntEnum
from os import path

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

    unknown: PlayerUnknownSettings

    def __init__(self):
        self._name = PlayerNameSettings()
        self.basic_settings = PlayerBasicSettings()
        self.position = PlayerPositionSettings()
        self.appearance = PlayerAppearanceSettings()
        self._skills = PlayerSkillsSettings()
        self.special_skills = PlayerSpecialSkillsSettings()
        self.unknown = PlayerUnknownSettings()

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
        p = Player()

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
