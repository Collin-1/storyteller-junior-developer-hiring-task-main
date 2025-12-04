#!/usr/bin/env python3
"""
Build Story - CLI tool for converting match events into a story pack
"""
import json
import argparse
from pathlib import Path
from story_builder import StoryBuilder


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Build story pack from match events')
    parser.add_argument('--input', default='data/match_events.json', 
                       help='Input events JSON file')
    parser.add_argument('--output', default='out/story.json',
                       help='Output story pack JSON file')
    parser.add_argument('--weights', 
                       help='Weights configuration file')
    
    args = parser.parse_args()
    
    # Setup paths
    base_path = Path(__file__).parent.parent
    events_path = base_path / args.input
    output_path = base_path / args.output
    
    # Handle weights file
    weights_path = None
    if args.weights:
        weights_path = base_path / args.weights
        if not weights_path.exists():
            print(f"Error: Weights file not found: {weights_path}")
            return 1
    else:
        # Check for default weights file
        default_weights = base_path / 'weights.example.json'
        if default_weights.exists():
            weights_path = default_weights
        else:
            # Prompt user for weights file
            print("No weights file specified and weights.example.json not found.")
            weights_input = input("Enter path to weights file: ").strip()
            if not weights_input:
                print("Error: Weights file is required.")
                return 1
            
            weights_path = Path(weights_input)
            if not weights_path.is_absolute():
                weights_path = base_path / weights_path
            if not weights_path.exists():
                print(f"Error: Weights file not found: {weights_path}")
                return 1
    
    # Build story
    builder = StoryBuilder(weights_path)
    story = builder.build_story(events_path)
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write output
    with open(output_path, 'w') as f:
        json.dump(story, f, indent=2)
    
    print(f"Story pack created: {output_path}")
    print(f"  - {len(story['pages'])} pages")
    print(f"  - {story['metrics']['highlights']} highlights")
    print(f"  - {story['metrics']['goals']} goals")


if __name__ == '__main__':
    main()

