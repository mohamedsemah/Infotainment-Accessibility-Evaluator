"""
WCAG 2.2 constants and mappings for accessibility evaluation.
"""

from enum import Enum
from typing import Dict, List, Tuple

class WCAGLevel(str, Enum):
    A = "A"
    AA = "AA"
    AAA = "AAA"

class WCAGPrinciple(str, Enum):
    PERCEIVABLE = "perceivable"
    OPERABLE = "operable"
    UNDERSTANDABLE = "understandable"
    ROBUST = "robust"

# WCAG 2.2 Success Criteria
WCAG_CRITERIA = {
    # Perceivable
    "1.1.1": {
        "title": "Non-text Content",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "All non-text content that is presented to the user has a text alternative"
    },
    "1.2.1": {
        "title": "Audio-only and Video-only (Prerecorded)",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "For prerecorded audio-only and prerecorded video-only media"
    },
    "1.2.2": {
        "title": "Captions (Prerecorded)",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "Captions are provided for all prerecorded audio content"
    },
    "1.2.3": {
        "title": "Audio Description or Media Alternative (Prerecorded)",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "An alternative for time-based media or audio description is provided"
    },
    "1.2.4": {
        "title": "Captions (Live)",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "Captions are provided for all live audio content"
    },
    "1.2.5": {
        "title": "Audio Description (Prerecorded)",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "Audio description is provided for all prerecorded video content"
    },
    "1.3.1": {
        "title": "Info and Relationships",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "Information, structure, and relationships can be programmatically determined"
    },
    "1.3.2": {
        "title": "Meaningful Sequence",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "When the sequence in which content is presented affects its meaning"
    },
    "1.3.3": {
        "title": "Sensory Characteristics",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "Instructions provided for understanding and operating content do not rely solely on sensory characteristics"
    },
    "1.3.4": {
        "title": "Orientation",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "Content does not restrict its view and operation to a single display orientation"
    },
    "1.3.5": {
        "title": "Identify Input Purpose",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "The purpose of each input field collecting information about the user can be programmatically determined"
    },
    "1.3.6": {
        "title": "Identify Purpose",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "In content implemented using markup languages, the purpose of User Interface Components, icons, and regions can be programmatically determined"
    },
    "1.4.1": {
        "title": "Use of Color",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "Color is not used as the only visual means of conveying information"
    },
    "1.4.2": {
        "title": "Audio Control",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "If any audio on a Web page plays automatically for more than 3 seconds"
    },
    "1.4.3": {
        "title": "Contrast (Minimum)",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "The visual presentation of text and images of text has a contrast ratio of at least 4.5:1"
    },
    "1.4.4": {
        "title": "Resize Text",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "Text can be resized without assistive technology up to 200 percent without loss of content or functionality"
    },
    "1.4.5": {
        "title": "Images of Text",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "If the technologies being used can achieve the visual presentation, text is used to convey information rather than images of text"
    },
    "1.4.6": {
        "title": "Contrast (Enhanced)",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "The visual presentation of text and images of text has a contrast ratio of at least 7:1"
    },
    "1.4.7": {
        "title": "Low or No Background Audio",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "For prerecorded audio-only content that (1) contains primarily speech in the foreground"
    },
    "1.4.8": {
        "title": "Visual Presentation",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "For the visual presentation of blocks of text"
    },
    "1.4.9": {
        "title": "Images of Text (No Exception)",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "Images of text are only used for pure decoration or where a particular presentation of text is essential"
    },
    "1.4.10": {
        "title": "Reflow",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "Content can be presented without loss of information or functionality, and without requiring scrolling in two dimensions"
    },
    "1.4.11": {
        "title": "Non-text Contrast",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "The visual presentation of user interface components and graphical objects has a contrast ratio of at least 3:1"
    },
    "1.4.12": {
        "title": "Text Spacing",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "In content implemented using markup languages, no loss of content or functionality occurs by setting text spacing"
    },
    "1.4.13": {
        "title": "Content on Hover or Focus",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.PERCEIVABLE,
        "description": "Where receiving and then removing pointer hover or keyboard focus triggers additional content to become visible"
    },
    
    # Operable
    "2.1.1": {
        "title": "Keyboard",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "All functionality of the content is available from a keyboard"
    },
    "2.1.2": {
        "title": "No Keyboard Trap",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "If keyboard focus can be moved to a component of the page using a keyboard interface"
    },
    "2.1.3": {
        "title": "Keyboard (No Exception)",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "All functionality of the content is available from a keyboard"
    },
    "2.1.4": {
        "title": "Character Key Shortcuts",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "If a keyboard shortcut is implemented in content"
    },
    "2.2.1": {
        "title": "Timing Adjustable",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "For each time limit that is set by the content"
    },
    "2.2.2": {
        "title": "Pause, Stop, Hide",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "For moving, blinking, scrolling, or auto-updating information"
    },
    "2.2.3": {
        "title": "No Timing",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "Timing is not an essential part of the event or activity presented by the content"
    },
    "2.2.4": {
        "title": "Interruptions",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "Interruptions can be postponed or suppressed by the user"
    },
    "2.2.5": {
        "title": "Re-authenticating",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "When an authenticated session expires, the user can continue the activity without loss of data"
    },
    "2.2.6": {
        "title": "Timeouts",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "Users are warned of the duration of any user inactivity that could cause data loss"
    },
    "2.3.1": {
        "title": "Three Flashes or Below Threshold",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "Web pages do not contain anything that flashes more than three times in any one second period"
    },
    "2.3.2": {
        "title": "Three Flashes",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "Web pages do not contain anything that flashes more than three times in any one second period"
    },
    "2.3.3": {
        "title": "Animation from Interactions",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "Motion animation triggered by interaction can be disabled"
    },
    "2.4.1": {
        "title": "Bypass Blocks",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "A mechanism is available to bypass blocks of content that are repeated on multiple Web pages"
    },
    "2.4.2": {
        "title": "Page Titled",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "Web pages have titles that describe topic or purpose"
    },
    "2.4.3": {
        "title": "Focus Order",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "If a Web page can be navigated sequentially and the navigation sequences affect meaning or operation"
    },
    "2.4.4": {
        "title": "Link Purpose (In Context)",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "The purpose of each link can be determined from the link text alone or from the link text together with its programmatically determined link context"
    },
    "2.4.5": {
        "title": "Multiple Ways",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "More than one way is available to locate a Web page within a set of Web pages"
    },
    "2.4.6": {
        "title": "Headings and Labels",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "Headings and labels describe topic or purpose"
    },
    "2.4.7": {
        "title": "Focus Visible",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "Any keyboard operable user interface has a mode of operation where the keyboard focus indicator is visible"
    },
    "2.4.8": {
        "title": "Location",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "Information about the user's location within a set of Web pages is available"
    },
    "2.4.9": {
        "title": "Link Purpose (Link Only)",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "A mechanism is available to allow the purpose of each link to be identified from link text alone"
    },
    "2.4.10": {
        "title": "Section Headings",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "Section headings are used to organize the content"
    },
    "2.4.11": {
        "title": "Focus Appearance (Minimum)",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "When the keyboard focus indicator is visible, an area of the focus indicator meets all the following"
    },
    "2.4.12": {
        "title": "Focus Appearance (Enhanced)",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "When the keyboard focus indicator is visible, an area of the focus indicator meets all the following"
    },
    "2.4.13": {
        "title": "Page Break Navigation",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "For a Web page with page breaks, a mechanism is available to navigate to each page break"
    },
    "2.5.1": {
        "title": "Pointer Gestures",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "All functionality that uses multipoint or path-based gestures for operation can be operated with a single pointer"
    },
    "2.5.2": {
        "title": "Pointer Cancellation",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "For functionality that can be operated using a single pointer"
    },
    "2.5.3": {
        "title": "Label in Name",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "For user interface components with labels that include text or images of text"
    },
    "2.5.4": {
        "title": "Motion Activation",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "Functionality that can be operated by device motion or user motion can also be operated by user interface components"
    },
    "2.5.5": {
        "title": "Target Size",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "Targets have a size of at least 44 by 44 CSS pixels"
    },
    "2.5.6": {
        "title": "Concurrent Input Mechanisms",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "Web content does not restrict use of input modalities available on a platform"
    },
    "2.5.7": {
        "title": "Dragging",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "All functionality that uses a dragging movement is operable with a single pointer"
    },
    "2.5.8": {
        "title": "Target Size (Minimum)",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.OPERABLE,
        "description": "Targets have a size of at least 24 by 24 CSS pixels"
    },
    
    # Understandable
    "3.1.1": {
        "title": "Language of Page",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "The default human language of each Web page can be programmatically determined"
    },
    "3.1.2": {
        "title": "Language of Parts",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "The human language of each passage or phrase in the content can be programmatically determined"
    },
    "3.1.3": {
        "title": "Unusual Words",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "A mechanism is available for identifying specific definitions of words or phrases used in an unusual or restricted way"
    },
    "3.1.4": {
        "title": "Abbreviations",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "A mechanism for identifying the expanded form or meaning of abbreviations is available"
    },
    "3.1.5": {
        "title": "Reading Level",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "When text requires reading ability more advanced than the lower secondary education level"
    },
    "3.1.6": {
        "title": "Pronunciation",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "A mechanism is available for identifying specific pronunciation of words where meaning of the words"
    },
    "3.2.1": {
        "title": "On Focus",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "When any component receives focus, it does not initiate a change of context"
    },
    "3.2.2": {
        "title": "On Input",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "Changing the setting of any user interface component does not automatically cause a change of context"
    },
    "3.2.3": {
        "title": "Consistent Navigation",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "Navigational mechanisms that are repeated on multiple Web pages within a set of Web pages occur in the same relative order each time they are repeated"
    },
    "3.2.4": {
        "title": "Consistent Identification",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "Components that have the same functionality within a set of Web pages are identified consistently"
    },
    "3.2.5": {
        "title": "Change on Request",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "Changes of context are initiated only by user request or a mechanism is available to turn off such changes"
    },
    "3.2.6": {
        "title": "Consistent Help",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "If a Web page contains any of the following help mechanisms"
    },
    "3.2.7": {
        "title": "Visible Controls",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "If any keyboard operable user interface component has keyboard focus"
    },
    "3.3.1": {
        "title": "Error Identification",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "If an input error is automatically detected, the item that is in error is identified and the error is described to the user in text"
    },
    "3.3.2": {
        "title": "Labels or Instructions",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "Labels or instructions are provided when content requires user input"
    },
    "3.3.3": {
        "title": "Error Suggestion",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "If an input error is automatically detected and suggestions for correction are known"
    },
    "3.3.4": {
        "title": "Error Prevention (Legal, Financial, Data)",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "For Web pages that cause legal commitments or financial transactions for the user to occur"
    },
    "3.3.5": {
        "title": "Help",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "Context-sensitive help is available"
    },
    "3.3.6": {
        "title": "Error Prevention (All)",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "For Web pages that require the user to submit information"
    },
    "3.3.7": {
        "title": "Accessible Authentication",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "A cognitive function test (such as remembering a password or solving a puzzle) is not required for any step in an authentication process"
    },
    "3.3.8": {
        "title": "Redundant Entry",
        "level": WCAGLevel.AAA,
        "principle": WCAGPrinciple.UNDERSTANDABLE,
        "description": "Information previously entered by the user in the same process is auto-populated or available for the user to select"
    },
    
    # Robust
    "4.1.1": {
        "title": "Parsing",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.ROBUST,
        "description": "In content implemented using markup languages, elements have complete start and end tags"
    },
    "4.1.2": {
        "title": "Name, Role, Value",
        "level": WCAGLevel.A,
        "principle": WCAGPrinciple.ROBUST,
        "description": "For all user interface components, the name and role can be programmatically determined"
    },
    "4.1.3": {
        "title": "Status Messages",
        "level": WCAGLevel.AA,
        "principle": WCAGPrinciple.ROBUST,
        "description": "In content implemented using markup languages, status messages can be programmatically determined through role or properties"
    }
}

# Contrast ratio thresholds
CONTRAST_THRESHOLDS = {
    WCAGLevel.AA: {
        "normal_text": 4.5,
        "large_text": 3.0,
        "non_text": 3.0
    },
    WCAGLevel.AAA: {
        "normal_text": 7.0,
        "large_text": 4.5,
        "non_text": 3.0
    }
}

# Text size categories for contrast evaluation
TEXT_SIZE_CATEGORIES = {
    "large": 18,  # 18px or 14pt
    "bold_large": 14  # 14px bold or 18pt
}

# Flash frequency thresholds (Hz)
FLASH_THRESHOLDS = {
    "max_frequency": 3.0,  # Maximum 3 flashes per second
    "dangerous_frequency": 2.0,  # Dangerous frequency threshold
    "safe_frequency": 1.0  # Safe frequency threshold
}

# ARIA role categories
ARIA_ROLE_CATEGORIES = {
    "widget": [
        "button", "checkbox", "gridcell", "link", "menuitem", "menuitemcheckbox",
        "menuitemradio", "option", "progressbar", "radio", "scrollbar", "slider",
        "spinbutton", "switch", "tab", "tabpanel", "textbox", "treeitem"
    ],
    "composite": [
        "combobox", "grid", "listbox", "menu", "menubar", "radiogroup", "tablist",
        "tree", "treegrid"
    ],
    "document": [
        "article", "columnheader", "definition", "directory", "document", "group",
        "heading", "img", "list", "listitem", "math", "none", "note", "presentation",
        "region", "row", "rowgroup", "rowheader", "separator", "table", "term", "toolbar"
    ],
    "landmark": [
        "application", "banner", "complementary", "contentinfo", "form", "main",
        "navigation", "search"
    ],
    "live_region": [
        "alert", "log", "marquee", "status", "timer"
    ],
    "window": [
        "alertdialog", "dialog"
    ]
}

# BCP-47 language tags (common ones)
COMMON_LANGUAGE_TAGS = [
    "en", "en-US", "en-GB", "en-CA", "en-AU",
    "es", "es-ES", "es-MX", "es-AR",
    "fr", "fr-FR", "fr-CA",
    "de", "de-DE", "de-AT",
    "it", "it-IT",
    "pt", "pt-BR", "pt-PT",
    "ru", "ru-RU",
    "ja", "ja-JP",
    "ko", "ko-KR",
    "zh", "zh-CN", "zh-TW",
    "ar", "ar-SA",
    "hi", "hi-IN",
    "nl", "nl-NL",
    "sv", "sv-SE",
    "no", "no-NO",
    "da", "da-DK",
    "fi", "fi-FI",
    "pl", "pl-PL",
    "tr", "tr-TR",
    "th", "th-TH",
    "vi", "vi-VN"
]

def get_criterion_by_type(criterion_type: str) -> List[str]:
    """Get WCAG criteria by type (contrast, seizure_safe, language, aria)."""
    type_mapping = {
        "contrast": ["1.4.3", "1.4.6", "1.4.11"],
        "seizure_safe": ["2.3.1", "2.3.2", "2.3.3"],
        "language": ["3.1.1", "3.1.2"],
        "aria": ["4.1.2", "4.1.3"],
        "state_explorer": ["1.4.13", "2.4.11", "2.4.12"]
    }
    return type_mapping.get(criterion_type, [])

def get_criteria_by_principle(principle: WCAGPrinciple) -> List[str]:
    """Get all criteria for a specific WCAG principle."""
    return [
        criterion_id for criterion_id, info in WCAG_CRITERIA.items()
        if info["principle"] == principle
    ]

def get_criteria_by_level(level: WCAGLevel) -> List[str]:
    """Get all criteria for a specific WCAG level."""
    return [
        criterion_id for criterion_id, info in WCAG_CRITERIA.items()
        if info["level"] == level
    ]
