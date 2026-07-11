"""
models.py — SQLAlchemy ORM model for the contact_messages table.

Mirrors the schema defined in schema.sql.
All columns use parameterized queries through SQLAlchemy — zero SQL injection risk.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SAEnum
from database import Base


class ContactMessage(Base):
    """
    Represents a single contact form submission stored in MySQL.

    Columns
    -------
    id          : Auto-increment primary key
    full_name   : Sanitized visitor name (max 150 chars)
    email       : Visitor email address (max 255 chars)
    subject     : Message subject (max 300 chars)
    message     : Full message body (TEXT, up to 65 535 bytes)
    ip_address  : IPv4 or IPv6 address of submitter (for spam tracking)
    user_agent  : Browser / client user-agent (truncated to 500 chars)
    created_at  : UTC timestamp of submission
    status      : Workflow state — 'new' | 'read' | 'replied'
    """

    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    full_name  = Column(String(150),  nullable=False)
    email      = Column(String(255),  nullable=False, index=True)
    subject    = Column(String(300),  nullable=False)
    message    = Column(Text,         nullable=False)

    ip_address = Column(String(45),   nullable=False, default="")
    user_agent = Column(String(500),  nullable=False, default="")

    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    status = Column(
        SAEnum("new", "read", "replied", name="message_status"),
        nullable=False,
        default="new",
    )

    def __repr__(self) -> str:
        return (
            f"<ContactMessage id={self.id} "
            f"from={self.email!r} "
            f"subject={self.subject!r} "
            f"status={self.status!r}>"
        )
