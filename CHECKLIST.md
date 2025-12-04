# Project Completion Checklist

## Core Requirements
- [x] Script/service converts `data/match_events.json` to `out/story.json`
- [x] Output follows `schema/story.schema.json` structure
- [x] Pack includes cover page
- [x] Pack includes N highlights chosen by heuristic
- [x] Stable ordering (deterministic for same input)
- [x] No exact duplicates in highlights
- [x] All required fields present
- [x] Fallback for no highlights (info page)
- [x] Preview works: `preview/index.html` can load `out/story.json`

## Testing Requirements (Minimum 3 Tests)
- [x] Test 1: Pack validates against schema
- [x] Test 2: Exactly one cover page at index 0
- [x] Test 3: No duplicate highlights
- [x] Test 4: Stable and deterministic ordering
- [x] Test 5: No highlights fallback works
- [x] Test 6: `created_at` is ISO-8601
- [x] Test 7: `source` points to input file
- [x] Test 8: Late minute bonus applies correctly
- [x] Test 9: Goals rank higher than shots
- [x] Test 10: Missing cover page fails validation

## Invariants from `tests/invariants.md`
- [x] Pack validates against `schema/story.schema.json`
- [x] Contains exactly one cover page at index 0
- [x] Pages contain only unique highlights (no duplicates)
- [x] Ordering is stable and deterministic
- [x] No highlights scenario includes info page
- [x] `created_at` is ISO-8601 (UTC)
- [x] `source` points to input file

## Documentation
- [x] `DECISIONS.md` completed with heuristic and ranking details
- [x] `DECISIONS.md` explains data handling (duplicates, missing fields)
- [x] `DECISIONS.md` describes pack structure and invariants
- [x] `AI_USAGE.md` completed with prompts and strategies
- [x] `AI_USAGE.md` includes verification steps
- [x] `AI_USAGE.md` explains where AI was not used

## Optional Stretch Goals
- [x] Tunable ranking with `weights.json`
- [x] Page explanations showing score calculation
- [x] Asset matching using `/assets` descriptions
- [x] Smart image selection based on event context
- [ ] LLM-enhanced captions with factual checking
- [ ] Enhanced preview UX beyond defaults

## Code Quality
- [x] Code is clean and readable
- [x] No nested for loops
- [x] Flattened if statements
- [x] No meta-comments
- [x] Proper error handling
- [x] Type safety checks
- [x] All tests passing (10/10)

## File Structure
- [x] `data/match_events.json` exists
- [x] `data/celtic-squad.json` exists
- [x] `data/kilmarnock-squad.json` exists
- [x] `assets/asset_descriptions.json` exists
- [x] `out/story.json` generated successfully
- [x] `schema/story.schema.json` exists
- [x] `preview/index.html` works
- [x] `weights.example.json` configured
- [x] Tests in `tests/test_story_builder.py`

