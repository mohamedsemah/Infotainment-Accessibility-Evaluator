"""
DOM builder service for constructing DOM trees from HTML/QML files.
"""

import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag, NavigableString
import xml.etree.ElementTree as ET
import re

@dataclass
class DOMNode:
    """Represents a DOM node with accessibility information."""
    tag: str
    attributes: Dict[str, str]
    text_content: str
    children: List['DOMNode']
    parent: Optional['DOMNode'] = None
    line_number: int = 0
    column_number: int = 0
    xpath: str = ""
    computed_styles: Dict[str, str] = None
    accessibility_info: Dict[str, Any] = None

class DOMBuilder:
    """Service for building DOM trees from HTML/QML files."""
    
    def __init__(self):
        self.html_parser = 'html.parser'
        self.xml_parser = 'xml'
    
    async def build_dom(self, file_path: str, file_content: str) -> Optional[DOMNode]:
        """Build DOM tree from file content."""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext in ['.html', '.htm', '.xhtml']:
                return await self._build_html_dom(file_content, file_path)
            elif file_ext == '.qml':
                return await self._build_qml_dom(file_content, file_path)
            elif file_ext == '.xml':
                return await self._build_xml_dom(file_content, file_path)
            else:
                return None
                
        except Exception as e:
            print(f"Error building DOM for {file_path}: {e}")
            return None
    
    async def _build_html_dom(self, content: str, file_path: str) -> DOMNode:
        """Build DOM from HTML content."""
        soup = BeautifulSoup(content, self.html_parser)
        
        # Find root element (html or body)
        root_element = soup.find('html') or soup.find('body') or soup
        if not root_element:
            return None
        
        return await self._build_node_from_element(root_element, file_path, "")
    
    async def _build_qml_dom(self, content: str, file_path: str) -> DOMNode:
        """Build DOM from QML content."""
        # QML is XML-like, so we can parse it as XML
        try:
            root = ET.fromstring(content)
            return await self._build_node_from_xml_element(root, file_path, "")
        except ET.ParseError:
            # Fallback: treat as text and extract basic structure
            return await self._build_qml_fallback_dom(content, file_path)
    
    async def _build_xml_dom(self, content: str, file_path: str) -> DOMNode:
        """Build DOM from XML content."""
        try:
            root = ET.fromstring(content)
            return await self._build_node_from_xml_element(root, file_path, "")
        except ET.ParseError:
            return None
    
    async def _build_node_from_element(self, element: Tag, file_path: str, xpath: str) -> DOMNode:
        """Build DOMNode from BeautifulSoup element."""
        # Get element attributes
        attributes = {}
        if hasattr(element, 'attrs'):
            attributes = dict(element.attrs)
        
        # Get text content
        text_content = element.get_text(strip=True) if hasattr(element, 'get_text') else ""
        
        # Get line number if available
        line_number = getattr(element, 'sourceline', 0)
        column_number = getattr(element, 'sourcepos', 0)
        
        # Build children
        children = []
        if hasattr(element, 'children'):
            for i, child in enumerate(element.children):
                if isinstance(child, Tag):
                    child_xpath = f"{xpath}/{child.name}[{i+1}]"
                    child_node = await self._build_node_from_element(child, file_path, child_xpath)
                    child_node.parent = None  # Will be set after creation
                    children.append(child_node)
                elif isinstance(child, NavigableString) and child.strip():
                    # Create text node
                    text_node = DOMNode(
                        tag="text",
                        attributes={},
                        text_content=child.strip(),
                        children=[],
                        line_number=line_number,
                        xpath=f"{xpath}/text()[{i+1}]"
                    )
                    children.append(text_node)
        
        # Create DOMNode
        node = DOMNode(
            tag=element.name if hasattr(element, 'name') else "unknown",
            attributes=attributes,
            text_content=text_content,
            children=children,
            line_number=line_number,
            column_number=column_number,
            xpath=xpath
        )
        
        # Set parent references
        for child in children:
            child.parent = node
        
        # Add accessibility information
        node.accessibility_info = await self._extract_accessibility_info(node)
        
        return node
    
    async def _build_node_from_xml_element(self, element: ET.Element, file_path: str, xpath: str) -> DOMNode:
        """Build DOMNode from XML element."""
        # Get element attributes
        attributes = dict(element.attrib)
        
        # Get text content
        text_content = element.text.strip() if element.text else ""
        
        # Build children
        children = []
        for i, child in enumerate(element):
            child_xpath = f"{xpath}/{child.tag}[{i+1}]"
            child_node = await self._build_node_from_xml_element(child, file_path, child_xpath)
            child_node.parent = None  # Will be set after creation
            children.append(child_node)
        
        # Create DOMNode
        node = DOMNode(
            tag=element.tag,
            attributes=attributes,
            text_content=text_content,
            children=children,
            xpath=xpath
        )
        
        # Set parent references
        for child in children:
            child.parent = node
        
        # Add accessibility information
        node.accessibility_info = await self._extract_accessibility_info(node)
        
        return node
    
    async def _build_qml_fallback_dom(self, content: str, file_path: str) -> DOMNode:
        """Fallback DOM building for QML files."""
        # Extract basic QML structure using regex
        lines = content.split('\n')
        root_node = DOMNode(
            tag="qml",
            attributes={},
            text_content="",
            children=[],
            xpath="/qml"
        )
        
        # Simple QML parsing - look for common patterns
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            # Look for property definitions
            if ':' in line and not line.startswith('import'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    prop_name = parts[0].strip()
                    prop_value = parts[1].strip().rstrip(',')
                    
                    # Create property node
                    prop_node = DOMNode(
                        tag="property",
                        attributes={"name": prop_name, "value": prop_value},
                        text_content=prop_value,
                        children=[],
                        line_number=i + 1,
                        xpath=f"/qml/property[{len(root_node.children) + 1}]"
                    )
                    prop_node.parent = root_node
                    root_node.children.append(prop_node)
        
        return root_node
    
    async def _extract_accessibility_info(self, node: DOMNode) -> Dict[str, Any]:
        """Extract accessibility information from a DOM node."""
        info = {
            "has_aria_label": False,
            "has_aria_labelledby": False,
            "has_aria_describedby": False,
            "has_role": False,
            "has_tabindex": False,
            "is_interactive": False,
            "is_heading": False,
            "is_landmark": False,
            "is_form_control": False,
            "is_image": False,
            "is_link": False,
            "is_button": False,
            "has_alt_text": False,
            "has_title": False,
            "is_focusable": False,
            "is_visible": True,
            "is_hidden": False
        }
        
        # Check ARIA attributes
        if "aria-label" in node.attributes:
            info["has_aria_label"] = True
        if "aria-labelledby" in node.attributes:
            info["has_aria_labelledby"] = True
        if "aria-describedby" in node.attributes:
            info["has_aria_describedby"] = True
        if "role" in node.attributes:
            info["has_role"] = True
        
        # Check interactive elements
        if "tabindex" in node.attributes:
            info["has_tabindex"] = True
            info["is_focusable"] = True
        
        # Check element types
        if node.tag in ["button", "input", "select", "textarea"]:
            info["is_interactive"] = True
            info["is_focusable"] = True
        
        if node.tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            info["is_heading"] = True
        
        if node.tag in ["main", "nav", "aside", "section", "article", "header", "footer"]:
            info["is_landmark"] = True
        
        if node.tag in ["input", "select", "textarea", "button"]:
            info["is_form_control"] = True
        
        if node.tag == "img":
            info["is_image"] = True
            if "alt" in node.attributes and node.attributes["alt"]:
                info["has_alt_text"] = True
        
        if node.tag == "a":
            info["is_link"] = True
            info["is_focusable"] = True
        
        if node.tag == "button":
            info["is_button"] = True
            info["is_focusable"] = True
        
        # Check for title attribute
        if "title" in node.attributes:
            info["has_title"] = True
        
        # Check for hidden elements
        if "hidden" in node.attributes or "style" in node.attributes:
            style = node.attributes.get("style", "")
            if "display: none" in style or "visibility: hidden" in style:
                info["is_hidden"] = True
                info["is_visible"] = False
        
        return info
    
    def find_nodes_by_selector(self, root: DOMNode, selector: str) -> List[DOMNode]:
        """Find nodes matching a CSS selector."""
        # Simple selector implementation
        if selector.startswith('#'):
            # ID selector
            id_value = selector[1:]
            return self._find_nodes_by_id(root, id_value)
        elif selector.startswith('.'):
            # Class selector
            class_value = selector[1:]
            return self._find_nodes_by_class(root, class_value)
        else:
            # Tag selector
            return self._find_nodes_by_tag(root, selector)
    
    def _find_nodes_by_id(self, root: DOMNode, id_value: str) -> List[DOMNode]:
        """Find nodes by ID."""
        results = []
        if root.attributes.get("id") == id_value:
            results.append(root)
        
        for child in root.children:
            results.extend(self._find_nodes_by_id(child, id_value))
        
        return results
    
    def _find_nodes_by_class(self, root: DOMNode, class_value: str) -> List[DOMNode]:
        """Find nodes by class."""
        results = []
        classes = root.attributes.get("class", "").split()
        if class_value in classes:
            results.append(root)
        
        for child in root.children:
            results.extend(self._find_nodes_by_class(child, class_value))
        
        return results
    
    def _find_nodes_by_tag(self, root: DOMNode, tag: str) -> List[DOMNode]:
        """Find nodes by tag."""
        results = []
        if root.tag == tag:
            results.append(root)
        
        for child in root.children:
            results.extend(self._find_nodes_by_tag(child, tag))
        
        return results
    
    def get_node_xpath(self, node: DOMNode) -> str:
        """Get XPath for a node."""
        return node.xpath
    
    def get_node_line_number(self, node: DOMNode) -> int:
        """Get line number for a node."""
        return node.line_number

