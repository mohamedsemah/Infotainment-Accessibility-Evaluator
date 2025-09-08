"""
Patching services for generating accessibility fixes.
"""

from .patch_generator import PatchGenerator
from .contrast_patcher import ContrastPatcher
from .aria_patcher import ARIAPatcher
from .language_patcher import LanguagePatcher
from .seizure_patcher import SeizurePatcher

__all__ = [
    'PatchGenerator',
    'ContrastPatcher',
    'ARIAPatcher', 
    'LanguagePatcher',
    'SeizurePatcher'
]

