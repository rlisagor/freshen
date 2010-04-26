# -*- coding: utf-8 -*-
"""
Partial tests for the parser.
"""
import unittest

from freshen.core import load_language
from freshen.parser import parse_file

class TestParseValidFeature(unittest.TestCase):
    """
    Tests for the parsing of a valid feature.
    """
    
    def setUp(self):
        self.language = load_language('en')

        
    def test_should_parse_feature_file_without_tags_and_without_use_only(self):
        feature = parse_file('resources/valid_no_tags_no_use_only.feature', self.language)
        self.assertEquals(feature.name, 'Independence of the counter.')
        
    
    def test_should_parse_feature_file_with_tags_and_without_use_only(self):
        feature = parse_file('resources/valid_with_tags_no_use_only.feature', self.language)
        self.assertEquals(feature.tags[0], 'one')
        
    
    def test_should_parse_feature_file_without_tags_and_with_use_only(self):
        feature = parse_file('resources/valid_no_tags_with_use_only.feature', self.language)
        self.assertEquals(feature.use_step_defs[0], 'independent_one')
        
        
    def test_should_parse_feature_file_without_tags_and_with_multiple_use_only(self):
        feature = parse_file('resources/valid_no_tags_with_multiple_use_only.feature', self.language)
        self.assertEquals(feature.use_step_defs[0], 'independent_one')
        self.assertEquals(feature.use_step_defs[1], 'te st')
        
        
    def test_should_parse_feature_file_with_tags_and_with_use_only(self):
        feature = parse_file('resources/valid_with_tags_with_use_only.feature', self.language)
        self.assertEquals(feature.tags[0], 'one')
        self.assertEquals(feature.use_step_defs[0], 'independent_one')
        
        
    def test_should_parse_feature_file_with_tags_and_with_multiple_use_only(self):
        feature = parse_file('resources/valid_with_tags_with_multiple_use_only.feature', self.language)
        self.assertEquals(feature.tags[0], 'one')
        self.assertEquals(feature.use_step_defs[0], 'independent_one')
        self.assertEquals(feature.use_step_defs[1], 'te st')
        
        
    def test_should_parse_feature_file_with_unicode_use_only(self):
        feature = parse_file('resources/valid_with_tags_with_unicode_use_only.feature', self.language)
        self.assertEquals(feature.tags[0], 'one')
        self.assertEquals(feature.use_step_defs[0], 'unicodeèédç')
        

    def test_should_parse_feature_file_with_full_unix_path_use_only(self):
        feature = parse_file('resources/valid_with_tags_with_full_unix_path_use_only.feature', self.language)
        self.assertEquals(feature.tags[0], 'one')
        self.assertEquals(feature.use_step_defs[0], '/home/user/independent_one.py')


    def test_should_parse_feature_file_with_full_windows_path_use_only(self):
        feature = parse_file('resources/valid_with_tags_with_full_windows_path_use_only.feature', self.language)
        self.assertEquals(feature.tags[0], 'one')
        self.assertEquals(feature.use_step_defs[0], 'C:\\Documents and Settings\\user\\Desktop\\independent_one.py')
        
        
    def test_should_parse_feature_file_with_use_only_short_form(self):
        feature = parse_file('resources/valid_no_tags_with_use_only_short_form.feature', self.language)
        self.assertEquals(feature.use_step_defs[0], 'independent_one')
        
        
    def test_should_parse_feature_file_with_background_and_no_tags(self):
        feature = parse_file('resources/Befriend_without_tags.feature', self.language)
        self.assertTrue(feature.has_background())
        self.assertEquals(len(feature.background.steps), 2)
        self.assertEquals(len(feature.scenarios), 2)
        
        
    def test_should_parse_feature_file_with_background_and_tags(self):
        feature = parse_file('resources/Befriend_with_tags.feature', self.language)
        self.assertTrue(feature.has_background())
        self.assertEquals(len(feature.background.steps), 2)
        self.assertEquals(len(feature.scenarios), 2)
        self.assertEquals(len(feature.scenarios[0].tags), 1)
        
        
    def test_should_parse_feature_file_with_background_and_title_and_tags(self):
        feature = parse_file('resources/Befriend_with_tags_and_background_title.feature', self.language)
        self.assertTrue(feature.has_background())
        self.assertEquals(len(feature.background.steps), 2)
        self.assertEquals(len(feature.scenarios), 2)
        self.assertEquals(len(feature.scenarios[0].tags), 1)
        

class TestParseValidFeatureInFrench(unittest.TestCase):
    """
    Tests for the parsing of a valid feature in French.
    """
    
    def setUp(self):
        self.language = load_language('fr')

        
    def test_should_parse_feature_file_without_tags_and_without_use_only(self):
        feature = parse_file('resources/valid_no_tags_no_use_only_fr.feature', self.language)
        self.assertEquals(feature.name, "L'indépendance des compteurs.")
        
    
    def test_should_parse_feature_file_with_tags_and_without_use_only(self):
        feature = parse_file('resources/valid_with_tags_no_use_only_fr.feature', self.language)
        self.assertEquals(feature.tags[0], 'un')
        
    
    def test_should_parse_feature_file_without_tags_and_with_use_only(self):
        feature = parse_file('resources/valid_no_tags_with_use_only_fr.feature', self.language)
        self.assertEquals(feature.use_step_defs[0], 'independent_one')
        
        
    def test_should_parse_feature_file_with_use_only_short_form_fr(self):
        feature = parse_file('resources/valid_no_tags_with_use_only_short_form_fr.feature', self.language)
        self.assertEquals(feature.use_step_defs[0], 'independent_one')


    def test_should_parse_feature_file_with_background_and_no_tags_fr(self):
        feature = parse_file('resources/Befriend_without_tags_fr.feature', self.language)
        self.assertTrue(feature.has_background())
        self.assertEquals(len(feature.background.steps), 2)
        self.assertEquals(len(feature.scenarios), 2)


class TestParseValidFeatureInBulgarian(unittest.TestCase):
    """
    Tests for the parsing of a valid feature in Bulgarian.
    
    @note: This test is used to ensure that if a keyword is not translated
           in a given language, then the missing keyword can be spelled in English.
    """
    
    def setUp(self):
        self.language = load_language('bg')

        
    def test_should_parse_feature_file_with_tags_and_with_multiple_use_only(self):
        feature = parse_file('resources/valid_with_tags_with_multiple_use_only_bg.feature', self.language)
        self.assertEquals(feature.tags[0], 'one')
        self.assertEquals(feature.use_step_defs[0], 'independent_one')
        self.assertEquals(feature.use_step_defs[1], 'te st')

    
if __name__ == "__main__":
    unittest.main()
