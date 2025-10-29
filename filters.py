"""
Intelligent content filtering module for InfoFlow MCP Server.
Filters content based on relevance, quality, freshness, and user preferences.
"""

import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from loguru import logger

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available. Using basic filtering only.")

import numpy as np
from models import ContentItem, FilteredResult, FilterCriteria
from config import FilterConfig, UserPreferences


class ContentFilter:
    """Main content filtering engine."""
    
    def __init__(self, config: FilterConfig, user_prefs: UserPreferences):
        self.config = config
        self.user_prefs = user_prefs
        
        # Initialize semantic similarity model if available
        self.model = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("Semantic similarity model loaded")
            except Exception as e:
                logger.warning(f"Could not load similarity model: {e}")
    
    async def filter_items(
        self,
        items: List[ContentItem],
        criteria: Optional[FilterCriteria] = None
    ) -> FilteredResult:
        """
        Filter content items based on criteria and user preferences.
        
        Args:
            items: List of content items to filter
            criteria: Optional filtering criteria (overrides config)
        
        Returns:
            FilteredResult with filtered items and metadata
        """
        if not items:
            return FilteredResult(
                filtered_items=[],
                total_processed=0,
                total_filtered=0,
                filter_criteria=criteria or self._default_criteria(),
                applied_at=datetime.now()
            )
        
        logger.info(f"Filtering {len(items)} items")
        
        # Use provided criteria or create default
        filter_criteria = criteria or self._default_criteria()
        
        # Apply filtering pipeline
        filtered = items.copy()
        
        # Step 1: Filter by age/freshness
        filtered = await self._filter_by_age(filtered, filter_criteria)
        logger.debug(f"After age filter: {len(filtered)} items")
        
        # Step 2: Filter by source
        filtered = await self._filter_by_source(filtered, filter_criteria)
        logger.debug(f"After source filter: {len(filtered)} items")
        
        # Step 3: Filter by keywords
        filtered = await self._filter_by_keywords(filtered, filter_criteria)
        logger.debug(f"After keyword filter: {len(filtered)} items")
        
        # Step 4: Calculate relevance scores
        filtered = await self._calculate_relevance(filtered, filter_criteria)
        logger.debug(f"After relevance calculation: {len(filtered)} items")
        
        # Step 5: Calculate quality scores
        filtered = await self._calculate_quality(filtered)
        logger.debug(f"After quality calculation: {len(filtered)} items")
        
        # Step 6: Filter by relevance and quality thresholds
        filtered = await self._filter_by_scores(filtered, filter_criteria)
        logger.debug(f"After score filtering: {len(filtered)} items")
        
        # Step 7: Sort by relevance and quality
        filtered = sorted(
            filtered,
            key=lambda x: (x.relevance_score or 0) * (x.quality_score or 0),
            reverse=True
        )
        
        logger.info(f"Filtered to {len(filtered)} high-quality items")
        
        return FilteredResult(
            filtered_items=filtered,
            total_processed=len(items),
            total_filtered=len(filtered),
            filter_criteria=filter_criteria,
            applied_at=datetime.now()
        )
    
    async def _filter_by_age(
        self,
        items: List[ContentItem],
        criteria: FilterCriteria
    ) -> List[ContentItem]:
        """Filter items by publication age."""
        max_age = criteria.max_age_days or self.config.max_age_days
        cutoff_date = datetime.now() - timedelta(days=max_age)
        
        filtered = []
        for item in items:
            if item.published_date:
                if item.published_date >= cutoff_date:
                    filtered.append(item)
            else:
                # If no date, assume recent and include
                filtered.append(item)
        
        return filtered
    
    async def _filter_by_source(
        self,
        items: List[ContentItem],
        criteria: FilterCriteria
    ) -> List[ContentItem]:
        """Filter items by source preferences."""
        blocked = set(criteria.blocked_sources or self.config.blocked_sources)
        preferred = set(criteria.preferred_sources or self.config.preferred_sources)
        
        filtered = []
        for item in items:
            # Block if source is in blocked list
            if item.source in blocked:
                continue
            
            # If preferred sources specified, prioritize them
            if preferred and item.source not in preferred:
                # Still include but with lower score
                item.relevance_score = (item.relevance_score or 0.5) * 0.7
            
            filtered.append(item)
        
        return filtered
    
    async def _filter_by_keywords(
        self,
        items: List[ContentItem],
        criteria: FilterCriteria
    ) -> List[ContentItem]:
        """Filter items by keyword matching."""
        keywords = criteria.keywords or self.config.keywords
        
        if not keywords:
            # No keywords specified, include all
            return items
        
        # Convert keywords to lowercase for case-insensitive matching
        keywords_lower = [kw.lower() for kw in keywords]
        
        filtered = []
        for item in items:
            # Check if any keyword appears in title or content
            text = f"{item.title} {item.content}".lower()
            
            match_count = sum(1 for kw in keywords_lower if kw in text)
            
            if match_count > 0:
                # Boost relevance based on keyword matches
                boost = 1.0 + (match_count * 0.1)
                item.relevance_score = (item.relevance_score or 0.5) * boost
                filtered.append(item)
        
        return filtered if filtered else items  # Return all if no matches
    
    async def _calculate_relevance(
        self,
        items: List[ContentItem],
        criteria: FilterCriteria
    ) -> List[ContentItem]:
        """Calculate relevance scores for items."""
        if not criteria.query and not self.user_prefs.topics_of_interest:
            # No query or interests, use basic relevance
            for item in items:
                if item.relevance_score is None:
                    item.relevance_score = 0.5
            return items
        
        # Combine query and user interests
        reference_text = " ".join([
            criteria.query or "",
            " ".join(self.user_prefs.topics_of_interest)
        ]).strip()
        
        if self.model and SENTENCE_TRANSFORMERS_AVAILABLE:
            # Use semantic similarity
            try:
                reference_embedding = self.model.encode([reference_text])[0]
                
                for item in items:
                    item_text = f"{item.title} {item.content[:500]}"
                    item_embedding = self.model.encode([item_text])[0]
                    
                    # Calculate cosine similarity
                    similarity = np.dot(reference_embedding, item_embedding) / (
                        np.linalg.norm(reference_embedding) * np.linalg.norm(item_embedding)
                    )
                    
                    item.relevance_score = float(similarity)
                
            except Exception as e:
                logger.error(f"Error calculating semantic similarity: {e}")
                # Fall back to keyword matching
                await self._fallback_relevance(items, reference_text)
        else:
            # Use keyword-based relevance
            await self._fallback_relevance(items, reference_text)
        
        return items
    
    async def _fallback_relevance(self, items: List[ContentItem], reference_text: str):
        """Fallback relevance calculation using keyword matching."""
        reference_words = set(reference_text.lower().split())
        
        for item in items:
            item_text = f"{item.title} {item.content}".lower()
            item_words = set(item_text.split())
            
            # Calculate Jaccard similarity
            intersection = len(reference_words & item_words)
            union = len(reference_words | item_words)
            
            if union > 0:
                item.relevance_score = intersection / union
            else:
                item.relevance_score = 0.0
    
    async def _calculate_quality(self, items: List[ContentItem]) -> List[ContentItem]:
        """Calculate quality scores for items."""
        for item in items:
            quality_score = 0.5  # Base score
            
            # Factor 1: Content length (not too short, not too long)
            content_length = len(item.content)
            if 200 <= content_length <= 5000:
                quality_score += 0.2
            elif content_length > 5000:
                quality_score += 0.1
            
            # Factor 2: Has URL (indicates real content)
            if item.url and item.url.startswith('http'):
                quality_score += 0.1
            
            # Factor 3: Has author
            if item.author:
                quality_score += 0.1
            
            # Factor 4: Has tags
            if item.tags and len(item.tags) > 0:
                quality_score += 0.1
            
            # Factor 5: Title quality (not all caps, reasonable length)
            if item.title:
                if not item.title.isupper():
                    quality_score += 0.05
                if 10 <= len(item.title) <= 200:
                    quality_score += 0.05
            
            # Factor 6: Content structure (has paragraphs)
            if '\n' in item.content:
                quality_score += 0.1
            
            # Normalize to 0-1
            item.quality_score = min(1.0, quality_score)
        
        return items
    
    async def _filter_by_scores(
        self,
        items: List[ContentItem],
        criteria: FilterCriteria
    ) -> List[ContentItem]:
        """Filter items by relevance and quality score thresholds."""
        relevance_threshold = criteria.relevance_threshold or self.config.relevance_threshold
        quality_threshold = criteria.quality_threshold or self.config.quality_threshold
        
        filtered = []
        for item in items:
            relevance = item.relevance_score or 0.0
            quality = item.quality_score or 0.0
            
            if relevance >= relevance_threshold and quality >= quality_threshold:
                filtered.append(item)
        
        return filtered
    
    def _default_criteria(self) -> FilterCriteria:
        """Create default filter criteria from config."""
        return FilterCriteria(
            relevance_threshold=self.config.relevance_threshold,
            quality_threshold=self.config.quality_threshold,
            max_age_days=self.config.max_age_days,
            preferred_sources=self.config.preferred_sources,
            blocked_sources=self.config.blocked_sources,
            keywords=self.config.keywords or self.user_prefs.topics_of_interest,
            query=""
        )
    
    async def rank_by_urgency(self, items: List[ContentItem]) -> List[ContentItem]:
        """
        Rank items by urgency for decision-making.
        
        Urgency factors:
        - Recency (newer = more urgent)
        - Relevance score
        - Keywords like "urgent", "breaking", "alert"
        """
        urgency_keywords = ['urgent', 'breaking', 'alert', 'critical', 'important', 'deadline']
        
        def calculate_urgency(item: ContentItem) -> float:
            score = 0.0
            
            # Recency factor (0-0.4)
            if item.published_date:
                age_hours = (datetime.now() - item.published_date).total_seconds() / 3600
                if age_hours < 1:
                    score += 0.4
                elif age_hours < 24:
                    score += 0.3
                elif age_hours < 168:  # 1 week
                    score += 0.2
                else:
                    score += 0.1
            
            # Relevance factor (0-0.4)
            score += (item.relevance_score or 0.5) * 0.4
            
            # Urgency keywords factor (0-0.2)
            text = f"{item.title} {item.content}".lower()
            keyword_count = sum(1 for kw in urgency_keywords if kw in text)
            score += min(0.2, keyword_count * 0.05)
            
            return score
        
        # Calculate urgency for all items
        for item in items:
            item.urgency_score = calculate_urgency(item)
        
        # Sort by urgency (descending)
        return sorted(items, key=lambda x: getattr(x, 'urgency_score', 0), reverse=True)


class DuplicateDetector:
    """Detect and remove duplicate content."""
    
    def __init__(self, similarity_threshold: float = 0.85):
        self.similarity_threshold = similarity_threshold
        self.model = None
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception as e:
                logger.warning(f"Could not load duplicate detection model: {e}")
    
    async def remove_duplicates(self, items: List[ContentItem]) -> List[ContentItem]:
        """Remove duplicate items based on content similarity."""
        if not items or len(items) <= 1:
            return items
        
        unique_items = []
        seen_hashes = set()
        
        for item in items:
            # Quick check: exact URL match
            if item.url in seen_hashes:
                continue
            
            # Quick check: exact title match
            title_hash = hash(item.title.lower())
            if title_hash in seen_hashes:
                continue
            
            # Semantic similarity check (if available)
            if self.model and unique_items:
                is_duplicate = await self._check_semantic_duplicate(item, unique_items)
                if is_duplicate:
                    continue
            
            unique_items.append(item)
            if item.url:
                seen_hashes.add(item.url)
            seen_hashes.add(title_hash)
        
        logger.info(f"Removed {len(items) - len(unique_items)} duplicates")
        return unique_items
    
    async def _check_semantic_duplicate(
        self,
        item: ContentItem,
        existing_items: List[ContentItem]
    ) -> bool:
        """Check if item is semantically duplicate of existing items."""
        try:
            item_text = f"{item.title} {item.content[:500]}"
            item_embedding = self.model.encode([item_text])[0]
            
            for existing in existing_items[-5:]:  # Check against last 5 items only
                existing_text = f"{existing.title} {existing.content[:500]}"
                existing_embedding = self.model.encode([existing_text])[0]
                
                similarity = np.dot(item_embedding, existing_embedding) / (
                    np.linalg.norm(item_embedding) * np.linalg.norm(existing_embedding)
                )
                
                if similarity >= self.similarity_threshold:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in semantic duplicate check: {e}")
            return False
