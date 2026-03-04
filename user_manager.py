"""
User Manager Module
Handles user preferences, saved topics, and search history.
Persists to user_preferences.json.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any


class UserManager:
    """Manages user preferences and search history."""
    
    DEFAULT_PREFS = {
        "saved_topics": [],
        "history": [],
        "settings": {
            "language": "en",
            "page_size": 10
        }
    }
    
    def __init__(self, prefs_file: str = "user_preferences.json"):
        """
        Initialize user manager.
        
        Args:
            prefs_file: Path to preferences JSON file
        """
        self.prefs_file = prefs_file
        self._ensure_prefs_file()
    
    def _ensure_prefs_file(self) -> None:
        """Create preferences file if it doesn't exist."""
        if not os.path.exists(self.prefs_file):
            self.save_prefs(self.DEFAULT_PREFS.copy())
            print(f"📝 Created preferences file: {self.prefs_file}")
    
    def load_prefs(self) -> Dict[str, Any]:
        """
        Load preferences from file.
        
        Returns:
            Dictionary with saved_topics, history, settings
        """
        try:
            with open(self.prefs_file, "r", encoding="utf-8") as f:
                prefs = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Error loading preferences: {e}. Using defaults.")
            return self.DEFAULT_PREFS.copy()
        
        # Ensure all keys exist
        prefs.setdefault("saved_topics", [])
        prefs.setdefault("history", [])
        prefs.setdefault("settings", {})
        
        return prefs
    
    def save_prefs(self, prefs: Dict[str, Any]) -> None:
        """
        Save preferences to file.
        
        Args:
            prefs: Preferences dictionary
        """
        try:
            with open(self.prefs_file, "w", encoding="utf-8") as f:
                json.dump(prefs, f, indent=4, ensure_ascii=False)
            print(f"✅ Preferences saved")
        except IOError as e:
            print(f"❌ Error saving preferences: {e}")
    
    def save_topic(self, topic: str) -> bool:
        """
        Save a topic to favorites.
        
        Args:
            topic: Topic to save
        
        Returns:
            True if saved, False if already exists
        """
        topic = (topic or "").strip()
        if not topic:
            return False
        
        prefs = self.load_prefs()
        
        if topic not in prefs["saved_topics"]:
            prefs["saved_topics"].append(topic)
            self.save_prefs(prefs)
            print(f"⭐ Topic saved: '{topic}'")
            return True
        else:
            print(f"⚠️  Topic already saved: '{topic}'")
            return False
    
    def remove_topic(self, topic: str) -> bool:
        """
        Remove a topic from favorites.
        
        Args:
            topic: Topic to remove
        
        Returns:
            True if removed, False if not found
        """
        topic = (topic or "").strip()
        if not topic:
            return False
        
        prefs = self.load_prefs()
        
        if topic in prefs["saved_topics"]:
            prefs["saved_topics"].remove(topic)
            self.save_prefs(prefs)
            print(f"🗑️  Topic removed: '{topic}'")
            return True
        
        return False
    
    def get_saved_topics(self) -> List[str]:
        """
        Get all saved topics.
        
        Returns:
            List of saved topics
        """
        prefs = self.load_prefs()
        return prefs.get("saved_topics", [])
    
    def add_history_entry(self, topic: str, n_results: int) -> None:
        """
        Add a search to history.
        
        Args:
            topic: Search topic
            n_results: Number of results returned
        """
        prefs = self.load_prefs()
        
        entry = {
            "topic": topic,
            "results": int(n_results),
            "timestamp": datetime.now().isoformat()
        }
        
        prefs["history"].append(entry)
        
        # Keep only last 50 entries
        if len(prefs["history"]) > 50:
            prefs["history"] = prefs["history"][-50:]
        
        self.save_prefs(prefs)
    
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent search history.
        
        Args:
            limit: Maximum number of entries to return
        
        Returns:
            List of history entries (most recent first)
        """
        prefs = self.load_prefs()
        history = prefs.get("history", [])
        
        # Return in reverse order (most recent first)
        return list(reversed(history))[:limit]
    
    def clear_history(self) -> None:
        """Clear all search history."""
        prefs = self.load_prefs()
        prefs["history"] = []
        self.save_prefs(prefs)
        print("🗑️  History cleared")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if key doesn't exist
        
        Returns:
            Setting value
        """
        prefs = self.load_prefs()
        return prefs.get("settings", {}).get(key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """
        Set a setting value.
        
        Args:
            key: Setting key
            value: Setting value
        """
        prefs = self.load_prefs()
        if "settings" not in prefs:
            prefs["settings"] = {}
        
        prefs["settings"][key] = value
        self.save_prefs(prefs)
