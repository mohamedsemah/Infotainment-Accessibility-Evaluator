"""
ARIA role and attribute mappings for accessibility validation.
"""

from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass

@dataclass
class ARIARole:
    """Represents an ARIA role with its properties."""
    name: str
    category: str
    required_attributes: Set[str]
    optional_attributes: Set[str]
    prohibited_attributes: Set[str]
    required_children: Set[str]
    required_parent: Optional[str]
    abstract: bool = False

@dataclass
class ARIAAttribute:
    """Represents an ARIA attribute with its properties."""
    name: str
    type: str  # string, boolean, number, token, tokenlist, id, idlist, etc.
    values: Optional[List[str]] = None
    required: bool = False
    global_attribute: bool = False

# ARIA Role Categories
ROLE_CATEGORIES = {
    "widget": "Interactive components that users can interact with",
    "composite": "Components that contain other components",
    "document": "Components that structure content",
    "landmark": "Components that identify regions of a page",
    "live_region": "Components that announce changes to screen readers",
    "window": "Components that create separate windows or dialogs"
}

# ARIA Roles Database
ARIA_ROLES = {
    # Widget Roles
    "button": ARIARole(
        name="button",
        category="widget",
        required_attributes=set(),
        optional_attributes={"aria-expanded", "aria-pressed", "aria-haspopup", "aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "checkbox": ARIARole(
        name="checkbox",
        category="widget",
        required_attributes=set(),
        optional_attributes={"aria-checked", "aria-required", "aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "radio": ARIARole(
        name="radio",
        category="widget",
        required_attributes=set(),
        optional_attributes={"aria-checked", "aria-required", "aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent="radiogroup"
    ),
    "switch": ARIARole(
        name="switch",
        category="widget",
        required_attributes=set(),
        optional_attributes={"aria-checked", "aria-required", "aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "slider": ARIARole(
        name="slider",
        category="widget",
        required_attributes=set(),
        optional_attributes={"aria-valuemin", "aria-valuemax", "aria-valuenow", "aria-valuetext", "aria-orientation", "aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "progressbar": ARIARole(
        name="progressbar",
        category="widget",
        required_attributes=set(),
        optional_attributes={"aria-valuemin", "aria-valuemax", "aria-valuenow", "aria-valuetext", "aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "textbox": ARIARole(
        name="textbox",
        category="widget",
        required_attributes=set(),
        optional_attributes={"aria-multiline", "aria-readonly", "aria-required", "aria-placeholder", "aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "combobox": ARIARole(
        name="combobox",
        category="composite",
        required_attributes=set(),
        optional_attributes={"aria-expanded", "aria-required", "aria-haspopup", "aria-autocomplete", "aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "listbox": ARIARole(
        name="listbox",
        category="composite",
        required_attributes=set(),
        optional_attributes={"aria-multiselectable", "aria-required", "aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children={"option"},
        required_parent=None
    ),
    "menu": ARIARole(
        name="menu",
        category="composite",
        required_attributes=set(),
        optional_attributes={"aria-activedescendant", "aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children={"menuitem", "menuitemcheckbox", "menuitemradio", "menuseparator"},
        required_parent=None
    ),
    "menubar": ARIARole(
        name="menubar",
        category="composite",
        required_attributes=set(),
        optional_attributes={"aria-activedescendant", "aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children={"menuitem", "menuitemcheckbox", "menuitemradio", "menuseparator"},
        required_parent=None
    ),
    "tablist": ARIARole(
        name="tablist",
        category="composite",
        required_attributes=set(),
        optional_attributes={"aria-activedescendant", "aria-orientation", "aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children={"tab"},
        required_parent=None
    ),
    "tree": ARIARole(
        name="tree",
        category="composite",
        required_attributes=set(),
        optional_attributes={"aria-multiselectable", "aria-activedescendant", "aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children={"treeitem"},
        required_parent=None
    ),
    "grid": ARIARole(
        name="grid",
        category="composite",
        required_attributes=set(),
        optional_attributes={"aria-multiselectable", "aria-activedescendant", "aria-level", "aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children={"row"},
        required_parent=None
    ),
    
    # Document Structure Roles
    "article": ARIARole(
        name="article",
        category="document",
        required_attributes=set(),
        optional_attributes={"aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "heading": ARIARole(
        name="heading",
        category="document",
        required_attributes={"aria-level"},
        optional_attributes={"aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "img": ARIARole(
        name="img",
        category="document",
        required_attributes=set(),
        optional_attributes={"aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "list": ARIARole(
        name="list",
        category="document",
        required_attributes=set(),
        optional_attributes={"aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children={"listitem"},
        required_parent=None
    ),
    "table": ARIARole(
        name="table",
        category="document",
        required_attributes=set(),
        optional_attributes={"aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children={"row"},
        required_parent=None
    ),
    
    # Landmark Roles
    "banner": ARIARole(
        name="banner",
        category="landmark",
        required_attributes=set(),
        optional_attributes={"aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "main": ARIARole(
        name="main",
        category="landmark",
        required_attributes=set(),
        optional_attributes={"aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "navigation": ARIARole(
        name="navigation",
        category="landmark",
        required_attributes=set(),
        optional_attributes={"aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "complementary": ARIARole(
        name="complementary",
        category="landmark",
        required_attributes=set(),
        optional_attributes={"aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "contentinfo": ARIARole(
        name="contentinfo",
        category="landmark",
        required_attributes=set(),
        optional_attributes={"aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "search": ARIARole(
        name="search",
        category="landmark",
        required_attributes=set(),
        optional_attributes={"aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    
    # Live Region Roles
    "alert": ARIARole(
        name="alert",
        category="live_region",
        required_attributes=set(),
        optional_attributes={"aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "status": ARIARole(
        name="status",
        category="live_region",
        required_attributes=set(),
        optional_attributes={"aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "log": ARIARole(
        name="log",
        category="live_region",
        required_attributes=set(),
        optional_attributes={"aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "timer": ARIARole(
        name="timer",
        category="live_region",
        required_attributes=set(),
        optional_attributes={"aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    
    # Window Roles
    "dialog": ARIARole(
        name="dialog",
        category="window",
        required_attributes=set(),
        optional_attributes={"aria-modal", "aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    ),
    "alertdialog": ARIARole(
        name="alertdialog",
        category="window",
        required_attributes=set(),
        optional_attributes={"aria-modal", "aria-describedby", "aria-label", "aria-labelledby"},
        prohibited_attributes=set(),
        required_children=set(),
        required_parent=None
    )
}

# ARIA Attributes Database
ARIA_ATTRIBUTES = {
    # Global Attributes
    "aria-label": ARIAAttribute(
        name="aria-label",
        type="string",
        global_attribute=True
    ),
    "aria-labelledby": ARIAAttribute(
        name="aria-labelledby",
        type="idlist",
        global_attribute=True
    ),
    "aria-describedby": ARIAAttribute(
        name="aria-describedby",
        type="idlist",
        global_attribute=True
    ),
    "aria-hidden": ARIAAttribute(
        name="aria-hidden",
        type="boolean",
        values=["true", "false"],
        global_attribute=True
    ),
    "aria-disabled": ARIAAttribute(
        name="aria-disabled",
        type="boolean",
        values=["true", "false"],
        global_attribute=True
    ),
    "aria-expanded": ARIAAttribute(
        name="aria-expanded",
        type="boolean",
        values=["true", "false", "undefined"],
        global_attribute=True
    ),
    "aria-selected": ARIAAttribute(
        name="aria-selected",
        type="boolean",
        values=["true", "false", "undefined"],
        global_attribute=True
    ),
    "aria-checked": ARIAAttribute(
        name="aria-checked",
        type="tristate",
        values=["true", "false", "mixed", "undefined"],
        global_attribute=True
    ),
    "aria-pressed": ARIAAttribute(
        name="aria-pressed",
        type="tristate",
        values=["true", "false", "mixed", "undefined"],
        global_attribute=True
    ),
    "aria-required": ARIAAttribute(
        name="aria-required",
        type="boolean",
        values=["true", "false"],
        global_attribute=True
    ),
    "aria-invalid": ARIAAttribute(
        name="aria-invalid",
        type="token",
        values=["true", "false", "grammar", "spelling"],
        global_attribute=True
    ),
    "aria-live": ARIAAttribute(
        name="aria-live",
        type="token",
        values=["off", "polite", "assertive"],
        global_attribute=True
    ),
    "aria-atomic": ARIAAttribute(
        name="aria-atomic",
        type="boolean",
        values=["true", "false"],
        global_attribute=True
    ),
    "aria-busy": ARIAAttribute(
        name="aria-busy",
        type="boolean",
        values=["true", "false"],
        global_attribute=True
    ),
    "aria-relevant": ARIAAttribute(
        name="aria-relevant",
        type="tokenlist",
        values=["additions", "removals", "text", "all"],
        global_attribute=True
    ),
    "aria-level": ARIAAttribute(
        name="aria-level",
        type="number",
        global_attribute=True
    ),
    "aria-posinset": ARIAAttribute(
        name="aria-posinset",
        type="number",
        global_attribute=True
    ),
    "aria-setsize": ARIAAttribute(
        name="aria-setsize",
        type="number",
        global_attribute=True
    ),
    "aria-valuemin": ARIAAttribute(
        name="aria-valuemin",
        type="number",
        global_attribute=True
    ),
    "aria-valuemax": ARIAAttribute(
        name="aria-valuemax",
        type="number",
        global_attribute=True
    ),
    "aria-valuenow": ARIAAttribute(
        name="aria-valuenow",
        type="number",
        global_attribute=True
    ),
    "aria-valuetext": ARIAAttribute(
        name="aria-valuetext",
        type="string",
        global_attribute=True
    ),
    "aria-orientation": ARIAAttribute(
        name="aria-orientation",
        type="token",
        values=["horizontal", "vertical"],
        global_attribute=True
    ),
    "aria-sort": ARIAAttribute(
        name="aria-sort",
        type="token",
        values=["ascending", "descending", "none", "other"],
        global_attribute=True
    ),
    "aria-haspopup": ARIAAttribute(
        name="aria-haspopup",
        type="token",
        values=["false", "true", "menu", "listbox", "tree", "grid", "dialog"],
        global_attribute=True
    ),
    "aria-activedescendant": ARIAAttribute(
        name="aria-activedescendant",
        type="id",
        global_attribute=True
    ),
    "aria-controls": ARIAAttribute(
        name="aria-controls",
        type="idlist",
        global_attribute=True
    ),
    "aria-owns": ARIAAttribute(
        name="aria-owns",
        type="idlist",
        global_attribute=True
    ),
    "aria-flowto": ARIAAttribute(
        name="aria-flowto",
        type="idlist",
        global_attribute=True
    ),
    "aria-details": ARIAAttribute(
        name="aria-details",
        type="id",
        global_attribute=True
    ),
    "aria-errormessage": ARIAAttribute(
        name="aria-errormessage",
        type="id",
        global_attribute=True
    ),
    "aria-keyshortcuts": ARIAAttribute(
        name="aria-keyshortcuts",
        type="string",
        global_attribute=True
    ),
    "aria-roledescription": ARIAAttribute(
        name="aria-roledescription",
        type="string",
        global_attribute=True
    ),
    "aria-autocomplete": ARIAAttribute(
        name="aria-autocomplete",
        type="token",
        values=["none", "inline", "list", "both"],
        global_attribute=True
    ),
    "aria-multiline": ARIAAttribute(
        name="aria-multiline",
        type="boolean",
        values=["true", "false"],
        global_attribute=True
    ),
    "aria-multiselectable": ARIAAttribute(
        name="aria-multiselectable",
        type="boolean",
        values=["true", "false"],
        global_attribute=True
    ),
    "aria-readonly": ARIAAttribute(
        name="aria-readonly",
        type="boolean",
        values=["true", "false"],
        global_attribute=True
    ),
    "aria-placeholder": ARIAAttribute(
        name="aria-placeholder",
        type="string",
        global_attribute=True
    ),
    "aria-modal": ARIAAttribute(
        name="aria-modal",
        type="boolean",
        values=["true", "false"],
        global_attribute=True
    )
}

def get_role(role_name: str) -> Optional[ARIARole]:
    """Get ARIA role information by name."""
    return ARIA_ROLES.get(role_name.lower())

def get_attribute(attr_name: str) -> Optional[ARIAAttribute]:
    """Get ARIA attribute information by name."""
    return ARIA_ATTRIBUTES.get(attr_name.lower())

def validate_role_attribute_combination(role: str, attribute: str) -> Dict[str, Any]:
    """Validate if an attribute is valid for a specific role."""
    result = {
        "valid": False,
        "required": False,
        "optional": False,
        "prohibited": False,
        "global": False
    }
    
    role_info = get_role(role)
    attr_info = get_attribute(attribute)
    
    if not role_info or not attr_info:
        return result
    
    # Check if it's a global attribute
    if attr_info.global_attribute:
        result["global"] = True
        result["valid"] = True
        result["optional"] = True
    
    # Check role-specific rules
    if attribute in role_info.required_attributes:
        result["valid"] = True
        result["required"] = True
    elif attribute in role_info.optional_attributes:
        result["valid"] = True
        result["optional"] = True
    elif attribute in role_info.prohibited_attributes:
        result["prohibited"] = True
    else:
        # If it's a global attribute and not explicitly prohibited, it's valid
        if attr_info.global_attribute:
            result["valid"] = True
            result["optional"] = True
    
    return result

def get_required_attributes_for_role(role: str) -> Set[str]:
    """Get required attributes for a specific role."""
    role_info = get_role(role)
    return role_info.required_attributes if role_info else set()

def get_optional_attributes_for_role(role: str) -> Set[str]:
    """Get optional attributes for a specific role."""
    role_info = get_role(role)
    return role_info.optional_attributes if role_info else set()

def get_prohibited_attributes_for_role(role: str) -> Set[str]:
    """Get prohibited attributes for a specific role."""
    role_info = get_role(role)
    return role_info.prohibited_attributes if role_info else set()

def validate_attribute_value(attribute: str, value: str) -> Dict[str, Any]:
    """Validate an attribute value against its type and allowed values."""
    result = {
        "valid": False,
        "type": None,
        "allowed_values": None,
        "error": None
    }
    
    attr_info = get_attribute(attribute)
    if not attr_info:
        result["error"] = "Unknown attribute"
        return result
    
    result["type"] = attr_info.type
    result["allowed_values"] = attr_info.values
    
    if attr_info.type == "boolean":
        result["valid"] = value.lower() in ["true", "false"]
    elif attr_info.type == "tristate":
        result["valid"] = value.lower() in ["true", "false", "mixed", "undefined"]
    elif attr_info.type == "token":
        result["valid"] = value.lower() in [v.lower() for v in (attr_info.values or [])]
    elif attr_info.type == "tokenlist":
        if attr_info.values:
            valid_values = [v.lower() for v in attr_info.values]
            result["valid"] = all(v.strip().lower() in valid_values for v in value.split())
        else:
            result["valid"] = True
    elif attr_info.type == "number":
        try:
            float(value)
            result["valid"] = True
        except ValueError:
            result["valid"] = False
    elif attr_info.type in ["string", "id", "idlist"]:
        result["valid"] = True  # String types are generally valid
    else:
        result["valid"] = True  # Unknown types are assumed valid
    
    return result

def get_roles_by_category(category: str) -> List[str]:
    """Get all roles in a specific category."""
    return [name for name, role in ARIA_ROLES.items() if role.category == category]

def get_global_attributes() -> List[str]:
    """Get all global ARIA attributes."""
    return [name for name, attr in ARIA_ATTRIBUTES.items() if attr.global_attribute]
