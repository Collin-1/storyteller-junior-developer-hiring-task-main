# Story Builder

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Build the story pack:**
   ```bash
   python scripts/build_story.py
   ```

3. **Run tests:**
   ```bash
   pytest tests/test_story_builder.py -v
   ```

4. **Preview the story:**
   - Open `preview/index.html` in your browser
   - Click "Load pack.json" and select `out/story.json`

## Usage

### Basic Usage
```bash
python scripts/build_story.py
```

This will read `data/match_events.json` and output `out/story.json`.

### Custom Options
```bash
python scripts/build_story.py \
  --input data/match_events.json \
  --output out/story.json \
  --weights weights.example.json
```

## How It Works

1. **Event Scoring**: Different event types receive different base scores (goals=5, saves=3, cards=1-3)
2. **Late Minute Bonus**: Events after minute 75 get +1 bonus for dramatic effect
3. **Ranking**: Events sorted by score (descending), then minute (ascending) for determinism
4. **Deduplication**: Events with same minute+type+player are deduplicated
5. **Page Generation**: Top 6 events become highlight pages, plus a cover page

## Testing

All 10 tests pass, covering:
- ✓ Schema validation
- ✓ Exactly one cover page at index 0
- ✓ No duplicate highlights
- ✓ Deterministic ordering
- ✓ No highlights fallback (info page)
- ✓ ISO-8601 timestamps
- ✓ Source tracking
- ✓ Late minute bonus logic
- ✓ Event ranking by type

Run tests with:
```bash
pytest tests/test_story_builder.py -v
```

## Output Structure

The generated `story.json` contains:
- **pack_id**: Unique identifier
- **title**: Match title
- **pages**: Array of cover, highlight, or info pages
- **metrics**: Quick stats (highlights count, goals count)
- **source**: Path to input data
- **created_at**: ISO-8601 timestamp

See `out/story.json` for example output.
