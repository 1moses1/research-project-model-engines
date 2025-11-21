#!/usr/bin/env python3
"""
RAG Engine - Retrieval Augmented Generation
Uses Rwanda NCSA standards as knowledge base for context-aware compliance decisions
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
import logging

# For embeddings and similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NCSAKnowledgeBase:
    """RAG system with Rwanda NCSA minimum cybersecurity standards"""

    def __init__(self, ncsa_data_dir: str = "data/rwanda_ncsa"):
        self.ncsa_dir = Path(ncsa_data_dir)
        self.knowledge_base = {}
        self.vectorizer = None
        self.document_vectors = None
        self.document_metadata = []

        # Load and index knowledge base
        self._load_knowledge_base()
        self._build_vector_index()

    def _load_knowledge_base(self):
        """Load NCSA standards and security frameworks"""
        logger.info("Loading NCSA knowledge base...")

        # Load NCSA documents
        if self.ncsa_dir.exists():
            for file_path in self.ncsa_dir.glob("*.txt"):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        doc_id = file_path.stem
                        self.knowledge_base[doc_id] = {
                            'content': content,
                            'source': 'NCSA',
                            'type': 'standard',
                            'file': str(file_path)
                        }
                except Exception as e:
                    logger.warning(f"Could not load {file_path}: {e}")

        # Load NIST control mappings
        self._load_nist_controls()

        # Load MITRE ATT&CK mappings if available
        self._load_mitre_attack()

        logger.info(f"Loaded {len(self.knowledge_base)} documents into knowledge base")

    def _load_nist_controls(self):
        """Load NIST SP 800-53 control definitions"""
        nist_controls = {
            'AC-3': {
                'name': 'Access Enforcement',
                'content': 'The information system enforces approved authorizations for logical access to information and system resources in accordance with applicable access control policies.',
                'family': 'Access Control',
                'source': 'NIST-800-53'
            },
            'SI-4': {
                'name': 'System Monitoring',
                'content': 'The organization monitors the information system to detect attacks and indicators of potential attacks, unauthorized local, network, and remote connections, and unauthorized use of the system.',
                'family': 'System and Information Integrity',
                'source': 'NIST-800-53'
            },
            'AU-6': {
                'name': 'Audit Review, Analysis, and Reporting',
                'content': 'The organization reviews and analyzes information system audit records for indications of inappropriate or unusual activity, investigates suspicious activity or suspected violations.',
                'family': 'Audit and Accountability',
                'source': 'NIST-800-53'
            },
            'IA-2': {
                'name': 'Identification and Authentication',
                'content': 'The information system uniquely identifies and authenticates organizational users (or processes acting on behalf of organizational users).',
                'family': 'Identification and Authentication',
                'source': 'NIST-800-53'
            },
            'SC-7': {
                'name': 'Boundary Protection',
                'content': 'The information system monitors and controls communications at the external boundary of the system and at key internal boundaries within the system.',
                'family': 'System and Communications Protection',
                'source': 'NIST-800-53'
            },
            'IR-4': {
                'name': 'Incident Handling',
                'content': 'The organization implements an incident handling capability for security incidents that includes preparation, detection and analysis, containment, eradication, and recovery.',
                'family': 'Incident Response',
                'source': 'NIST-800-53'
            },
            'CM-6': {
                'name': 'Configuration Settings',
                'content': 'The organization establishes and documents configuration settings for information technology products employed within the information system using security configuration checklists.',
                'family': 'Configuration Management',
                'source': 'NIST-800-53'
            },
            'RA-5': {
                'name': 'Vulnerability Scanning',
                'content': 'The organization scans for vulnerabilities in the information system and hosted applications, analyzes vulnerability scan reports and results from security control assessments.',
                'family': 'Risk Assessment',
                'source': 'NIST-800-53'
            }
        }

        for control_id, control_data in nist_controls.items():
            doc_id = f"NIST_{control_id}"
            self.knowledge_base[doc_id] = {
                'content': f"{control_data['name']}: {control_data['content']}",
                'source': control_data['source'],
                'type': 'control',
                'control_id': control_id,
                'family': control_data['family']
            }

    def _load_mitre_attack(self):
        """Load MITRE ATT&CK technique descriptions"""
        mitre_dir = Path("data/security_feeds/mitre_attack")

        if mitre_dir.exists():
            for json_file in mitre_dir.glob("*-techniques.json"):
                try:
                    with open(json_file, 'r') as f:
                        techniques = json.load(f)

                    for technique in techniques[:20]:  # Load top 20
                        doc_id = f"MITRE_{technique['id']}"
                        self.knowledge_base[doc_id] = {
                            'content': f"{technique['name']}: {technique['description']}",
                            'source': 'MITRE-ATT&CK',
                            'type': 'technique',
                            'technique_id': technique['id'],
                            'tactics': technique.get('tactics', [])
                        }

                except Exception as e:
                    logger.warning(f"Could not load MITRE data: {e}")

    def _build_vector_index(self):
        """Build TF-IDF vector index for retrieval"""
        logger.info("Building vector index for RAG retrieval...")

        documents = []
        self.document_metadata = []

        for doc_id, doc_data in self.knowledge_base.items():
            documents.append(doc_data['content'])
            self.document_metadata.append({
                'id': doc_id,
                'source': doc_data.get('source', 'unknown'),
                'type': doc_data.get('type', 'document')
            })

        if not documents:
            logger.warning("No documents to index - using fallback")
            return

        # Create TF-IDF vectors
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )

        self.document_vectors = self.vectorizer.fit_transform(documents)

        logger.info(f"Indexed {len(documents)} documents with {self.document_vectors.shape[1]} features")

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve most relevant documents from knowledge base

        Args:
            query: Input query (log message, alert, etc.)
            top_k: Number of top documents to retrieve

        Returns:
            List of relevant documents with similarity scores
        """
        if self.vectorizer is None or self.document_vectors is None:
            logger.warning("Vector index not built - returning empty")
            return []

        # Vectorize query
        query_vector = self.vectorizer.transform([query])

        # Compute similarity
        similarities = cosine_similarity(query_vector, self.document_vectors)[0]

        # Get top-k
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            doc_id = self.document_metadata[idx]['id']
            doc_data = self.knowledge_base[doc_id]

            results.append({
                'doc_id': doc_id,
                'content': doc_data['content'],
                'source': doc_data.get('source', 'unknown'),
                'type': doc_data.get('type', 'document'),
                'similarity': float(similarities[idx]),
                'metadata': self.document_metadata[idx]
            })

        return results

    def augment_with_context(self, query: str, prediction: Dict) -> Dict:
        """
        Augment model prediction with RAG context

        Args:
            query: Original input
            prediction: Model prediction from XGBoost

        Returns:
            Augmented prediction with NCSA context
        """
        # Retrieve relevant documents
        retrieved_docs = self.retrieve(query, top_k=3)

        # Extract relevant standards
        relevant_standards = []
        relevant_controls = []

        for doc in retrieved_docs:
            if doc['type'] == 'standard':
                relevant_standards.append({
                    'name': doc['doc_id'],
                    'snippet': doc['content'][:200],
                    'relevance': doc['similarity']
                })
            elif doc['type'] == 'control':
                relevant_controls.append({
                    'control_id': doc.get('metadata', {}).get('id', ''),
                    'description': doc['content'][:200],
                    'relevance': doc['similarity']
                })

        # Build augmented response
        augmented = {
            **prediction,
            'rag_context': {
                'relevant_ncsa_standards': relevant_standards,
                'relevant_controls': relevant_controls,
                'retrieved_documents': len(retrieved_docs),
                'max_relevance': max([d['similarity'] for d in retrieved_docs]) if retrieved_docs else 0
            },
            'compliance_reasoning': self._generate_reasoning(prediction, retrieved_docs)
        }

        return augmented

    def _generate_reasoning(self, prediction: Dict, retrieved_docs: List[Dict]) -> str:
        """Generate human-readable compliance reasoning"""
        status = prediction.get('compliance_status', 'unknown')
        confidence = prediction.get('confidence_score', 0)

        reasoning_parts = []

        # Main decision
        reasoning_parts.append(
            f"Classified as {status.upper()} with {confidence:.1%} confidence."
        )

        # Top relevant standard
        if retrieved_docs:
            top_doc = retrieved_docs[0]
            reasoning_parts.append(
                f"Most relevant standard: {top_doc['source']} - {top_doc['doc_id']} "
                f"(relevance: {top_doc['similarity']:.1%})."
            )

        # Control mapping
        if 'control_id' in prediction:
            reasoning_parts.append(
                f"Mapped to NIST control {prediction['control_id']} "
                f"({prediction.get('control_family', 'Unknown Family')})."
            )

        return ' '.join(reasoning_parts)

    def get_compliance_guidance(self, control_id: str) -> Optional[Dict]:
        """Get compliance guidance for specific control"""
        doc_id = f"NIST_{control_id}"

        if doc_id in self.knowledge_base:
            return self.knowledge_base[doc_id]

        return None


class RAGComplianceEngine:
    """
    Complete RAG-based compliance engine
    Combines XGBoost predictions with NCSA knowledge base
    """

    def __init__(self, xgboost_model_path: str = None, ncsa_data_dir: str = "data/rwanda_ncsa"):
        """Initialize RAG engine with model and knowledge base"""
        self.knowledge_base = NCSAKnowledgeBase(ncsa_data_dir)

        # Load XGBoost model if provided
        self.xgboost_model = None
        if xgboost_model_path:
            self._load_xgboost_model(xgboost_model_path)

    def _load_xgboost_model(self, model_path: str):
        """Load trained XGBoost model"""
        try:
            from models.xgboost_classifier import XGBoostClassifier
            self.xgboost_model = XGBoostClassifier()
            self.xgboost_model.load_model(model_path)
            logger.info(f"Loaded XGBoost model from {model_path}")
        except Exception as e:
            logger.warning(f"Could not load XGBoost model: {e}")

    def analyze(self, raw_input: str, use_rag: bool = True) -> Dict:
        """
        Analyze input with RAG-augmented predictions

        Args:
            raw_input: Unstructured security input
            use_rag: Whether to augment with RAG context

        Returns:
            Complete analysis with RAG context
        """
        # Process with NLP engine
        from nlp.unstructured_processor import UnstructuredSecurityProcessor
        processor = UnstructuredSecurityProcessor()
        structured = processor.process(raw_input)

        # Get XGBoost prediction if model available
        if self.xgboost_model:
            import pandas as pd
            df = pd.DataFrame([structured])
            predictions, probabilities = self.xgboost_model.predict(df)

            structured['compliance_status'] = predictions[0]
            structured['confidence_score'] = float(probabilities[0])

        # Augment with RAG context
        if use_rag:
            augmented = self.knowledge_base.augment_with_context(raw_input, structured)
        else:
            augmented = structured

        return augmented

    def batch_analyze(self, inputs: List[str], use_rag: bool = True) -> List[Dict]:
        """Batch analysis with RAG"""
        results = []

        for input_text in inputs:
            result = self.analyze(input_text, use_rag=use_rag)
            results.append(result)

        return results


def main():
    """Test RAG engine"""
    print("\n" + "="*100)
    print("RAG COMPLIANCE ENGINE TEST")
    print("="*100 + "\n")

    # Initialize RAG engine
    rag_engine = RAGComplianceEngine()

    # Test queries
    test_queries = [
        "Unauthorized access denied to database server from IP 192.168.1.100",
        "User successfully authenticated via multi-factor authentication",
        "Vulnerability scan detected critical CVE-2024-1234 on web server",
        "Incident response team contained ransomware attack on file server",
        "System configuration changed without approval - audit log generated"
    ]

    for i, query in enumerate(test_queries, 1):
        print(f"\nQuery {i}: {query[:70]}...")

        # Retrieve relevant documents
        results = rag_engine.knowledge_base.retrieve(query, top_k=3)

        print(f"  Top relevant documents:")
        for j, doc in enumerate(results, 1):
            print(f"    {j}. {doc['source']} - {doc['doc_id']} (similarity: {doc['similarity']:.2%})")
            print(f"       {doc['content'][:100]}...")

    print("\n" + "="*100)


if __name__ == '__main__':
    main()
