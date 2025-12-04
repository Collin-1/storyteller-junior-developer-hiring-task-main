"""
Story Builder - Core class for converting match events into story packs
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional


class StoryBuilder:
    """Builds a story pack from match events"""
    
    def __init__(self, weights_path: Optional[Path] = None):
        """Initialize with optional weights configuration"""
        self.weights = self._load_weights(weights_path)
        self.asset_descriptions = self._load_asset_descriptions()
        
    def _load_weights(self, weights_path: Optional[Path]) -> Dict:
        """Load ranking weights from file or use defaults"""
        if weights_path and weights_path.exists():
            with open(weights_path, 'r') as f:
                return json.load(f)
        
        # No weights file provided - must specify one
        raise FileNotFoundError(
            "Weights configuration file is required. "
            "Please provide a weights file using --weights option or ensure weights.example.json exists."
        )
    
    def _load_asset_descriptions(self) -> Dict[str, str]:
        """Load asset descriptions for image matching"""
        asset_path = Path(__file__).parent.parent / 'assets' / 'asset_descriptions.json'
        if asset_path.exists():
            with open(asset_path, 'r') as f:
                data = json.load(f)
                return {asset['filename']: asset['description'] 
                       for asset in data.get('assets', [])}
        return {}
    
    def _calculate_score(self, event: Dict) -> float:
        """Calculate ranking score for an event"""
        event_type = event.get('type', '')
        base_score = self.weights['event_weights'].get(event_type, 0)
        
        # If no exact match, check if 'goal' is in the event type
        if base_score == 0 and 'goal' in event_type.lower():
            base_score = self.weights['event_weights'].get('goal', 0)
        
        # Only include events with meaningful base score
        if base_score <= 0:
            return 0
        
        # Add late minute bonus
        try:
            minute = int(event.get('minute', 0))
        except (ValueError, TypeError):
            minute = 0
            
        if minute >= self.weights['late_minute_bonus_after']:
            base_score += self.weights['late_minute_bonus']
        
        return base_score
    
    def _is_duplicate(self, event1: Dict, event2: Dict) -> bool:
        """Check if two events are duplicates (same minute, type, player)"""
        return (event1.get('minute') == event2.get('minute') and
                event1.get('type') == event2.get('type') and
                event1.get('playerRef1') == event2.get('playerRef1'))
    
    def _find_matching_image(self, event: Dict, player_name: str, used_images: set) -> str:
        """Find best matching image for an event, avoiding duplicates"""
        event_type = event.get('type', '')
        comment = event.get('comment', '').lower()
        event_type_lower = event_type.lower()
        
        best_match = None
        best_score = 0
        
        for filename, description in self.asset_descriptions.items():
            if filename in used_images:
                continue
                
            desc_lower = description.lower()
            score = 0
            
            if player_name and player_name.lower() in desc_lower:
                score += 5
            
            if 'goal' in event_type_lower:
                if 'celtic 1' in comment and '1-0' in desc_lower:
                    score += 10
                elif 'celtic 2' in comment and '2-0' in desc_lower:
                    score += 10
                elif 'celtic 3' in comment and '3-0' in desc_lower:
                    score += 10
                elif 'celtic 4' in comment and '4-0' in desc_lower:
                    score += 10
                
                if 'scores' in desc_lower:
                    score += 3
                if 'goal' in desc_lower:
                    score += 1
            
            if 'penalty' in event_type_lower:
                if 'penalty' in desc_lower:
                    score += 5
                if 'scores a penalty' in desc_lower or 'scores penalty' in desc_lower:
                    score += 3
            
            if 'save' in event_type_lower:
                if 'saved' in desc_lower or 'save' in desc_lower:
                    score += 5
            
            if event_type == 'end 2' and 'full time' in desc_lower:
                score += 10
            
            if score > best_score:
                best_score = score
                best_match = filename
        
        if best_match:
            used_images.add(best_match)
            return f"../assets/{best_match}"
        return "../assets/placeholder.png"
        
    def _get_player_name(self, player_ref: str, squads: Dict) -> str:
        """Get player name from squad data"""
        for team_name in ['celtic', 'kilmarnock']:
            team_squad = squads.get(team_name, {})
            
            if not isinstance(team_squad, dict):
                continue
            
            if 'squad' not in team_squad:
                continue
            
            for squad_item in team_squad['squad']:
                if not isinstance(squad_item, dict):
                    continue
                
                if 'person' not in squad_item:
                    continue
                
                for player in squad_item['person']:
                    if not isinstance(player, dict):
                        continue
                    
                    if player.get('id') != player_ref:
                        continue
                    
                    first = player.get('firstName', '')
                    last = player.get('lastName', '')
                    full_name = f"{first} {last}".strip()
                    return full_name if full_name else player_ref
        
        return player_ref
    
    def _create_headline(self, event: Dict, player_name: str) -> str:
        event_type = event.get('type', '')
        
        if event_type == 'goal':
            return f"GOAL — {player_name}"
        elif event_type == 'penalty goal':
            return f"PENALTY GOAL — {player_name}"
        elif event_type == 'miss':
            return f"CHANCE — {player_name}"
        elif event_type == 'attempt saved':
            return f"SAVE — Shot by {player_name}"
        elif event_type == 'yellow card':
            return f"YELLOW CARD — {player_name}"
        elif event_type == 'penalty won':
            return f"PENALTY WON — {player_name}"
        elif event_type == 'end 2':
            return "FULL TIME"
        elif event_type == 'end 1':
            return "HALF TIME"
        else:
            return f"{event_type.upper()} — {player_name}"
    
    def _create_caption(self, event: Dict) -> str:
        """Create caption from event comment"""
        return event.get('comment', '')
    
    def build_story(self, events_path: Path, squads: Optional[Dict] = None) -> Dict:
        """Build story pack from match events"""
        with open(events_path, 'r') as f:
            data = json.load(f)
        
        match_info = data.get('matchInfo', {})
        messages = data.get('messages', [{}])[0].get('message', [])
        
        contestants = match_info.get('contestant', [])
        home_team = next((c['name'] for c in contestants if c.get('position') == 'home'), 'Home')
        away_team = next((c['name'] for c in contestants if c.get('position') == 'away'), 'Away')
        
        if squads is None:
            squads = self._load_squads()
        
        scored_events = []
        for event in messages:
            score = self._calculate_score(event)
            if score <= 0:
                continue
            
            player_ref = event.get('playerRef1', '')
            player_name = self._get_player_name(player_ref, squads) if player_ref else ''
            
            scored_events.append({
                'event': event,
                'score': score,
                'player_name': player_name
            })
        
        scored_events.sort(key=lambda x: (-x['score'], int(x['event'].get('minute', 0))))
        
        unique_events = []
        seen = set()
        for item in scored_events:
            event = item['event']
            key = (event.get('minute'), event.get('type'), event.get('playerRef1'))
            if key in seen:
                continue
            seen.add(key)
            unique_events.append(item)
        
        max_highlights = self.weights['max_pages'] - 1
        top_events = unique_events[:max_highlights]
        
        top_events.sort(key=lambda x: int(x['event'].get('minute', 0)))
        
        pages = []
        
        cover_image = "../assets/21521990.jpg"
        pages.append({
            "type": "cover",
            "headline": f"{home_team} vs {away_team}",
            "subheadline": f"{match_info.get('competition', {}).get('knownName', 'Match Day')}",
            "image": cover_image
        })
        
        used_images = set()
        for item in top_events:
            event = item['event']
            player_name = item['player_name']
            
            minute = int(event.get('minute', 0))
            image = self._find_matching_image(event, player_name, used_images)
            
            if image == "../assets/placeholder.png":
                continue
            
            headline = self._create_headline(event, player_name)
            caption = self._create_caption(event)
            
            event_type = event.get('type')
            page = {
                "type": "highlight",
                "minute": minute,
                "headline": headline,
                "caption": caption,
                "image": image,
                "explanation": f"{event_type}={self.weights['event_weights'].get(event_type, 0)}"
            }
            
            if minute >= self.weights['late_minute_bonus_after']:
                page["explanation"] += f" + late_bonus={self.weights['late_minute_bonus']}"
            
            pages.append(page)
        
        if len(pages) == 1:
            pages.append({
                "type": "info",
                "headline": "No Key Moments",
                "body": "No significant highlights were detected in this match."
            })
        
        story_id = f"{home_team.lower()}_{away_team.lower()}_{match_info.get('date', 'unknown')}"
        
        try:
            source_path = str(events_path.relative_to(Path.cwd()))
        except ValueError:
            source_path = str(events_path)
        
        pack = {
            "pack_id": story_id,
            "title": f"Top Moments — {home_team} vs {away_team}",
            "pages": pages,
            "metrics": {
                "highlights": len([p for p in pages if p.get('type') == 'highlight']),
                "goals": len([e for e in top_events if 'goal' in e['event'].get('type', '')])
            },
            "source": source_path,
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        
        return pack
    
    def _load_squads(self) -> Dict:
        """Load squad data from JSON files"""
        squads = {'celtic': [], 'kilmarnock': []}
        
        base_path = Path(__file__).parent.parent / 'data'
        
        celtic_path = base_path / 'celtic-squad.json'
        if celtic_path.exists():
            with open(celtic_path, 'r', encoding='utf-8') as f:
                squads['celtic'] = json.load(f)
        
        kilmarnock_path = base_path / 'kilmarnock-squad.json'
        if kilmarnock_path.exists():
            with open(kilmarnock_path, 'r', encoding='utf-8') as f:
                squads['kilmarnock'] = json.load(f)
        
        return squads
