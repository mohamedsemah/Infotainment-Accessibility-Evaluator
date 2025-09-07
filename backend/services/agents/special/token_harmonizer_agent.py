"""
TokenHarmonizerAgent - Recommends design-token-level fixes for repeated patterns.
"""

import os
import re
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict, Counter
from pathlib import Path

from models.schemas import Finding, Cluster, Patch, PatchType, SeverityLevel, ConfidenceLevel
from utils.id_gen import generate_patch_id

class TokenHarmonizerAgent:
    """Agent responsible for harmonizing design tokens and recommending fixes."""
    
    def __init__(self):
        self.findings = []
        self.clusters = []
        self.patches = []
        self.design_tokens = {}
    
    async def analyze(self, clusters: List[Cluster], upload_path: str) -> List[Patch]:
        """Analyze clusters and recommend design token fixes."""
        self.clusters = clusters
        self.patches = []
        
        # Extract design tokens from clusters
        await self._extract_design_tokens()
        
        # Analyze token patterns
        await self._analyze_token_patterns()
        
        # Generate patches for token harmonization
        await self._generate_token_patches()
        
        return self.patches
    
    async def _extract_design_tokens(self):
        """Extract design tokens from clusters."""
        self.design_tokens = {
            'colors': defaultdict(list),
            'spacing': defaultdict(list),
            'typography': defaultdict(list),
            'sizing': defaultdict(list),
            'shadows': defaultdict(list),
            'borders': defaultdict(list)
        }
        
        for cluster in self.clusters:
            await self._extract_tokens_from_cluster(cluster)
    
    async def _extract_tokens_from_cluster(self, cluster: Cluster):
        """Extract tokens from a specific cluster."""
        for finding in cluster.occurrences:
            # Extract tokens based on criterion
            if cluster.criterion.value == 'contrast':
                await self._extract_contrast_tokens(finding, cluster)
            elif cluster.criterion.value == 'seizure_safe':
                await self._extract_animation_tokens(finding, cluster)
            elif cluster.criterion.value == 'language':
                await self._extract_language_tokens(finding, cluster)
            elif cluster.criterion.value == 'aria':
                await self._extract_aria_tokens(finding, cluster)
            elif cluster.criterion.value == 'state_explorer':
                await self._extract_state_tokens(finding, cluster)
    
    async def _extract_contrast_tokens(self, finding: Finding, cluster: Cluster):
        """Extract color tokens from contrast findings."""
        for evidence in finding.evidence:
            if evidence.metrics:
                # Extract foreground and background colors
                fg_color = evidence.metrics.get('foreground', {}).get('hex', '')
                bg_color = evidence.metrics.get('background', {}).get('hex', '')
                
                if fg_color:
                    self.design_tokens['colors'][fg_color].append({
                        'finding': finding,
                        'cluster': cluster,
                        'type': 'foreground',
                        'context': finding.selector
                    })
                
                if bg_color:
                    self.design_tokens['colors'][bg_color].append({
                        'finding': finding,
                        'cluster': cluster,
                        'type': 'background',
                        'context': finding.selector
                    })
    
    async def _extract_animation_tokens(self, finding: Finding, cluster: Cluster):
        """Extract animation tokens from seizure findings."""
        for evidence in finding.evidence:
            if evidence.metrics:
                # Extract animation properties
                duration = evidence.metrics.get('duration', '')
                frequency = evidence.metrics.get('frequency', '')
                animation_type = evidence.metrics.get('animation_type', '')
                
                if duration:
                    self.design_tokens['sizing'][f'duration-{duration}'].append({
                        'finding': finding,
                        'cluster': cluster,
                        'type': 'duration',
                        'context': finding.selector
                    })
                
                if frequency:
                    self.design_tokens['sizing'][f'frequency-{frequency}'].append({
                        'finding': finding,
                        'cluster': cluster,
                        'type': 'frequency',
                        'context': finding.selector
                    })
    
    async def _extract_language_tokens(self, finding: Finding, cluster: Cluster):
        """Extract language tokens from language findings."""
        for evidence in finding.evidence:
            if evidence.metrics:
                # Extract language values
                lang_value = evidence.metrics.get('lang_value', '')
                scope = evidence.metrics.get('scope', '')
                
                if lang_value:
                    self.design_tokens['typography'][f'lang-{lang_value}'].append({
                        'finding': finding,
                        'cluster': cluster,
                        'type': 'language',
                        'context': finding.selector
                    })
    
    async def _extract_aria_tokens(self, finding: Finding, cluster: Cluster):
        """Extract ARIA tokens from ARIA findings."""
        for evidence in finding.evidence:
            if evidence.metrics:
                # Extract ARIA attributes
                role = evidence.metrics.get('role', '')
                attribute = evidence.metrics.get('attribute', '')
                
                if role:
                    self.design_tokens['typography'][f'role-{role}'].append({
                        'finding': finding,
                        'cluster': cluster,
                        'type': 'role',
                        'context': finding.selector
                    })
    
    async def _extract_state_tokens(self, finding: Finding, cluster: Cluster):
        """Extract state tokens from state findings."""
        for evidence in finding.evidence:
            if evidence.metrics:
                # Extract state properties
                state = evidence.metrics.get('state', '')
                component = evidence.metrics.get('component', '')
                
                if state:
                    self.design_tokens['sizing'][f'state-{state}'].append({
                        'finding': finding,
                        'cluster': cluster,
                        'type': 'state',
                        'context': finding.selector
                    })
    
    async def _analyze_token_patterns(self):
        """Analyze patterns in design tokens."""
        # Find frequently used tokens
        frequent_tokens = {}
        
        for token_type, tokens in self.design_tokens.items():
            for token_value, occurrences in tokens.items():
                if len(occurrences) >= 3:  # Threshold for frequent usage
                    frequent_tokens[token_value] = {
                        'type': token_type,
                        'count': len(occurrences),
                        'occurrences': occurrences
                    }
        
        # Store frequent tokens for patch generation
        self.frequent_tokens = frequent_tokens
    
    async def _generate_token_patches(self):
        """Generate patches for token harmonization."""
        # Generate patches for frequent color tokens
        await self._generate_color_token_patches()
        
        # Generate patches for frequent animation tokens
        await self._generate_animation_token_patches()
        
        # Generate patches for frequent typography tokens
        await self._generate_typography_token_patches()
        
        # Generate patches for frequent sizing tokens
        await self._generate_sizing_token_patches()
    
    async def _generate_color_token_patches(self):
        """Generate patches for color token harmonization."""
        color_tokens = {k: v for k, v in self.frequent_tokens.items() if v['type'] == 'colors'}
        
        for token_value, token_info in color_tokens.items():
            # Group by color type (foreground/background)
            fg_occurrences = [occ for occ in token_info['occurrences'] if occ['type'] == 'foreground']
            bg_occurrences = [occ for occ in token_info['occurrences'] if occ['type'] == 'background']
            
            if fg_occurrences:
                await self._create_color_token_patch(token_value, fg_occurrences, 'foreground')
            
            if bg_occurrences:
                await self._create_color_token_patch(token_value, bg_occurrences, 'background')
    
    async def _generate_animation_token_patches(self):
        """Generate patches for animation token harmonization."""
        animation_tokens = {k: v for k, v in self.frequent_tokens.items() if v['type'] == 'sizing' and 'duration' in k}
        
        for token_value, token_info in animation_tokens.items():
            await self._create_animation_token_patch(token_value, token_info['occurrences'])
    
    async def _generate_typography_token_patches(self):
        """Generate patches for typography token harmonization."""
        typography_tokens = {k: v for k, v in self.frequent_tokens.items() if v['type'] == 'typography'}
        
        for token_value, token_info in typography_tokens.items():
            await self._create_typography_token_patch(token_value, token_info['occurrences'])
    
    async def _generate_sizing_token_patches(self):
        """Generate patches for sizing token harmonization."""
        sizing_tokens = {k: v for k, v in self.frequent_tokens.items() if v['type'] == 'sizing' and 'duration' not in k}
        
        for token_value, token_info in sizing_tokens.items():
            await self._create_sizing_token_patch(token_value, token_info['occurrences'])
    
    async def _create_color_token_patch(self, color_value: str, occurrences: List[Dict], color_type: str):
        """Create a color token patch."""
        patch_id = generate_patch_id()
        
        # Generate CSS custom property
        token_name = f"--color-{color_type}-{color_value[1:]}"
        
        # Create CSS patch
        css_patch = f"""
/* Design Token: {token_name} */
:root {{
    {token_name}: {color_value};
}}

/* Apply token to affected elements */
"""
        
        # Add selectors for affected elements
        selectors = set()
        for occ in occurrences:
            selectors.add(occ['context'])
        
        for selector in selectors:
            if color_type == 'foreground':
                css_patch += f"{selector} {{ color: var({token_name}); }}\n"
            else:
                css_patch += f"{selector} {{ background-color: var({token_name}); }}\n"
        
        # Create patch
        patch = Patch(
            id=patch_id,
            type=PatchType.CSS_UPDATE,
            file_path="design-tokens.css",
            diff=css_patch,
            rationale=f"Create design token for {color_type} color {color_value} used in {len(occurrences)} places",
            risks=["May affect other elements using the same color", "Requires testing across all states"],
            confidence=ConfidenceLevel.HIGH
        )
        
        self.patches.append(patch)
    
    async def _create_animation_token_patch(self, token_value: str, occurrences: List[Dict]):
        """Create an animation token patch."""
        patch_id = generate_patch_id()
        
        # Extract duration from token value
        duration = token_value.replace('duration-', '')
        
        # Generate CSS custom property
        token_name = f"--animation-duration-{duration}"
        
        # Create CSS patch
        css_patch = f"""
/* Design Token: {token_name} */
:root {{
    {token_name}: {duration}ms;
}}

/* Apply token to affected elements */
"""
        
        # Add selectors for affected elements
        selectors = set()
        for occ in occurrences:
            selectors.add(occ['context'])
        
        for selector in selectors:
            css_patch += f"{selector} {{ animation-duration: var({token_name}); }}\n"
        
        # Create patch
        patch = Patch(
            id=patch_id,
            type=PatchType.CSS_UPDATE,
            file_path="design-tokens.css",
            diff=css_patch,
            rationale=f"Create design token for animation duration {duration}ms used in {len(occurrences)} places",
            risks=["May affect animation timing", "Requires testing across all states"],
            confidence=ConfidenceLevel.HIGH
        )
        
        self.patches.append(patch)
    
    async def _create_typography_token_patch(self, token_value: str, occurrences: List[Dict]):
        """Create a typography token patch."""
        patch_id = generate_patch_id()
        
        # Generate CSS custom property
        token_name = f"--typography-{token_value.replace('-', '-')}"
        
        # Create CSS patch
        css_patch = f"""
/* Design Token: {token_name} */
:root {{
    {token_name}: {token_value};
}}

/* Apply token to affected elements */
"""
        
        # Add selectors for affected elements
        selectors = set()
        for occ in occurrences:
            selectors.add(occ['context'])
        
        for selector in selectors:
            css_patch += f"{selector} {{ font-family: var({token_name}); }}\n"
        
        # Create patch
        patch = Patch(
            id=patch_id,
            type=PatchType.CSS_UPDATE,
            file_path="design-tokens.css",
            diff=css_patch,
            rationale=f"Create design token for typography {token_value} used in {len(occurrences)} places",
            risks=["May affect text rendering", "Requires testing across all languages"],
            confidence=ConfidenceLevel.MEDIUM
        )
        
        self.patches.append(patch)
    
    async def _create_sizing_token_patch(self, token_value: str, occurrences: List[Dict]):
        """Create a sizing token patch."""
        patch_id = generate_patch_id()
        
        # Generate CSS custom property
        token_name = f"--sizing-{token_value.replace('-', '-')}"
        
        # Create CSS patch
        css_patch = f"""
/* Design Token: {token_name} */
:root {{
    {token_name}: {token_value};
}}

/* Apply token to affected elements */
"""
        
        # Add selectors for affected elements
        selectors = set()
        for occ in occurrences:
            selectors.add(occ['context'])
        
        for selector in selectors:
            css_patch += f"{selector} {{ size: var({token_name}); }}\n"
        
        # Create patch
        patch = Patch(
            id=patch_id,
            type=PatchType.CSS_UPDATE,
            file_path="design-tokens.css",
            diff=css_patch,
            rationale=f"Create design token for sizing {token_value} used in {len(occurrences)} places",
            risks=["May affect layout", "Requires testing across all screen sizes"],
            confidence=ConfidenceLevel.MEDIUM
        )
        
        self.patches.append(patch)
    
    async def _create_comprehensive_token_patch(self):
        """Create a comprehensive design token patch."""
        patch_id = generate_patch_id()
        
        # Generate comprehensive CSS custom properties
        css_patch = """
/* Comprehensive Design Token System */
:root {
    /* Color Tokens */
    --color-primary: #007bff;
    --color-secondary: #6c757d;
    --color-success: #28a745;
    --color-danger: #dc3545;
    --color-warning: #ffc107;
    --color-info: #17a2b8;
    --color-light: #f8f9fa;
    --color-dark: #343a40;
    
    /* Typography Tokens */
    --font-family-sans-serif: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --font-family-monospace: SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    
    /* Spacing Tokens */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 3rem;
    
    /* Animation Tokens */
    --animation-duration-fast: 150ms;
    --animation-duration-normal: 300ms;
    --animation-duration-slow: 500ms;
    
    /* Border Tokens */
    --border-width: 1px;
    --border-style: solid;
    --border-radius: 0.25rem;
    
    /* Shadow Tokens */
    --shadow-sm: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    --shadow-md: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    --shadow-lg: 0 1rem 3rem rgba(0, 0, 0, 0.175);
}
"""
        
        # Create patch
        patch = Patch(
            id=patch_id,
            type=PatchType.CSS_UPDATE,
            file_path="design-tokens.css",
            diff=css_patch,
            rationale="Create comprehensive design token system for consistent styling",
            risks=["May conflict with existing styles", "Requires migration of existing code"],
            confidence=ConfidenceLevel.MEDIUM
        )
        
        self.patches.append(patch)
