# AI USAGE

My approach to using AI was highly iterative and collaborative, rather than being split into distinct "AI" and "manual" tasks. I often used AI to generate initial implementations—such as the logic for finding matching images—and then intervened manually when the results were not accurate. For instance, the AI's initial image matching algorithm selected incorrect images for goals, so I manually modified the code to prioritize specific scorelines (e.g., matching "1-0" in descriptions) over generic scoring. This workflow involved constant switching between AI generation and manual refinement to ensure the desired results were achieved.

## Where AI helped
- AI (GitHub Copilot) helped parse the README and understand the schema requirements
- Used AI to understand the story.schema.json structure and required fields
- AI assisted with pytest fixture setup and test structure
- AI assisted in  markdown documentation to match 

## Prompts or strategies that worked
-  Ask AI to create a development checklist for me to follow
-  Quick fixes of error when running CLI
-  Design the Algorithm for Image matching 


## Verification steps (tests, assertions, manual checks)
I manually checked that the below we correct:
- Created 10 pytest tests covering all 7 required invariants plus ranking logic
- Every generated story is validated against story.schema.json using jsonschema library
- Verified output story.json has correct structure, no duplicates, proper ordering
- Tested with empty events (no highlights fallback), single event, missing player data
- Ran builder multiple times to ensure identical output with same input
- Loaded generated story.json in preview/index.html to check visual output

## Cases where you chose **not** to use AI and why
- Manually desinged event scoring weights and ranking algorithm to ensure they matched project requirements and were transparent
- Debuging some of the login for image matching, kept geting errors