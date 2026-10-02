"""
Backward-compatibility proxy for src.interventions.rule_interventions.
All logic is centralized in src.interventions.rule_interventions.
"""

from src.interventions.rule_interventions import (
    BaseInterventionStrategy,
    Combinatorial3ASTMutationsStrategy,
    GlobalPhaseShiftStrategy,
    InterventionType,
    InvertBufferConditionStrategy,
    MutateGridParamsStrategy,
    OmitBottleneckPreconditionStrategy,
    OmitGoalCheckPredicateStrategy,
    OmitLeafPreconditionStrategy,
    RedundantEffectStrategy,
    RenameVariableAttributeStrategy,
    RuleInterventionEngine,
    SwapLHSConditionOrderStrategy,
)

__all__ = [
    "BaseInterventionStrategy",
    "Combinatorial3ASTMutationsStrategy",
    "GlobalPhaseShiftStrategy",
    "InterventionType",
    "InvertBufferConditionStrategy",
    "MutateGridParamsStrategy",
    "OmitBottleneckPreconditionStrategy",
    "OmitGoalCheckPredicateStrategy",
    "OmitLeafPreconditionStrategy",
    "RedundantEffectStrategy",
    "RenameVariableAttributeStrategy",
    "RuleInterventionEngine",
    "SwapLHSConditionOrderStrategy",
]
