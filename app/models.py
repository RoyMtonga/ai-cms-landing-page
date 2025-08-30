from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class PageStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class WebsiteStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BUILDING = "building"


class FeatureType(str, Enum):
    CORE = "core"
    AI_BUILDER = "ai_builder"
    CMS = "cms"
    ADVANCED = "advanced"


class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    HERO = "hero"
    FEATURE = "feature"
    CTA = "cta"
    NAVIGATION = "navigation"
    FOOTER = "footer"


# Persistent models (stored in database)
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    username: str = Field(max_length=50, unique=True)
    full_name: str = Field(max_length=100)
    is_active: bool = Field(default=True)
    is_premium: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    websites: List["Website"] = Relationship(back_populates="owner")
    ai_sessions: List["AIBuilderSession"] = Relationship(back_populates="user")


class Website(SQLModel, table=True):
    __tablename__ = "websites"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    domain: Optional[str] = Field(default=None, max_length=255, unique=True)
    description: Optional[str] = Field(default=None, max_length=500)
    status: WebsiteStatus = Field(default=WebsiteStatus.BUILDING)
    theme: str = Field(default="modern", max_length=50)
    custom_css: Optional[str] = Field(default=None)
    seo_settings: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    analytics_config: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    owner_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = Field(default=None)

    # Relationships
    owner: User = Relationship(back_populates="websites")
    pages: List["Page"] = Relationship(back_populates="website")
    navigation_items: List["NavigationItem"] = Relationship(back_populates="website")
    ai_sessions: List["AIBuilderSession"] = Relationship(back_populates="website")


class Page(SQLModel, table=True):
    __tablename__ = "pages"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    slug: str = Field(max_length=100)
    meta_description: Optional[str] = Field(default=None, max_length=300)
    content: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    status: PageStatus = Field(default=PageStatus.DRAFT)
    is_homepage: bool = Field(default=False)
    template: str = Field(default="landing", max_length=50)
    custom_css: Optional[str] = Field(default=None)
    website_id: int = Field(foreign_key="websites.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = Field(default=None)

    # Relationships
    website: Website = Relationship(back_populates="pages")
    content_blocks: List["ContentBlock"] = Relationship(back_populates="page")


class ContentBlock(SQLModel, table=True):
    __tablename__ = "content_blocks"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    type: ContentType = Field()
    title: Optional[str] = Field(default=None, max_length=200)
    content: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    position: int = Field(default=0)
    is_visible: bool = Field(default=True)
    styling: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    page_id: int = Field(foreign_key="pages.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    page: Page = Relationship(back_populates="content_blocks")


class Feature(SQLModel, table=True):
    __tablename__ = "features"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    title: str = Field(max_length=200)
    description: str = Field(max_length=500)
    type: FeatureType = Field()
    icon: Optional[str] = Field(default=None, max_length=100)
    is_active: bool = Field(default=True)
    sort_order: int = Field(default=0)
    feature_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class NavigationItem(SQLModel, table=True):
    __tablename__ = "navigation_items"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    label: str = Field(max_length=100)
    url: str = Field(max_length=500)
    position: int = Field(default=0)
    is_external: bool = Field(default=False)
    is_active: bool = Field(default=True)
    parent_id: Optional[int] = Field(default=None, foreign_key="navigation_items.id")
    website_id: int = Field(foreign_key="websites.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    website: Website = Relationship(back_populates="navigation_items")
    parent: Optional["NavigationItem"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "NavigationItem.id"}
    )
    children: List["NavigationItem"] = Relationship(back_populates="parent")


class AIBuilderSession(SQLModel, table=True):
    __tablename__ = "ai_builder_sessions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(unique=True, max_length=100)
    prompt: str = Field(max_length=2000)
    generated_content: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    user_feedback: Optional[str] = Field(default=None, max_length=1000)
    is_applied: bool = Field(default=False)
    user_id: int = Field(foreign_key="users.id")
    website_id: Optional[int] = Field(default=None, foreign_key="websites.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="ai_sessions")
    website: Optional[Website] = Relationship(back_populates="ai_sessions")


class Template(SQLModel, table=True):
    __tablename__ = "templates"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    title: str = Field(max_length=200)
    description: str = Field(max_length=500)
    category: str = Field(max_length=50)
    preview_image: Optional[str] = Field(default=None, max_length=500)
    structure: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    default_styling: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    is_premium: bool = Field(default=False)
    is_active: bool = Field(default=True)
    usage_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)
class UserCreate(SQLModel, table=False):
    email: str = Field(max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    username: str = Field(max_length=50)
    full_name: str = Field(max_length=100)


class UserUpdate(SQLModel, table=False):
    full_name: Optional[str] = Field(default=None, max_length=100)
    is_premium: Optional[bool] = Field(default=None)


class WebsiteCreate(SQLModel, table=False):
    name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    domain: Optional[str] = Field(default=None, max_length=255)
    theme: str = Field(default="modern", max_length=50)


class WebsiteUpdate(SQLModel, table=False):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    domain: Optional[str] = Field(default=None, max_length=255)
    status: Optional[WebsiteStatus] = Field(default=None)
    theme: Optional[str] = Field(default=None, max_length=50)
    custom_css: Optional[str] = Field(default=None)
    seo_settings: Optional[Dict[str, Any]] = Field(default=None)


class PageCreate(SQLModel, table=False):
    title: str = Field(max_length=200)
    slug: str = Field(max_length=100)
    meta_description: Optional[str] = Field(default=None, max_length=300)
    template: str = Field(default="landing", max_length=50)
    is_homepage: bool = Field(default=False)


class PageUpdate(SQLModel, table=False):
    title: Optional[str] = Field(default=None, max_length=200)
    slug: Optional[str] = Field(default=None, max_length=100)
    meta_description: Optional[str] = Field(default=None, max_length=300)
    content: Optional[Dict[str, Any]] = Field(default=None)
    status: Optional[PageStatus] = Field(default=None)
    template: Optional[str] = Field(default=None, max_length=50)
    custom_css: Optional[str] = Field(default=None)


class ContentBlockCreate(SQLModel, table=False):
    type: ContentType
    title: Optional[str] = Field(default=None, max_length=200)
    content: Dict[str, Any] = Field(default={})
    position: int = Field(default=0)
    styling: Dict[str, Any] = Field(default={})


class ContentBlockUpdate(SQLModel, table=False):
    title: Optional[str] = Field(default=None, max_length=200)
    content: Optional[Dict[str, Any]] = Field(default=None)
    position: Optional[int] = Field(default=None)
    is_visible: Optional[bool] = Field(default=None)
    styling: Optional[Dict[str, Any]] = Field(default=None)


class NavigationItemCreate(SQLModel, table=False):
    label: str = Field(max_length=100)
    url: str = Field(max_length=500)
    position: int = Field(default=0)
    is_external: bool = Field(default=False)
    parent_id: Optional[int] = Field(default=None)


class NavigationItemUpdate(SQLModel, table=False):
    label: Optional[str] = Field(default=None, max_length=100)
    url: Optional[str] = Field(default=None, max_length=500)
    position: Optional[int] = Field(default=None)
    is_external: Optional[bool] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    parent_id: Optional[int] = Field(default=None)


class AIBuilderRequest(SQLModel, table=False):
    prompt: str = Field(max_length=2000)
    website_id: Optional[int] = Field(default=None)


class AIBuilderResponse(SQLModel, table=False):
    session_id: str
    generated_content: Dict[str, Any]
    suggestions: List[str] = Field(default=[])


class FeatureResponse(SQLModel, table=False):
    id: int
    name: str
    title: str
    description: str
    type: FeatureType
    icon: Optional[str]
    feature_metadata: Dict[str, Any]


class LandingPageData(SQLModel, table=False):
    hero_content: Dict[str, Any] = Field(default={})
    features: List[FeatureResponse] = Field(default=[])
    how_it_works_steps: List[Dict[str, Any]] = Field(default=[])
    cta_content: Dict[str, Any] = Field(default={})
    navigation_items: List[Dict[str, str]] = Field(default=[])
    footer_links: List[Dict[str, str]] = Field(default=[])
