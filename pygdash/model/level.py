from enum import Enum
from base64 import b64decode, urlsafe_b64decode
import zlib
import binascii
import math

# enum for level lengths        
class LevelLength(Enum):
    ALL = '-'
    TINY = 0
    SHORT = 1
    MEDIUM = 2
    LONG = 3
    XL = 4

# enum for level difficulties    
class LevelDifficulty(Enum):
    ALL = '-'
    NA = -1
    EASY = 1
    NORMAL = 2
    HARD = 3
    HARDER = 4
    INSANE = 5
    DEMON = -2
    AUTO = -3
    
# enum for demon difficulties    
class DemonDifficulty(Enum):
    NONE = -1
    EASY = 10
    MEDIUM = 20
    HARD = 30
    INSANE = 40
    EXTREME = 50
    
# enum for level difficulty names  
class LevelDifficultyName(Enum):
    NA = 'N/A'
    EASY = 'Easy'
    NORMAL = 'Normal'
    HARD = 'Hard'
    HARDER = 'Harder'
    INSANE = 'Insane'
    AUTO = 'Auto'
    DEMON = 'Demon'
    
# enum for level songs
class LevelSong(Enum):
    CUSTOM = -1
    STEREO_MADNESS = 0
    BACK_ON_TRACK = 1
    POLARGEIST = 2
    DRY_OUT = 3
    BASE_AFTER_BASE = 4
    CANT_LET_GO = 5
    JUMPER = 6
    TIME_MACHINE = 7
    CYCLES = 8
    XSTEP = 9
    CLUTTERFUNK = 10
    TOE = 11
    ELECTROMAN_ADVENTURES = 12
    CLUBSTEP = 13
    ELECTRODYNAMIX = 14
    HEXAGON_FORCE = 15
    BLAST_PROCESSING = 16
    TOE2 = 17
    GEOMETRICAL_DOMINATOR = 18
    DEADLOCKED = 19
    FINGERDASH = 20
    
class LevelFeatured(Enum):
    NEVER = 0
    UNFEATURED = -1
    FEATURED = 1

# represents filters to be applied when requesting levels from the API
class LevelFilters:
    
    # initializes with optional filters to be applied
    def __init__(self, gdw = False, len_ = LevelLength.ALL, star = False, type_ = 2, epic = False, coins = 0, str_ = '', feature = False, original = False, twoPlayer = False, diff = LevelDifficulty.ALL):
        self.gdw = int(gdw)
        self.len_ = len_
        self.star = int(star)
        self.page = 0
        self.type_ = type_
        self.epic = int(epic)
        self.coins = coins
        self.str_ = str_
        self.feature = int(feature)
        self.original = int(original)
        self.twoPlayer = int(twoPlayer)
        self.diff = diff
        self.demonFilter = DemonDifficulty.NONE
    
    # sets demon difficulty filter - chainable
    # separated since not all levels need to define this
    def setDemonDifficulty(self, diff):
        if not isinstance(diff, DemonDifficulty): raise Exception("setDemonDifficulty called without DemonDifficulty enum as argument!")
        self.demonFilter = diff
        return self
     
    # returns the filter represented as a dictionary for use directly with the API
    def asDict(self):
        return {
            'gdw': self.gdw,
            'len': self.len_.value,
            'star': self.star,
            'page': self.page,
            'type': self.type_,
            'epic': self.epic,
            'coins': self.coins,
            'str': self.str_,
            'feature': self.feature,
            'original': self.original,
            'twoPlayer': self.twoPlayer,
            'diff': self.diff.value,
            'demonFilter': int(self.demonFilter.value / 10)
        }
        
# represents extended data for a level from the download endpoint
class LevelData:

    # placeholder for other uses of the model
    def __init__(self):
        pass
        
    # constructs extended data from the raw input
    def __init__(self, raw):
        self.levelDataEncoded = raw['4']
        self.password = raw['27']
        self.uploadTime = raw['28']
        self.updateTime = raw['29']
        self.extraString = raw['36']
        self.index20 = int(raw['20'])
        self.index21 = int(raw['21'])
        self.index22 = int(raw['22'])
        self.index23 = int(raw['23'])
        self.index24 = int(raw['24'])
        self.index32 = raw['32']
        self.index33 = raw['33']
        self.index34 = raw['34']
        # index 26 = base64+inflated string. with some checksums.
        self.index26 = raw['26'].split("#")[0]
     
    # decode helper function     
    def decode_base64_and_inflate(self, b64string):
        decoded_data = urlsafe_b64decode(b64string)
        return zlib.decompress(decoded_data, 47)
        
# represents a single Level
class Level:

    # placeholder for other uses of the model
    def __init__(self):
        pass
    
    # levels are generated from raw KV input
    # if fast is True, do not do potentially expensive operations here
    # if isDL is True, insert the LevelData object as well
    def __init__(self, raw, fast=False, isDL=False):
        self.wasFast = fast
        self.levelID = int(raw['1'])
        self.levelName = raw['2']
        self.version = int(raw['5'])
        self.creatorID = int(raw['6'])
        self.downloads = int(raw['10'])
        self.likes = int(raw['14'])
        self.length = LevelLength(int(raw['15']))
        self.isDemon = raw['17'] != ''
        self.isAuto = raw['25'] != ''
        self.demonDifficulty = DemonDifficulty.NONE if not self.isDemon else DemonDifficulty(int(raw['9']))
        self.diffName = self.diffNameFromNum(int(raw['9']))
        self.desc = ""
        if not self.wasFast: 
            try:
                self.desc = b64decode(raw['3']).decode('ascii') # expensive operation
            except binascii.Error:
                self.desc = ""
        self.track = LevelSong.CUSTOM if raw['35'] != '0' else LevelSong(int(raw['12']))
        self.customSong = int(raw['35'])
        self.gameVersion = self.createdVersionFromNum(int(raw['13']))
        self.stars = int(raw['18'])
        self.featured = LevelFeatured.FEATURED if int(raw['19']) > 0 else LevelFeatured(int(raw['19']))
        self.featureScore = int(raw['19'])
        self.copyOf = int(raw['30'])
        self.isCopy = self.copyOf != 0
        self.twoPlayer = raw['31'] != '0'
        self.coins = int(raw['37'])
        self.coinsVerified = raw['38'] != '0'
        self.starsRequested = int(raw['39'])
        self.isEpic = raw['42'] != '0'
        self.objCount = int(raw['45'])
        self.levelData = None
        if isDL: self.levelData = LevelData(raw)
        
    # tostring
    def __str__(self):
        lvlStr = "{0} ({1} Stars - {2} Requested)".format(self.levelName, self.stars, self.starsRequested)
        if self.featured == LevelFeatured.FEATURED: lvlStr += " ({0}{1})".format(("Epic " if self.isEpic else ""), ("Featured {0}".format(self.featureScore) if self.featured == LevelFeatured.FEATURED else ""))
        
        lvlStr += "\n{0}".format(self.desc)
        
        if self.isDemon: lvlStr += "\nDifficulty: {0}".format(self.demonToName())
        else: lvlStr += "\nDifficulty: {0}".format(self.diffName.value)
        
        return lvlStr
       
    # helper to convert numeric to a LevelDifficultyName
    def diffNameFromNum(self, num):
        if self.isAuto:
            return LevelDifficultyName.AUTO
        elif self.isDemon:
            return LevelDifficultyName.DEMON
        elif num == 0:
            return LevelDifficultyName.NA
        elif num == 10:
            return LevelDifficultyName.EASY
        elif num == 20:
            return LevelDifficultyName.NORMAL
        elif num == 30:
            return LevelDifficultyName.HARD
        elif num == 40:
            return LevelDifficultyName.HARDER
        elif num == 50:
            return LevelDifficultyName.INSANE
     
    # helper to convert numeric to a version string
    def createdVersionFromNum(self, num):
        if num == 10: return "Pre 1.6"
        elif num == 7: return "1.6"
        else: return "{0}.{1}".format(int(num/10), (num%10))
        
    # helper to convert DemonDifficulty to a string
    def demonToName(self):
        if self.demonDifficulty == DemonDifficulty.NONE:
            return "Not Demon"
        elif self.demonDifficulty == DemonDifficulty.EASY:
            return "Easy Demon"
        elif self.demonDifficulty == DemonDifficulty.MEDIUM:
            return "Medium Demon"
        elif self.demonDifficulty == DemonDifficulty.HARD:
            return "Hard Demon"
        elif self.demonDifficulty == DemonDifficulty.INSANE:
            return "Insane Demon"
        elif self.demonDifficulty == DemonDifficulty.EXTREME:
            return "Extreme Demon"
            
# iterable for level results, to fetch beyond current page limit.
class LevelResultSet:

    # initialize with a service to fetch data with
    def __init__(self, service, filters):
        self.service = service
        self.filters = filters
        self.levels = {}
        
    # get item
    def __getitem__(self, index):
        if isinstance(index, tuple): raise Exception("Cannot have a multi-dimensional LevelResultSet!")
        # magic to retrieve as needed
        self._fetch(index)
        return self.levels[index]
        
    # fetches a page as needed
    def _fetch(self, index):
        if index not in self.levels:
            self.filters.page = math.floor(index/10)
            tmplvls = self.service._getLevels(self.filters)
            for i in range(len(tmplvls)):
                self.levels[(self.filters.page*10)+i] = tmplvls[i]