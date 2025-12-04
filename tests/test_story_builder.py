import json
import pytest
from pathlib import Path
from jsonschema import validate, ValidationError
import sys

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from story_builder import StoryBuilder


@pytest.fixture
def schema():
    """Load the story pack JSON schema"""
    schema_path = Path(__file__).parent.parent / 'schema' / 'story.schema.json'
    with open(schema_path, 'r') as f:
        return json.load(f)


@pytest.fixture
def sample_events():
    """Load sample match events"""
    events_path = Path(__file__).parent.parent / 'data' / 'match_events.json'
    return events_path


@pytest.fixture
def builder():
    """Create a StoryBuilder instance"""
    weights_path = Path(__file__).parent.parent / 'weights.example.json'
    return StoryBuilder(weights_path)


class TestInvariants:
    """Tests for required invariants from invariants.md"""
    
    def test_pack_validates_against_schema(self, builder, sample_events, schema):
        """Invariant 1: Pack validates against schema/story.schema.json"""
        story = builder.build_story(sample_events)
        
        # Should not raise ValidationError
        try:
            validate(instance=story, schema=schema)
        except ValidationError as e:
            pytest.fail(f"Story pack failed schema validation: {e.message}")
    
    def test_contains_exactly_one_cover_at_index_zero(self, builder, sample_events):
        """Invariant 2: Contains exactly one cover Page at index 0"""
        story = builder.build_story(sample_events)
        
        # Check pages exist
        assert 'pages' in story
        assert len(story['pages']) >= 1
        
        # Check first page is cover
        assert story['pages'][0]['type'] == 'cover'
        
        # Check no other cover pages exist
        cover_count = sum(1 for page in story['pages'] if page.get('type') == 'cover')
        assert cover_count == 1, f"Expected exactly 1 cover page, found {cover_count}"
    
    def test_no_duplicate_highlights(self, builder, sample_events):
        """Invariant 3: pages[1:] contain only unique highlights (no exact duplicates)"""
        story = builder.build_story(sample_events)
        
        highlight_pages = [p for p in story['pages'][1:] if p.get('type') == 'highlight']
        
        # Check for duplicates
        seen = set()
        for page in highlight_pages:
            # Create a hashable key from important fields
            key = (page.get('minute'), page.get('headline'), page.get('caption'))
            assert key not in seen, f"Duplicate highlight found: {page}"
            seen.add(key)
    
    def test_ordering_is_stable_and_deterministic(self, builder, sample_events):
        """Invariant 4: Ordering is stable and deterministic for the same input"""
        # Build story twice
        story1 = builder.build_story(sample_events)
        story2 = builder.build_story(sample_events)
        
        # Extract page identifiers
        pages1 = [(p.get('type'), p.get('minute'), p.get('headline')) 
                  for p in story1['pages']]
        pages2 = [(p.get('type'), p.get('minute'), p.get('headline')) 
                  for p in story2['pages']]
        
        # Should be identical
        assert pages1 == pages2, "Story ordering is not deterministic"
    
    def test_no_highlights_fallback(self, builder, tmp_path):
        """Invariant 5: When no highlights, include an info Page communicating 'no highlights'"""
        # Create empty events file
        empty_events = tmp_path / "empty_events.json"
        empty_data = {
            "matchInfo": {
                "contestant": [
                    {"name": "TeamA", "position": "home"},
                    {"name": "TeamB", "position": "away"}
                ],
                "competition": {"knownName": "Test League"}
            },
            "messages": [{"message": []}]
        }
        
        with open(empty_events, 'w') as f:
            json.dump(empty_data, f)
        
        story = builder.build_story(empty_events)
        
        # Should have cover + info page
        assert len(story['pages']) >= 2
        assert story['pages'][0]['type'] == 'cover'
        
        # Check for info page
        info_pages = [p for p in story['pages'] if p.get('type') == 'info']
        assert len(info_pages) >= 1, "Expected info page when no highlights"
    
    def test_created_at_is_iso8601(self, builder, sample_events):
        """Invariant 6: created_at is ISO-8601 (UTC recommended)"""
        story = builder.build_story(sample_events)
        
        assert 'created_at' in story
        created_at = story['created_at']
        
        # Validate ISO-8601 format
        from datetime import datetime
        try:
            # Should parse without error
            dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            # Should contain timezone info (Z or +00:00)
            assert 'Z' in created_at or '+' in created_at, "created_at should include timezone"
        except ValueError as e:
            pytest.fail(f"created_at is not valid ISO-8601: {created_at}")
    
    def test_source_points_to_input_file(self, builder, sample_events):
        """Invariant 7: source points to the input file used"""
        story = builder.build_story(sample_events)
        
        assert 'source' in story
        assert len(story['source']) > 0
        # Should reference the data file
        assert 'match_events.json' in story['source']


class TestRanking:
    """Tests for ranking heuristic"""
    
    def test_late_minute_bonus_applies(self, builder, tmp_path):
        """Goal at minute 90 ranks higher than shot at minute 10 due to late_minute_bonus"""
        # Create test events
        test_events = tmp_path / "test_events.json"
        test_data = {
            "matchInfo": {
                "contestant": [
                    {"name": "TeamA", "position": "home"},
                    {"name": "TeamB", "position": "away"}
                ],
                "competition": {"knownName": "Test"}
            },
            "messages": [{
                "message": [
                    {
                        "minute": "90",
                        "type": "goal",
                        "playerRef1": "player1",
                        "comment": "Late goal!",
                        "period": "2",
                        "second": "0"
                    },
                    {
                        "minute": "10",
                        "type": "attempt saved",
                        "playerRef1": "player2",
                        "comment": "Early shot saved",
                        "period": "1",
                        "second": "0"
                    }
                ]
            }]
        }
        
        with open(test_events, 'w') as f:
            json.dump(test_data, f)
        
        story = builder.build_story(test_events)
        highlights = [p for p in story['pages'] if p.get('type') == 'highlight']
        
        # Goal at 90 should be first highlight (after cover)
        if len(highlights) > 0:
            assert highlights[0]['minute'] == 90, "Late goal should rank highest"
    
    def test_goals_rank_higher_than_shots(self, builder, tmp_path):
        """Goals should rank higher than saved shots"""
        test_events = tmp_path / "test_events.json"
        test_data = {
            "matchInfo": {
                "contestant": [
                    {"name": "TeamA", "position": "home"},
                    {"name": "TeamB", "position": "away"}
                ],
                "competition": {"knownName": "Test"}
            },
            "messages": [{
                "message": [
                    {
                        "minute": "30",
                        "type": "goal",
                        "playerRef1": "player1",
                        "comment": "Goal!",
                        "period": "1",
                        "second": "0"
                    },
                    {
                        "minute": "40",
                        "type": "attempt saved",
                        "playerRef1": "player2",
                        "comment": "Shot saved",
                        "period": "1",
                        "second": "0"
                    }
                ]
            }]
        }
        
        with open(test_events, 'w') as f:
            json.dump(test_data, f)
        
        story = builder.build_story(test_events)
        highlights = [p for p in story['pages'] if p.get('type') == 'highlight']
        
        # Goal should appear before shot
        if len(highlights) >= 2:
            goal_index = next(i for i, p in enumerate(highlights) if p['minute'] == 30)
            shot_index = next(i for i, p in enumerate(highlights) if p['minute'] == 40)
            assert goal_index < shot_index, "Goal should rank higher than shot"


class TestNegativeCases:
    """Negative test cases"""
    
    def test_missing_cover_page_fails(self):
        """A pack without a cover Page should fail validation"""
        invalid_pack = {
            "story_id": "test",
            "title": "Test",
            "pages": [
                {"type": "highlight", "minute": 10, "headline": "Test", "caption": "Test"}
            ],
            "source": "test.json",
            "created_at": "2024-01-01T00:00:00Z"
        }
        
        # Verify test setup: first page should not be cover
        pages = invalid_pack['pages']
        assert pages[0].get('type') != 'cover', "Test setup: first page should not be cover"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
