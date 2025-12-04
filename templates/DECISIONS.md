# DECISIONS

## Heuristic and ranking

The story builder ranks events using a scoring system with two components:

1. **Base weight**: Each event type has a predefined weight (0-5) configured in `weights.example.json`:
   - Goals (including penalty goals): 5 points
   - Saves, penalties won/lost: 3 points  
   - Cards: 1-3 points depending on severity
   - Administrative events (halftime, fulltime): 0 points

2. **Late minute bonus**: Events occurring after minute 75 receive +1 bonus point to capture dramatic moments near the end of matches.

Events are ranked by score (descending), then by minute (ascending) for deterministic ordering. The top 6 scoring events become highlights.

**Image matching strategy**: Images are matched to events using a keyword-based scoring system with strict requirements:
- Player name match: +5 points
- Goal events: +10 for score context (1-0, 2-0, etc.), +5 for "scores"/"scoring", +2 for "goal"
- Penalty events: +5 for "penalty" keyword, +5 additional for "scores penalty"
- Save events: +10 for "saved"/"save" keywords

**Minimum score thresholds** ensure contextual relevance:
- Goal events: 8 points minimum (requires player name + score context or keyword)
- Save events: 8 points minimum (MUST contain save keywords, not just player name)
- Non-goal penalty events: 8 points minimum (requires penalty context)
- Other events: 5 points minimum

This prevents mismatches like save events showing goal celebration images. Events without contextually appropriate images are skipped (using placeholder.png triggers skip logic).

**Image deduplication**: A `used_images` set tracks assigned images to ensure each highlight has a unique image.

## Data handling (duplicates, missing fields, out‑of‑order minutes)

**Duplicates**: The data contains duplicate events (same minute, type, player). Deduplication logic uses `_is_duplicate()` to compare minute, type, and playerRef1, keeping only the first occurrence.

**Missing fields**: Player names are looked up from squad files using playerRef1. If a player is not found, the event can still be included but without a player-specific name in the headline.

**Out-of-order minutes**: Events are not assumed to arrive in chronological order. The builder sorts all events by minute before processing to ensure correct ranking.

**Encoding**: Squad files are loaded with UTF-8 encoding to handle special characters in player names (e.g., Arne Engels, Daizen Maeda).

## Pack structure and invariants

The generated story pack follows a strict structure:
1. **Cover page** (index 0): Always present with match title, competition, and cover image
2. **Highlights** (indices 1-6): Top scoring events, ordered by rank then minute
3. **Metadata**: Includes pack_id (team_opponent_date format), metrics (highlight/goal counts), source file, and ISO-8601 timestamp

**Invariants enforced** (tested in `test_story_builder.py`):
- Valid against `story.schema.json`
- Exactly one cover page at index 0
- No duplicate highlights (same minute/type/player)
- Deterministic ordering (same input always produces same output)
- Fallback handling (empty events list produces cover-only pack)
- ISO-8601 timestamps in created_at field
- Source field points to input data file

## What I would do with 2 more hours

1. **Advanced image matching**: Implement ML-based image classification to verify images actually depict the claimed event type, rather than relying solely on text descriptions. This would eliminate edge cases where descriptions are misleading.

2. **Event type taxonomy**: Create a hierarchical event type system (e.g., "goal" parent type with "penalty goal", "own goal", "header goal" subtypes) to simplify weight configuration and matching logic.

3. **Configurable highlight count**: Make the top-6 limit configurable via weights file, allowing different story lengths for different match types (e.g., top 8 for cup finals, top 4 for friendlies).

4. **Multi-match support**: Extend the builder to generate multi-match story packs (e.g., "Weekend Highlights" across multiple games) by combining events from different source files and grouping by match.

5. **Performance optimization**: Add caching for squad lookups and asset descriptions to speed up processing for large datasets or repeated builds.

