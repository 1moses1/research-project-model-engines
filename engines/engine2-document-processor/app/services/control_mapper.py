"""
Control Mapper Service
Maps extracted controls to Rwanda NCSA framework controls
"""

from typing import Dict, List, Optional
import json
import os
from pathlib import Path
from difflib import SequenceMatcher


class ControlMapper:
    """Maps extracted controls to Rwanda NCSA control taxonomy"""

    def __init__(self, taxonomy_path: Optional[str] = None):
        """
        Initialize control mapper with taxonomy

        Args:
            taxonomy_path: Path to control taxonomy JSON file
        """
        if taxonomy_path is None:
            # Use path from environment variable or default to local copy
            taxonomy_path = os.getenv(
                'CONTROL_TAXONOMY_PATH',
                '/app/data/control_taxonomy_validated.json'  # ENGINE 2 local copy
            )

        self.taxonomy_path = Path(taxonomy_path)
        self.controls = {}
        self.families = {}
        self.load_taxonomy()

    def load_taxonomy(self):
        """Load control taxonomy from JSON file"""
        try:
            if not self.taxonomy_path.exists():
                print(f"⚠️ Taxonomy file not found: {self.taxonomy_path}")
                print("⚠️ Using empty taxonomy")
                self.controls = {}
                self.families = {}
                return

            with open(self.taxonomy_path, 'r') as f:
                taxonomy_data = json.load(f)

            # Parse Rwanda NCSA controls (try both key names for compatibility)
            rwanda_key = 'rwanda' if 'rwanda' in taxonomy_data else 'rwanda_ncsa_controls'
            if rwanda_key in taxonomy_data:
                for control in taxonomy_data[rwanda_key]:
                    control_id = control['control_id']
                    self.controls[control_id] = control

                    # Index by family
                    family = control.get('family', 'Unknown')
                    if family not in self.families:
                        self.families[family] = []
                    self.families[family].append(control_id)

            # Also parse NIST controls if available (try both key names)
            nist_key = 'nist' if 'nist' in taxonomy_data else 'nist_controls'
            if nist_key in taxonomy_data:
                for control in taxonomy_data[nist_key]:
                    control_id = control['control_id']
                    if control_id not in self.controls:
                        self.controls[control_id] = control

                        family = control.get('family', 'Unknown')
                        if family not in self.families:
                            self.families[family] = []
                        self.families[family].append(control_id)

            print(f"✅ Loaded {len(self.controls)} controls from taxonomy")
            print(f"✅ Found {len(self.families)} control families")

        except Exception as e:
            print(f"⚠️ Error loading taxonomy: {str(e)}")
            self.controls = {}
            self.families = {}

    def find_matching_controls(
        self,
        extracted_controls: List[Dict],
        threshold: float = 0.6
    ) -> List[Dict]:
        """
        Find matching Rwanda NCSA controls for extracted controls

        Args:
            extracted_controls: List of controls extracted from document
            threshold: Similarity threshold (0.0-1.0)

        Returns:
            List of matched controls with mappings
        """
        matched_controls = []

        for extracted in extracted_controls:
            # Try to find matches based on:
            # 1. Control ID (exact match)
            # 2. Control name (fuzzy match)
            # 3. Description (fuzzy match)
            # 4. Control family (exact match)

            best_match = None
            best_score = 0.0

            extracted_id = extracted.get('control_id', '').upper()
            extracted_name = extracted.get('control_name', '').lower()
            extracted_desc = extracted.get('description', '').lower()
            extracted_family = extracted.get('family', '')

            # Method 1: Try exact ID match first
            if extracted_id in self.controls:
                best_match = self.controls[extracted_id]
                best_score = 1.0

            # Method 2: Fuzzy matching on name and description
            if best_score < threshold:
                for control_id, control_data in self.controls.items():
                    # Calculate similarity scores
                    # Try both 'name' and 'control_name' for compatibility
                    control_name = control_data.get('name') or control_data.get('control_name', '')
                    name_similarity = self._similarity(
                        extracted_name,
                        control_name.lower()
                    )
                    desc_similarity = self._similarity(
                        extracted_desc,
                        control_data.get('description', '').lower()
                    )

                    # Weighted average (name is more important)
                    combined_score = (name_similarity * 0.7) + (desc_similarity * 0.3)

                    # Bonus if family matches
                    if extracted_family == control_data.get('family', ''):
                        combined_score += 0.1

                    if combined_score > best_score:
                        best_score = combined_score
                        best_match = control_data

            # Add matched control if above threshold
            if best_match and best_score >= threshold:
                matched_control = {
                    'extracted': extracted,
                    'matched': best_match,
                    'match_score': round(best_score, 2),
                    'match_method': 'exact_id' if best_score == 1.0 else 'fuzzy_match'
                }
                matched_controls.append(matched_control)
            else:
                # No match found - keep as unmatched
                matched_control = {
                    'extracted': extracted,
                    'matched': None,
                    'match_score': 0.0,
                    'match_method': 'no_match'
                }
                matched_controls.append(matched_control)

        print(f"🔍 Matched {sum(1 for m in matched_controls if m['matched'])} / {len(extracted_controls)} controls")

        return matched_controls

    def search_controls(
        self,
        query: str,
        search_fields: List[str] = None
    ) -> List[Dict]:
        """
        Search controls by keyword

        Args:
            query: Search query
            search_fields: Fields to search in (default: all)

        Returns:
            List of matching controls
        """
        if search_fields is None:
            search_fields = ['control_id', 'control_name', 'description', 'family']

        query_lower = query.lower()
        results = []

        for control_id, control_data in self.controls.items():
            # Check if query matches any search field
            for field in search_fields:
                field_value = str(control_data.get(field, '')).lower()
                if query_lower in field_value:
                    # Calculate relevance score
                    relevance = self._similarity(query_lower, field_value)
                    results.append({
                        'control': control_data,
                        'relevance': round(relevance, 2),
                        'matched_field': field
                    })
                    break

        # Sort by relevance
        results.sort(key=lambda x: x['relevance'], reverse=True)

        print(f"🔍 Found {len(results)} controls matching '{query}'")

        return results

    def get_families(self) -> List[str]:
        """
        Get list of all control families

        Returns:
            List of family names
        """
        return list(self.families.keys())

    def get_control(self, control_id: str) -> Optional[Dict]:
        """
        Get control by ID

        Args:
            control_id: Control ID

        Returns:
            Control data or None if not found
        """
        return self.controls.get(control_id.upper())

    def get_controls_by_family(self, family: str) -> List[Dict]:
        """
        Get all controls in a family

        Args:
            family: Control family name

        Returns:
            List of controls in family
        """
        if family not in self.families:
            return []

        control_ids = self.families[family]
        return [self.controls[cid] for cid in control_ids]

    def get_control_count(self) -> Dict[str, int]:
        """
        Get count of controls by framework

        Returns:
            Dictionary with framework counts
        """
        counts = {
            'total': len(self.controls),
            'rwanda_ncsa': 0,
            'nist': 0,
            'families': len(self.families)
        }

        for control_data in self.controls.values():
            framework = control_data.get('framework', '')
            if framework == 'Rwanda-NCSA':
                counts['rwanda_ncsa'] += 1
            elif 'NIST' in framework or framework == 'NIST SP 800-53':
                counts['nist'] += 1

        return counts

    def _similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two strings

        Args:
            text1: First string
            text2: Second string

        Returns:
            Similarity score (0.0-1.0)
        """
        if not text1 or not text2:
            return 0.0

        return SequenceMatcher(None, text1, text2).ratio()

    def validate_control(self, control_id: str) -> bool:
        """
        Check if a control ID exists in the taxonomy

        Args:
            control_id: Control ID to validate

        Returns:
            True if control exists, False otherwise
        """
        return control_id.upper() in self.controls

    def get_control_requirements(self, control_id: str) -> List[str]:
        """
        Get requirements for a specific control

        Args:
            control_id: Control ID

        Returns:
            List of requirements
        """
        control = self.get_control(control_id)
        if control:
            return control.get('requirements', [])
        return []

    def get_control_indicators(self, control_id: str) -> List[str]:
        """
        Get log indicators for a specific control

        Args:
            control_id: Control ID

        Returns:
            List of log indicators
        """
        control = self.get_control(control_id)
        if control:
            return control.get('log_indicators', [])
        return []
