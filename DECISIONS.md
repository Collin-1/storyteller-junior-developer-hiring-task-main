# DECISIONS

## Heuristic and Ranking

### Event Scoring System
- **Configurable weights**: All event types are scored via `weights.example.json` configuration file
- **Key event scores**:
  - Full-time/Half-time (`end 2`/`end 1`): 6 points (highest priority for match structure)
  - Goals (`goal`, `penalty goal`): 5 points
  - Penalty missed: 4 points
  - Saves, penalty won/lost, post hits: 3 points
  - Shots on target, misses, blocked attempts: 2-3 points
  - Yellow cards, corners: 1 point
  - Routine events (substitutions, offside, lineups): 0 points (filtered out)

### Ranking Strategy
- **Primary sort**: By score (descending) - highest impact events first
- **Secondary sort**: By minute (ascending) - stable, deterministic ordering when scores tie
- **Chronological display**: After selecting top events, re-sort by minute for story flow

## Data Handling

### Duplicate Detection
- **Definition**: Events with identical `(minute, type, playerRef1)` tuple
- **Strategy**: Remove duplicates after scoring but before ranking
- **Preservation**: First occurrence kept when duplicates share the same score

### Missing or Malformed Data
- **Missing player names**: 
  - Look up `playerRef1` in Celtic and Kilmarnock squad JSON files
  - Navigate nested structure: `squad[].person[]` to find matching `id`
  - Fallback to `playerRef` string if player not found
- **Missing images**: 
  - Smart matching against asset descriptions using keyword scoring
  - Matches on: player names (+5), event types (goal/penalty/save), score context ("1-0", "2-0")
  - Skip events with no suitable image (placeholder.png)
  - Track used images to prevent duplicates across pages
- **Missing fields**: Use `.get()` with empty string defaults for safe access
- **Out-of-order events**: Process as-is; final ordering determined by score + minute, not input order

### Goal-Specific Image Matching
- **Score-aware matching**: Match "Celtic 1" in comment to "1-0" in asset description
- **Sequential goals**: Different images for 1-0, 2-0, 3-0, 4-0 scorelines
- **Keyword prioritization**: "scores" (+3) preferred over generic "goal" (+1)

## Pack Structure and Invariants

### Cover Page (Index 0)
- **Type**: `cover`
- **Headline**: "{home_team} vs {away_team}"
- **Subheadline**: Competition name from match info
- **Image**: Fixed walkout image (`21521990.jpg` - McGregor with mascots)
- **Guaranteed**: Always present, even with no highlights

### Highlight Pages
- **Required fields**: `type`, `minute`, `headline`, `caption`, `image`, `explanation`
- **Headline format**: "{EVENT_TYPE} — {Player Name}"
- **Caption**: Direct from event comment (already descriptive)
- **Explanation**: Shows scoring breakdown (e.g., "goal=5 + late_bonus=1")
- **Image selection**: Avoids duplicates via `used_images` set

### Fallback Handling
- **No highlights scenario**: Add info page with "No Key Moments" message
- **Prevents**: Empty story packs when no events meet scoring threshold

### Metadata
- **ISO-8601 timestamps**: `created_at` in UTC with 'Z' suffix
- **Source tracking**: Relative path to input file (falls back to absolute if needed)
- **Metrics object**: Counts highlights and goals for quick overview
- **Pack ID**: Format `{home}_{away}_{date}` for unique identification

## What I Would Do With 2 More Hours

   - Add unit tests for individual helper methods
   - Implement property-based testing for ranking stability
   - Add `--strict` mode that fails fast on missing data instead of using fallbacks
   - Add my own documentation
