"""
Repast4py data logging.
"""

from dataclasses import dataclass
from repast4py import logging

@dataclass
class MeetLog:
    total_meets: int = 0
    min_meets: int = 0
    max_meets: int = 0