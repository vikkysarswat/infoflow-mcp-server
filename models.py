"""
Data models for InfoFlow MCP Server
"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RiskTolerance(str, Enum):
    """Risk tolerance levels for decision making"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DecisionStyle(str, Enum):
    """Decision-making styles"""
    ANALYTICAL = "analytical"
    INTUITIVE = "intuitive"
    COLLABORATIVE = "collaborative"


class PriorityLevel(str, Enum):
    """Priority levels for content"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class DecisionStatus(str, Enum):
    """Status of a decision"""
    PENDING = "pending"
    DECIDED = "decided"
    IMPLEMENTED = "implemented"
    REVIEWED = "reviewed"


class UserProfile(BaseModel):
    """User profile model"""
    user_id: str = Field(..., description="Unique user identifier")
    name: str = Field(..., description="User's name")
    interests: List[str] = Field(default_factory=list, description="List of user interests")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")
    risk_tolerance: RiskTolerance = Field(default=RiskTolerance.MEDIUM)
    decision_style: DecisionStyle = Field(default=DecisionStyle.ANALYTICAL)
    notification_threshold: int = Field(default=3, ge=1, le=5, description="Priority level for notifications (1-5)")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ContentItem(BaseModel):
    """Content item to be filtered/synthesized"""
    content_id: str = Field(..., description="Unique content identifier")
    title: str = Field(..., description="Content title")
    content: str = Field(..., description="Content text")
    source: Optional[str] = Field(None, description="Content source")
    url: Optional[str] = Field(None, description="Content URL")
    tags: List[str] = Field(default_factory=list, description="Content tags")
    relevance_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Relevance score (0-1)")
    priority: Optional[PriorityLevel] = Field(None, description="Assigned priority level")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class FilterCriteria(BaseModel):
    """Criteria for filtering content"""
    user_id: str
    min_relevance: float = Field(default=0.3, ge=0.0, le=1.0)
    min_priority: int = Field(default=3, ge=1, le=5)
    interests: Optional[List[str]] = None
    exclude_tags: List[str] = Field(default_factory=list)


class SynthesisRequest(BaseModel):
    """Request for synthesizing information"""
    user_id: str
    sources: List[ContentItem] = Field(..., description="Sources to synthesize")
    focus_areas: List[str] = Field(default_factory=list, description="Areas to focus on")
    max_length: int = Field(default=500, ge=100, le=2000, description="Maximum summary length")


class SynthesisResult(BaseModel):
    """Result of information synthesis"""
    summary: str = Field(..., description="Synthesized summary")
    key_themes: List[str] = Field(default_factory=list, description="Key themes identified")
    consensus_points: List[str] = Field(default_factory=list, description="Points of consensus")
    contradictions: List[str] = Field(default_factory=list, description="Contradictions found")
    actionable_insights: List[str] = Field(default_factory=list, description="Actionable insights")
    sources_used: int = Field(..., description="Number of sources used")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DecisionOption(BaseModel):
    """An option in a decision"""
    option_id: str
    name: str
    description: str
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    cost: Optional[float] = None
    time_required: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Decision(BaseModel):
    """Decision model"""
    decision_id: str
    user_id: str
    title: str
    description: str
    context: str = Field(default="", description="Additional context for the decision")
    options: List[DecisionOption] = Field(default_factory=list)
    criteria: List[str] = Field(default_factory=list, description="Decision criteria")
    status: DecisionStatus = Field(default=DecisionStatus.PENDING)
    selected_option: Optional[str] = None
    rationale: Optional[str] = None
    outcome: Optional[str] = None
    feedback_score: Optional[int] = Field(None, ge=1, le=5)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    decided_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DecisionRecommendation(BaseModel):
    """AI recommendation for a decision"""
    decision_id: str
    recommended_option: str
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in recommendation (0-1)")
    reasoning: str
    considerations: List[str] = Field(default_factory=list)
    risk_assessment: str
    alternative_suggestions: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MonitoredTopic(BaseModel):
    """Topic being monitored"""
    topic_id: str
    user_id: str
    name: str
    description: str
    keywords: List[str] = Field(default_factory=list)
    priority_threshold: int = Field(default=3, ge=1, le=5)
    last_checked: Optional[datetime] = None
    alert_count: int = Field(default=0)
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TopicAlert(BaseModel):
    """Alert for a monitored topic"""
    alert_id: str
    topic_id: str
    user_id: str
    content_id: str
    message: str
    priority: PriorityLevel
    read: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
