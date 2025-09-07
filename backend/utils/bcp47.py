"""
BCP-47 language tag validation and canonicalization utilities.
"""

import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class LanguageTag:
    """Represents a BCP-47 language tag."""
    language: str
    script: Optional[str] = None
    region: Optional[str] = None
    variant: Optional[str] = None
    extension: Optional[str] = None
    private_use: Optional[str] = None
    
    def __str__(self) -> str:
        """Convert to BCP-47 string format."""
        parts = [self.language]
        
        if self.script:
            parts.append(self.script)
        if self.region:
            parts.append(self.region)
        if self.variant:
            parts.append(self.variant)
        if self.extension:
            parts.append(self.extension)
        if self.private_use:
            parts.append(self.private_use)
        
        return "-".join(parts)

# Common language subtags
LANGUAGE_SUBTAGS = {
    # Primary languages
    "en": "English",
    "es": "Spanish", 
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ar": "Arabic",
    "hi": "Hindi",
    "nl": "Dutch",
    "sv": "Swedish",
    "no": "Norwegian",
    "da": "Danish",
    "fi": "Finnish",
    "pl": "Polish",
    "tr": "Turkish",
    "th": "Thai",
    "vi": "Vietnamese",
    "he": "Hebrew",
    "id": "Indonesian",
    "ms": "Malay",
    "tl": "Tagalog",
    "uk": "Ukrainian",
    "cs": "Czech",
    "hu": "Hungarian",
    "ro": "Romanian",
    "bg": "Bulgarian",
    "hr": "Croatian",
    "sk": "Slovak",
    "sl": "Slovenian",
    "et": "Estonian",
    "lv": "Latvian",
    "lt": "Lithuanian",
    "el": "Greek",
    "is": "Icelandic",
    "ga": "Irish",
    "cy": "Welsh",
    "mt": "Maltese",
    "eu": "Basque",
    "ca": "Catalan",
    "gl": "Galician"
}

# Common script subtags
SCRIPT_SUBTAGS = {
    "Latn": "Latin",
    "Cyrl": "Cyrillic",
    "Arab": "Arabic",
    "Hani": "Han",
    "Hira": "Hiragana",
    "Kana": "Katakana",
    "Hang": "Hangul",
    "Deva": "Devanagari",
    "Thai": "Thai",
    "Grek": "Greek",
    "Hebr": "Hebrew",
    "Armn": "Armenian",
    "Geor": "Georgian",
    "Ethi": "Ethiopic",
    "Taml": "Tamil",
    "Telu": "Telugu",
    "Gujr": "Gujarati",
    "Beng": "Bengali",
    "Orya": "Oriya",
    "Mlym": "Malayalam",
    "Knda": "Kannada",
    "Sinh": "Sinhala",
    "Tibt": "Tibetan",
    "Mong": "Mongolian",
    "Laoo": "Lao",
    "Khmr": "Khmer",
    "Mymr": "Myanmar"
}

# Common region subtags
REGION_SUBTAGS = {
    "US": "United States",
    "GB": "United Kingdom",
    "CA": "Canada",
    "AU": "Australia",
    "NZ": "New Zealand",
    "IE": "Ireland",
    "ZA": "South Africa",
    "IN": "India",
    "PK": "Pakistan",
    "BD": "Bangladesh",
    "LK": "Sri Lanka",
    "NP": "Nepal",
    "BT": "Bhutan",
    "MV": "Maldives",
    "ES": "Spain",
    "MX": "Mexico",
    "AR": "Argentina",
    "BR": "Brazil",
    "CL": "Chile",
    "CO": "Colombia",
    "PE": "Peru",
    "VE": "Venezuela",
    "UY": "Uruguay",
    "PY": "Paraguay",
    "BO": "Bolivia",
    "EC": "Ecuador",
    "GY": "Guyana",
    "SR": "Suriname",
    "FR": "France",
    "DE": "Germany",
    "IT": "Italy",
    "PT": "Portugal",
    "NL": "Netherlands",
    "BE": "Belgium",
    "CH": "Switzerland",
    "AT": "Austria",
    "LU": "Luxembourg",
    "LI": "Liechtenstein",
    "MC": "Monaco",
    "AD": "Andorra",
    "SM": "San Marino",
    "VA": "Vatican City",
    "RU": "Russia",
    "CN": "China",
    "JP": "Japan",
    "KR": "South Korea",
    "KP": "North Korea",
    "TW": "Taiwan",
    "HK": "Hong Kong",
    "MO": "Macau",
    "SG": "Singapore",
    "MY": "Malaysia",
    "TH": "Thailand",
    "VN": "Vietnam",
    "LA": "Laos",
    "KH": "Cambodia",
    "MM": "Myanmar",
    "ID": "Indonesia",
    "PH": "Philippines",
    "BN": "Brunei",
    "TL": "East Timor",
    "SA": "Saudi Arabia",
    "AE": "United Arab Emirates",
    "QA": "Qatar",
    "KW": "Kuwait",
    "BH": "Bahrain",
    "OM": "Oman",
    "YE": "Yemen",
    "IQ": "Iraq",
    "IR": "Iran",
    "AF": "Afghanistan",
    "PK": "Pakistan",
    "BD": "Bangladesh",
    "LK": "Sri Lanka",
    "NP": "Nepal",
    "BT": "Bhutan",
    "MV": "Maldives"
}

def parse_language_tag(tag: str) -> Optional[LanguageTag]:
    """Parse a BCP-47 language tag into components."""
    if not tag or not isinstance(tag, str):
        return None
    
    # Normalize the tag
    tag = tag.strip().lower()
    
    # Split by hyphens
    parts = tag.split('-')
    
    if not parts or not parts[0]:
        return None
    
    language_tag = LanguageTag(language=parts[0])
    
    # Process remaining parts
    i = 1
    while i < len(parts):
        part = parts[i]
        
        # Script (4 characters, title case)
        if len(part) == 4 and part.isalpha():
            language_tag.script = part.title()
            i += 1
        # Region (2 characters, uppercase)
        elif len(part) == 2 and part.isalpha():
            language_tag.region = part.upper()
            i += 1
        # Variant (5-8 characters or 4 characters starting with digit)
        elif len(part) >= 4 and (len(part) <= 8 or (len(part) == 4 and part[0].isdigit())):
            language_tag.variant = part
            i += 1
        # Extension (single character + hyphen)
        elif len(part) == 1 and part.isalpha():
            if i + 1 < len(parts):
                language_tag.extension = f"{part}-{parts[i + 1]}"
                i += 2
            else:
                break
        # Private use (x + hyphen)
        elif part == 'x' and i + 1 < len(parts):
            language_tag.private_use = '-'.join(parts[i:])
            break
        else:
            # Unknown format, stop parsing
            break
    
    return language_tag

def validate_language_tag(tag: str) -> Dict[str, Any]:
    """Validate a BCP-47 language tag and return validation results."""
    result = {
        "valid": False,
        "canonical": None,
        "errors": [],
        "warnings": [],
        "components": {}
    }
    
    if not tag:
        result["errors"].append("Empty language tag")
        return result
    
    parsed = parse_language_tag(tag)
    if not parsed:
        result["errors"].append("Invalid language tag format")
        return result
    
    result["components"] = {
        "language": parsed.language,
        "script": parsed.script,
        "region": parsed.region,
        "variant": parsed.variant,
        "extension": parsed.extension,
        "private_use": parsed.private_use
    }
    
    # Validate language subtag
    if parsed.language not in LANGUAGE_SUBTAGS:
        result["warnings"].append(f"Unknown language subtag: {parsed.language}")
    
    # Validate script subtag
    if parsed.script and parsed.script not in SCRIPT_SUBTAGS:
        result["warnings"].append(f"Unknown script subtag: {parsed.script}")
    
    # Validate region subtag
    if parsed.region and parsed.region not in REGION_SUBTAGS:
        result["warnings"].append(f"Unknown region subtag: {parsed.region}")
    
    # Check for common issues
    if parsed.language == "en" and parsed.region == "US" and not parsed.script:
        result["warnings"].append("Consider adding script subtag for clarity")
    
    # Generate canonical form
    canonical_parts = [parsed.language]
    if parsed.script:
        canonical_parts.append(parsed.script)
    if parsed.region:
        canonical_parts.append(parsed.region)
    if parsed.variant:
        canonical_parts.append(parsed.variant)
    if parsed.extension:
        canonical_parts.append(parsed.extension)
    if parsed.private_use:
        canonical_parts.append(parsed.private_use)
    
    result["canonical"] = "-".join(canonical_parts)
    result["valid"] = len(result["errors"]) == 0
    
    return result

def get_language_name(tag: str) -> Optional[str]:
    """Get the human-readable name of a language tag."""
    parsed = parse_language_tag(tag)
    if not parsed:
        return None
    
    return LANGUAGE_SUBTAGS.get(parsed.language)

def get_region_name(tag: str) -> Optional[str]:
    """Get the human-readable name of the region in a language tag."""
    parsed = parse_language_tag(tag)
    if not parsed or not parsed.region:
        return None
    
    return REGION_SUBTAGS.get(parsed.region)

def get_script_name(tag: str) -> Optional[str]:
    """Get the human-readable name of the script in a language tag."""
    parsed = parse_language_tag(tag)
    if not parsed or not parsed.script:
        return None
    
    return SCRIPT_SUBTAGS.get(parsed.script)

def is_valid_language_tag(tag: str) -> bool:
    """Check if a language tag is valid."""
    return validate_language_tag(tag)["valid"]

def canonicalize_language_tag(tag: str) -> Optional[str]:
    """Canonicalize a language tag to its standard form."""
    validation = validate_language_tag(tag)
    return validation["canonical"] if validation["valid"] else None

def get_common_language_tags() -> List[str]:
    """Get a list of common language tags."""
    return list(LANGUAGE_SUBTAGS.keys())

def suggest_language_tag(partial_tag: str) -> List[str]:
    """Suggest complete language tags based on partial input."""
    suggestions = []
    partial = partial_tag.lower()
    
    for tag in LANGUAGE_SUBTAGS.keys():
        if tag.startswith(partial):
            suggestions.append(tag)
    
    return suggestions[:10]  # Limit to 10 suggestions
