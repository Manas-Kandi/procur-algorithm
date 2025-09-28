"""Caching and refresh strategies for vendor data scraping."""

from __future__ import annotations

import json
import os
import pickle
import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

from .base_scraper import VendorData


@dataclass
class CacheEntry:
    """Represents a cached data entry."""

    key: str
    data: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    size_bytes: int = 0
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def is_stale(self, max_age_hours: float) -> bool:
        """Check if cache entry is stale based on age."""
        age = datetime.now() - self.created_at
        return age.total_seconds() > (max_age_hours * 3600)

    def mark_accessed(self):
        """Mark entry as accessed."""
        self.access_count += 1
        self.last_accessed = datetime.now()


class CacheManager:
    """Manages caching for vendor data scraping operations."""

    def __init__(self, cache_dir: str = ".cache", max_size_mb: int = 500):
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.cache_dir.mkdir(exist_ok=True)

        # Cache configuration
        self.default_ttl_hours = 24
        self.vendor_data_ttl_hours = 72  # Vendor data can be cached longer
        self.pricing_data_ttl_hours = 12  # Pricing changes more frequently
        self.compliance_data_ttl_hours = 168  # Compliance data changes rarely (1 week)

        # In-memory cache for frequently accessed data
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._memory_cache_max_size = 100

        # Load existing cache index
        self._load_cache_index()

    def _load_cache_index(self):
        """Load cache index from disk."""
        index_file = self.cache_dir / "cache_index.json"
        if index_file.exists():
            try:
                with open(index_file, 'r') as f:
                    index_data = json.load(f)
                    # Convert to CacheEntry objects
                    for key, entry_data in index_data.items():
                        entry = CacheEntry(
                            key=key,
                            data=None,  # Data is loaded on demand
                            created_at=datetime.fromisoformat(entry_data['created_at']),
                            expires_at=datetime.fromisoformat(entry_data['expires_at']) if entry_data.get('expires_at') else None,
                            access_count=entry_data.get('access_count', 0),
                            last_accessed=datetime.fromisoformat(entry_data['last_accessed']) if entry_data.get('last_accessed') else None,
                            size_bytes=entry_data.get('size_bytes', 0),
                            metadata=entry_data.get('metadata', {})
                        )
                        self._memory_cache[key] = entry
            except Exception as e:
                print(f"Failed to load cache index: {e}")

    def _save_cache_index(self):
        """Save cache index to disk."""
        index_file = self.cache_dir / "cache_index.json"
        try:
            index_data = {}
            for key, entry in self._memory_cache.items():
                index_data[key] = {
                    'created_at': entry.created_at.isoformat(),
                    'expires_at': entry.expires_at.isoformat() if entry.expires_at else None,
                    'access_count': entry.access_count,
                    'last_accessed': entry.last_accessed.isoformat() if entry.last_accessed else None,
                    'size_bytes': entry.size_bytes,
                    'metadata': entry.metadata
                }
            with open(index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
        except Exception as e:
            print(f"Failed to save cache index: {e}")

    def _generate_cache_key(self, category: str, operation: str, **kwargs) -> str:
        """Generate a cache key for the given parameters."""
        # Create a deterministic key based on parameters
        key_components = [category, operation]
        for k, v in sorted(kwargs.items()):
            key_components.append(f"{k}={v}")

        key_string = "|".join(key_components)
        # Hash to create shorter, consistent keys
        return hashlib.md5(key_string.encode()).hexdigest()[:16]

    def _get_cache_file_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{cache_key}.cache"

    def _get_ttl_for_operation(self, operation: str) -> float:
        """Get TTL in hours for different operations."""
        ttl_mapping = {
            'vendor_directory': self.vendor_data_ttl_hours,
            'vendor_details': self.vendor_data_ttl_hours,
            'pricing_data': self.pricing_data_ttl_hours,
            'compliance_data': self.compliance_data_ttl_hours,
        }
        return ttl_mapping.get(operation, self.default_ttl_hours)

    def get(self, category: str, operation: str, **kwargs) -> Optional[Any]:
        """Retrieve data from cache."""
        cache_key = self._generate_cache_key(category, operation, **kwargs)

        # Check memory cache first
        if cache_key in self._memory_cache:
            entry = self._memory_cache[cache_key]

            if entry.is_expired():
                self._remove_from_cache(cache_key)
                return None

            # Load data from disk if not in memory
            if entry.data is None:
                entry.data = self._load_from_disk(cache_key)

            if entry.data is not None:
                entry.mark_accessed()
                return entry.data

        return None

    def put(self, category: str, operation: str, data: Any, **kwargs) -> bool:
        """Store data in cache."""
        cache_key = self._generate_cache_key(category, operation, **kwargs)
        ttl_hours = self._get_ttl_for_operation(operation)

        try:
            # Save to disk
            if not self._save_to_disk(cache_key, data):
                return False

            # Calculate size
            size_bytes = self._calculate_size(data)

            # Create cache entry
            entry = CacheEntry(
                key=cache_key,
                data=data,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=ttl_hours),
                size_bytes=size_bytes,
                metadata={
                    'category': category,
                    'operation': operation,
                    'kwargs': kwargs
                }
            )

            # Add to memory cache
            self._memory_cache[cache_key] = entry

            # Manage cache size
            self._manage_cache_size()

            # Save index
            self._save_cache_index()

            return True

        except Exception as e:
            print(f"Failed to cache data: {e}")
            return False

    def _save_to_disk(self, cache_key: str, data: Any) -> bool:
        """Save data to disk."""
        try:
            cache_file = self._get_cache_file_path(cache_key)

            # Use pickle for complex objects, JSON for simple ones
            if isinstance(data, (list, dict)) and self._is_json_serializable(data):
                with open(cache_file, 'w') as f:
                    json.dump(data, f)
            else:
                with open(cache_file, 'wb') as f:
                    pickle.dump(data, f)

            return True
        except Exception as e:
            print(f"Failed to save to disk: {e}")
            return False

    def _load_from_disk(self, cache_key: str) -> Optional[Any]:
        """Load data from disk."""
        try:
            cache_file = self._get_cache_file_path(cache_key)
            if not cache_file.exists():
                return None

            # Try JSON first, then pickle
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, UnicodeDecodeError):
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)

        except Exception as e:
            print(f"Failed to load from disk: {e}")
            return None

    def _is_json_serializable(self, data: Any) -> bool:
        """Check if data is JSON serializable."""
        try:
            json.dumps(data)
            return True
        except (TypeError, ValueError):
            return False

    def _calculate_size(self, data: Any) -> int:
        """Calculate approximate size of data in bytes."""
        try:
            if isinstance(data, str):
                return len(data.encode('utf-8'))
            elif isinstance(data, (list, dict)):
                return len(json.dumps(data).encode('utf-8'))
            else:
                return len(pickle.dumps(data))
        except Exception:
            return 1024  # Default size estimate

    def _manage_cache_size(self):
        """Manage cache size by removing old/unused entries."""
        # Get current cache size
        current_size = sum(entry.size_bytes for entry in self._memory_cache.values())

        if current_size <= self.max_size_bytes:
            return

        # Sort entries by LRU (Least Recently Used)
        entries_by_lru = sorted(
            self._memory_cache.items(),
            key=lambda x: x[1].last_accessed or x[1].created_at
        )

        # Remove entries until we're under the size limit
        for cache_key, entry in entries_by_lru:
            if current_size <= self.max_size_bytes * 0.8:  # Target 80% of max size
                break

            self._remove_from_cache(cache_key)
            current_size -= entry.size_bytes

        # Also limit memory cache entries
        if len(self._memory_cache) > self._memory_cache_max_size:
            # Keep only the most recently accessed entries
            entries_by_access = sorted(
                self._memory_cache.items(),
                key=lambda x: x[1].last_accessed or x[1].created_at,
                reverse=True
            )

            # Keep top N entries
            keep_entries = dict(entries_by_access[:self._memory_cache_max_size])

            # Remove others
            for cache_key in list(self._memory_cache.keys()):
                if cache_key not in keep_entries:
                    self._remove_from_cache(cache_key)

    def _remove_from_cache(self, cache_key: str):
        """Remove entry from cache."""
        # Remove from memory
        if cache_key in self._memory_cache:
            del self._memory_cache[cache_key]

        # Remove from disk
        cache_file = self._get_cache_file_path(cache_key)
        if cache_file.exists():
            try:
                cache_file.unlink()
            except Exception as e:
                print(f"Failed to remove cache file: {e}")

    def clear_expired(self):
        """Remove all expired cache entries."""
        expired_keys = []
        for cache_key, entry in self._memory_cache.items():
            if entry.is_expired():
                expired_keys.append(cache_key)

        for cache_key in expired_keys:
            self._remove_from_cache(cache_key)

        self._save_cache_index()

    def clear_stale(self, max_age_hours: float = 168):  # Default 1 week
        """Remove stale cache entries."""
        stale_keys = []
        for cache_key, entry in self._memory_cache.items():
            if entry.is_stale(max_age_hours):
                stale_keys.append(cache_key)

        for cache_key in stale_keys:
            self._remove_from_cache(cache_key)

        self._save_cache_index()

    def clear_category(self, category: str):
        """Clear all cache entries for a specific category."""
        category_keys = []
        for cache_key, entry in self._memory_cache.items():
            if entry.metadata.get('category') == category:
                category_keys.append(cache_key)

        for cache_key in category_keys:
            self._remove_from_cache(cache_key)

        self._save_cache_index()

    def clear_all(self):
        """Clear all cache entries."""
        # Remove all files
        for cache_file in self.cache_dir.glob("*.cache"):
            try:
                cache_file.unlink()
            except Exception:
                pass

        # Clear memory cache
        self._memory_cache.clear()

        # Remove index file
        index_file = self.cache_dir / "cache_index.json"
        if index_file.exists():
            try:
                index_file.unlink()
            except Exception:
                pass

    def get_cache_stats(self) -> Dict:
        """Get cache statistics."""
        total_entries = len(self._memory_cache)
        total_size = sum(entry.size_bytes for entry in self._memory_cache.values())
        total_accesses = sum(entry.access_count for entry in self._memory_cache.values())

        # Count by operation type
        operation_counts = {}
        for entry in self._memory_cache.values():
            operation = entry.metadata.get('operation', 'unknown')
            operation_counts[operation] = operation_counts.get(operation, 0) + 1

        # Find most/least accessed
        if self._memory_cache:
            most_accessed = max(self._memory_cache.values(), key=lambda x: x.access_count)
            least_accessed = min(self._memory_cache.values(), key=lambda x: x.access_count)
        else:
            most_accessed = least_accessed = None

        return {
            'total_entries': total_entries,
            'total_size_mb': total_size / (1024 * 1024),
            'max_size_mb': self.max_size_bytes / (1024 * 1024),
            'utilization_percent': (total_size / self.max_size_bytes * 100) if self.max_size_bytes > 0 else 0,
            'total_accesses': total_accesses,
            'avg_accesses_per_entry': total_accesses / total_entries if total_entries > 0 else 0,
            'operation_counts': operation_counts,
            'most_accessed_key': most_accessed.key if most_accessed else None,
            'most_accessed_count': most_accessed.access_count if most_accessed else 0,
            'least_accessed_key': least_accessed.key if least_accessed else None,
            'least_accessed_count': least_accessed.access_count if least_accessed else 0,
        }


class CachedScraper:
    """Base class for scrapers with caching support."""

    def __init__(self, cache_manager: Optional[CacheManager] = None):
        self.cache_manager = cache_manager or CacheManager()

    def get_cached_or_scrape(
        self,
        category: str,
        operation: str,
        scrape_func,
        *args,
        force_refresh: bool = False,
        **kwargs
    ) -> Any:
        """Get data from cache or scrape if not available."""

        if not force_refresh:
            # Try to get from cache first
            cached_data = self.cache_manager.get(category, operation, **kwargs)
            if cached_data is not None:
                return cached_data

        # Scrape fresh data
        fresh_data = scrape_func(*args, **kwargs)

        # Cache the result
        if fresh_data is not None:
            self.cache_manager.put(category, operation, fresh_data, **kwargs)

        return fresh_data


# Utility functions for common caching patterns

def cache_vendor_data(vendors: List[VendorData], category: str, cache_manager: CacheManager):
    """Cache a list of vendor data."""
    vendor_dict = {vendor.name: vendor.__dict__ for vendor in vendors}
    cache_manager.put(category, 'vendor_directory', vendor_dict)


def get_cached_vendor_data(category: str, cache_manager: CacheManager) -> Optional[List[VendorData]]:
    """Retrieve cached vendor data."""
    vendor_dict = cache_manager.get(category, 'vendor_directory')
    if vendor_dict:
        vendors = []
        for vendor_data in vendor_dict.values():
            vendor = VendorData(**vendor_data)
            vendors.append(vendor)
        return vendors
    return None


# Example usage
if __name__ == "__main__":
    # Initialize cache manager
    cache_manager = CacheManager(cache_dir=".test_cache", max_size_mb=50)

    # Example: Cache some vendor data
    test_vendors = [
        VendorData(name="Test Vendor 1", website="https://example1.com"),
        VendorData(name="Test Vendor 2", website="https://example2.com")
    ]

    # Cache the data
    cache_vendor_data(test_vendors, "test_category", cache_manager)

    # Retrieve from cache
    cached_vendors = get_cached_vendor_data("test_category", cache_manager)
    print(f"Retrieved {len(cached_vendors)} vendors from cache")

    # Show cache stats
    stats = cache_manager.get_cache_stats()
    print(f"Cache stats: {stats}")

    # Clean up
    cache_manager.clear_all()