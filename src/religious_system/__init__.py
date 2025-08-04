"""
ClaudeEthos Religious System

A system for implementing and validating religious edicts in agent development work.
"""

from .edicts import EdictValidator, Edict, EvidenceType, EdictType
from .agent_validator import ReligiousAgentValidator
from .evidence_system import EvidenceValidator, Evidence
from .sin_log import sin_log, confess, perform_penance, get_wisdom_report, Sin, SinSeverity
from .religious_salutations import salutation_protocol, greet_agent, respond_to_salutation, ReligiousSalutation
from .cleric_agent import ClaudeEthosCleric, summon_cleric, DocumentSanctity, SacredTextViolation, RedemptionPath

__version__ = "0.1.0"
__all__ = [
    "EdictValidator",
    "Edict", 
    "EvidenceType",
    "ReligiousAgentValidator",
    "EvidenceValidator",
    "Evidence",
    "EdictType",
    "sin_log",
    "confess",
    "perform_penance",
    "get_wisdom_report",
    "Sin",
    "SinSeverity",
    "salutation_protocol",
    "greet_agent",
    "respond_to_salutation",
    "ReligiousSalutation"
]