from pygdash.service import BaseService
from pygdash.model.level import LevelFilters, Level, LevelResultSet

# used to retrieve level data from the API
class LevelService(BaseService):

    # fetches a list of levels, returning a LevelResultSet object
    def listLevels(self, filters = None):
        # default filters
        if filters is None:
            filters = LevelFilters()
        # return a non-populated LevelResultSet
        return LevelResultSet(self, filters)
        
    # gets data on a level by its ID
    def getLevelByID(self, levelID, isGDW = False, inc = 0, extras = 1):
        # options
        levelOpts = {
            'levelID': levelID,
            'gdw': int(isGDW),
            'inc': int(inc),
            'extras': int(extras)
        }
        # send POST request to endpoint
        response = self.post("downloadGJLevel22.php", levelOpts)
        return Level(self._getKVData(response), isDL=True)
        
    # helper to get daily level
    def getDailyLevel(self):
        return self.getLevelByID(-1)
        
    # helper to get weekly demon
    def getWeeklyDemon(self):
        return self.getLevelByID(-2)
    
    # internal method to get a list of levels with filters applied        
    def _getLevels(self, filters):
        # send POST request to endpoint
        response = self.post("getGJLevels21.php", filters.asDict())
        # process response
        # sections separated by #
        all_data = response.split("#")
        # count/page params
        cdata = all_data[3].split(":")
        offset = cdata[1]
        count = cdata[0]
        numPerPage = cdata[2]
        # level info
        levels = all_data[0].split("|")
        # output list
        results = []
        for level in levels:
            # convert to kv pairs
            ldatakv = self._getKVData(level)
            # generate level object
            lobj = Level(ldatakv)
            # push
            results.append(lobj)
            
        return results
        
    # helper func to process the GD API response
    def _getKVData(self, raw):
        data = raw.split(":")
        # generate kv pairs
        datakv = {}
        i = 0
        while i < len(data):
            datakv[data[i]] = data[i+1]
            i += 2
        return datakv