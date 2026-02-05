#!/usr/bin/env python3
"""
Tests for MCP Compliance Analyzer.

Tests both rule-based fallback and LLM analysis (when API key available).
"""

import os
import sys
import asyncio
import pytest

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.ncsa_controls import (
    get_control, get_all_controls, find_relevant_controls,
    get_control_families, NCSA_CONTROLS
)
from app.models.schemas import LogEntry, AnalysisRequest


# =============================================================================
# NCSA Controls Tests
# =============================================================================

class TestNCSAControls:
    """Test NCSA controls database."""

    def test_controls_loaded(self):
        """Verify controls are loaded."""
        controls = get_all_controls()
        assert len(controls) > 0
        print(f"Loaded {len(controls)} NCSA controls")

    def test_get_specific_control(self):
        """Test retrieving a specific control."""
        ctrl = get_control("RWNCSA-AC-37")
        assert ctrl is not None
        assert ctrl["control_id"] == "RWNCSA-AC-37"
        assert ctrl["control_family"] == "Access Control"
        assert "Failed password" in ctrl["evidence_patterns"]

    def test_control_families(self):
        """Test control families."""
        families = get_control_families()
        assert "AC" in families
        assert families["AC"] == "Access Control"
        assert "IA" in families

    def test_find_relevant_controls_failed_password(self):
        """Test finding controls for failed password log."""
        log = "Failed password for invalid user admin from 192.168.1.100"
        controls = find_relevant_controls(log, top_k=3)

        assert len(controls) > 0
        control_ids = [c["control_id"] for c in controls]
        # Should find authentication-related controls
        assert any("IA" in cid or "AC" in cid for cid in control_ids)

    def test_find_relevant_controls_session(self):
        """Test finding controls for session log."""
        log = "session opened for user root by (uid=0)"
        controls = find_relevant_controls(log, top_k=3)

        assert len(controls) > 0
        # Should find audit-related controls
        control_ids = [c["control_id"] for c in controls]
        assert any("AU" in cid for cid in control_ids)

    def test_find_relevant_controls_no_match(self):
        """Test with log that doesn't match any pattern."""
        log = "Random system event with no keywords"
        controls = find_relevant_controls(log, top_k=3)
        # Should return empty list (no matches)
        assert len(controls) == 0


# =============================================================================
# Rule-Based Analysis Tests
# =============================================================================

class TestRuleBasedAnalysis:
    """Test rule-based fallback analysis."""

    def setup_method(self):
        """Import rule-based function."""
        from app.main import rule_based_analysis
        self.analyze = rule_based_analysis

    def test_failed_password(self):
        """Test failed password detection."""
        result = self.analyze(
            "Failed password for invalid user admin from 192.168.1.100 port 22 ssh2",
            {}
        )

        assert result is not None
        assert result["prediction"] == "non_compliant"
        assert result["confidence"] >= 0.95
        assert "RWNCSA-IA-98" in result["primary_control"]["control_id"]
        assert result["model_used"] == "rule-based"

    def test_accepted_password(self):
        """Test successful login detection."""
        result = self.analyze(
            "Accepted password for ubuntu from 10.0.0.5 port 22 ssh2",
            {}
        )

        assert result is not None
        assert result["prediction"] == "compliant"
        assert result["confidence"] >= 0.95
        assert "RWNCSA-IA-97" in result["primary_control"]["control_id"]

    def test_session_opened(self):
        """Test session opened detection."""
        result = self.analyze(
            "pam_unix(sshd:session): session opened for user root by (uid=0)",
            {}
        )

        assert result is not None
        assert result["prediction"] == "compliant"
        assert "AU" in result["primary_control"]["control_id"]

    def test_invalid_user(self):
        """Test invalid user detection."""
        result = self.analyze(
            "Invalid user test from 192.168.1.50",
            {}
        )

        assert result is not None
        assert result["prediction"] == "non_compliant"
        assert "AC" in result["primary_control"]["control_id"]

    def test_cron_job(self):
        """Test cron job detection."""
        result = self.analyze(
            "CRON[12345]: (root) CMD (/usr/bin/backup.sh)",
            {}
        )

        assert result is not None
        assert result["prediction"] == "compliant"
        assert "CM" in result["primary_control"]["control_id"]

    def test_no_match(self):
        """Test log with no matching pattern."""
        result = self.analyze(
            "Some random log message without known patterns",
            {}
        )

        assert result is None  # Should return None for LLM fallback


# =============================================================================
# API Schema Tests
# =============================================================================

class TestSchemas:
    """Test Pydantic schemas."""

    def test_log_entry_schema(self):
        """Test LogEntry schema."""
        entry = LogEntry(
            log_message="Failed password for user admin",
            port=22,
            status_code=401
        )

        assert entry.log_message == "Failed password for user admin"
        assert entry.port == 22
        assert entry.status_code == 401

    def test_analysis_request_schema(self):
        """Test AnalysisRequest schema."""
        request = AnalysisRequest(
            log_message="Test log message",
            status_code=200,
            port=443
        )

        assert request.log_message == "Test log message"
        assert request.include_reasoning == True  # Default


# =============================================================================
# Integration Tests (require API key)
# =============================================================================

@pytest.mark.skipif(
    not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"),
    reason="No API key available"
)
class TestLLMIntegration:
    """Integration tests with actual LLM API."""

    @pytest.fixture
    def llm_client(self):
        """Create LLM client."""
        from app.services.llm_client import ComplianceLLMClient

        provider = "anthropic" if os.getenv("ANTHROPIC_API_KEY") else "openai"
        return ComplianceLLMClient(provider=provider, enable_cache=True)

    @pytest.mark.asyncio
    async def test_llm_analyze_failed_password(self, llm_client):
        """Test LLM analysis of failed password."""
        result = await llm_client.analyze_log(
            log_message="Failed password for invalid user admin from 192.168.1.100 port 22 ssh2",
            context={"port": 22, "hour_of_day": 14}
        )

        assert result is not None
        assert "prediction" in result
        assert result["prediction"] in ["compliant", "non_compliant", "partial"]
        assert "confidence" in result
        assert "primary_control" in result
        assert "reasoning" in result

        print(f"\nLLM Result:")
        print(f"  Prediction: {result['prediction']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Control: {result['primary_control']['control_id']}")
        print(f"  Reasoning: {result['reasoning'][:100]}...")

    @pytest.mark.asyncio
    async def test_llm_caching(self, llm_client):
        """Test response caching."""
        log = "Accepted publickey for deploy from 10.0.0.10 port 22 ssh2"

        # First call - not cached
        result1 = await llm_client.analyze_log(log_message=log)
        assert result1["cached"] == False

        # Second call - should be cached
        result2 = await llm_client.analyze_log(log_message=log)
        assert result2["cached"] == True
        assert result2["latency_ms"] < result1["latency_ms"]


# =============================================================================
# Run Tests
# =============================================================================

def run_tests():
    """Run all tests."""
    print("=" * 70)
    print("MCP COMPLIANCE ANALYZER - TEST SUITE")
    print("=" * 70)

    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])


if __name__ == "__main__":
    run_tests()
