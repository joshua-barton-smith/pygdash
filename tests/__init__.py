from pygdash.service import BaseService
from pygdash.service.level import LevelService

from pygdash.model.level import LevelFilters, LevelFeatured, LevelDifficulty, LevelDifficultyName, DemonDifficulty

import unittest

# confirm BaseService
class TestBaseService(unittest.TestCase):

    def setUp(self):
        self.service = BaseService()
        
    def test_setters(self):
        self.service.setVersions('123', '456')
        self.service.setSecret('abcdefg')
        self.assertEqual(self.service.gameVersion, '123')
        self.assertEqual(self.service.binaryVersion, '456')
        self.assertEqual(self.service.secret, 'abcdefg')
        
    def test_post(self):
        self.service.setSecret('abcdefg')
        with self.assertRaises(Exception):
            self.service.post("downloadGJLevel22.php", {})

# test the LevelService methods
class TestLevelService(unittest.TestCase):
    
    def setUp(self):
        self.service = LevelService()
        
    def test_listall(self):
        results = self.service.listLevels()
        self.assertEqual(results[0].stars, 2)
        self.assertEqual(results[0].featured, LevelFeatured.FEATURED)
        self.assertEqual(results[0].diffName, LevelDifficultyName.EASY)
        
    def test_listfiltered(self):
        filters = LevelFilters(diff = LevelDifficulty.DEMON)
        results = self.service.listLevels(filters = filters)
        self.assertEqual(results[0].stars, 10)
        self.assertEqual(results[0].featured, LevelFeatured.FEATURED)
        self.assertEqual(results[0].diffName, LevelDifficultyName.DEMON)
        self.assertEqual(results[0].demonDifficulty, DemonDifficulty.EASY)
        
if __name__ == '__main__':
    unittest.main()