"""Backward-compatible re-exports for the legacy events module."""

from app.rules.base_rule import EventCandidate, RuleContext
from app.rules.base_rule import RuleProtocol as EventRule

__all__ = ["EventCandidate", "EventRule", "RuleContext"]
