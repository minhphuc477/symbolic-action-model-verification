"""
Backward-compatibility package for rule interventions.
All logic is centralized in src.interventions.rule_interventions.
"""

from .rule_interventions import InterventionType, RuleInterventionEngine

__all__ = ["InterventionType", "RuleInterventionEngine"]
