"""
Unit tests for fitment feature extraction improvements.

Tests the enhanced parsing functions in fitment_checker.py:
- Thread parsing with tapped hole detection
- Hole pattern parsing with aggregation
- BOM description thread parsing
- Clearance hole detection
- Spatial text grouping
- Multi-page feature aggregation
"""

import pytest
from backend.services.fitment_checker import (
    _parse_threads,
    _parse_hole_patterns,
    _classify_gender,
    ThreadFeature,
    HolePattern,
)


class TestThreadParsing:
    """Tests for _parse_threads() function."""
    
    def test_basic_thread_extraction(self):
        """Test basic thread specification extraction."""
        text = "M8×1.25"
        gender = "male"
        threads = _parse_threads(text, gender)
        
        assert len(threads) == 1
        assert threads[0].nominal == 8.0
        assert threads[0].pitch == 1.25
        assert threads[0].gender == "male"
    
    def test_thread_with_count(self):
        """Test thread extraction with count prefix."""
        text = "4×M8×1.25"
        gender = "male"
        threads = _parse_threads(text, gender)
        
        assert len(threads) == 1
        assert threads[0].count == 4
        assert threads[0].nominal == 8.0
        assert threads[0].pitch == 1.25


class TestHolePatternParsing:
    """Tests for _parse_hole_patterns() function."""
    
    def test_counted_hole_pattern(self):
        """Test extraction of counted hole patterns like 4×Ø8.5."""
        text = "4×Ø8.5"
        part_number = "TEST-01"
        holes = _parse_hole_patterns(text, part_number)
        
        assert len(holes) == 1
        assert holes[0].count == 4
        assert holes[0].diameter == 8.5
        assert holes[0].source == part_number
    
    def test_single_hole_aggregation(self):
        """Test aggregation of individual hole callouts."""
        text = "Ø8.5 Ø8.5 Ø8.5 Ø8.5"
        part_number = "TEST-01"
        holes = _parse_hole_patterns(text, part_number)
        
        assert len(holes) == 1
        assert holes[0].count == 4
        assert holes[0].diameter == 8.5


class TestGenderClassification:
    """Tests for _classify_gender() function."""
    
    def test_male_keywords(self):
        """Test male gender classification from keywords."""
        assert _classify_gender("M8X30 SOC HD CAP SCREW SS") == "male"
        assert _classify_gender("BOLT M10") == "male"
        assert _classify_gender("STUD M12") == "male"
    
    def test_female_default(self):
        """Test female gender as default when no male keywords."""
        assert _classify_gender("BASE PLATE") == "female"
        assert _classify_gender("HOLDING BED") == "female"


# Placeholder for additional test classes
# Will be populated as implementation progresses
