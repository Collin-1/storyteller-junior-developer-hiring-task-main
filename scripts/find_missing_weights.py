#!/usr/bin/env python3
"""
Find all event types in match_events.json that don't have weights defined
"""
import json
from pathlib import Path
from collections import Counter

def main():
    # Load weights
    weights_path = Path(__file__).parent.parent / 'weights.example.json'
    with open(weights_path, 'r') as f:
        weights = json.load(f)
    
    defined_weights = set(weights.get('event_weights', {}).keys())
    
    # Load match events
    events_path = Path(__file__).parent.parent / 'data' / 'match_events.json'
    with open(events_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    messages = data.get('messages', [{}])[0].get('message', [])
    
    # Collect all event types
    all_event_types = Counter()
    missing_weight_events = []
    
    for event in messages:
        event_type = event.get('type', '')
        all_event_types[event_type] += 1
        
        if event_type and event_type not in defined_weights:
            # Check if it's a goal variant
            is_goal_variant = 'goal' in event_type.lower()
            
            missing_weight_events.append({
                'type': event_type,
                'minute': event.get('minute', ''),
                'comment': event.get('comment', '')[:80],
                'is_goal_variant': is_goal_variant
            })
    
    # Create summary
    missing_types = {}
    for event_type, count in all_event_types.items():
        if event_type not in defined_weights:
            is_goal_variant = 'goal' in event_type.lower()
            missing_types[event_type] = {
                'count': count,
                'is_goal_variant': is_goal_variant,
                'suggested_weight': 5 if is_goal_variant else 0
            }
    
    # Output
    output = {
        'summary': {
            'total_event_types': len(all_event_types),
            'defined_weights': len(defined_weights),
            'missing_weights': len(missing_types)
        },
        'missing_event_types': missing_types,
        'sample_events': missing_weight_events[:20]  # First 20 examples
    }
    
    # Write to file
    output_path = Path(__file__).parent.parent / 'out' / 'missing_weights.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"✓ Found {len(missing_types)} event types without weights")
    print(f"✓ Report saved to: {output_path}")
    print("\nMissing event types:")
    for event_type, info in sorted(missing_types.items(), key=lambda x: -x[1]['count']):
        goal_flag = " [GOAL VARIANT]" if info['is_goal_variant'] else ""
        print(f"  - {event_type}: {info['count']} occurrences{goal_flag}")

if __name__ == '__main__':
    main()
