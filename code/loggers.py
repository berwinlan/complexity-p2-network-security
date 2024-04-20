"""
Repast4py data logging.
"""

from dataclasses import dataclass


@dataclass
class MeetLog:
    """
    Data class for the meet log.
    """

    total_meets: int = 0
    min_meets: int = 0
    max_meets: int = 0
