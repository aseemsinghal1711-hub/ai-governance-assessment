"""
Full Assessment Orchestrator - runs the complete multi-agent pipeline.

Takes a completed AISystemProfile (from intake) and produces a bundled
result containing the assessment report and remediation plan.

Usage:
    from full_assessment import run_full_pipeline
    result = run_full_pipeline(profile)
    print(result.report.eu_ai_act_risk_tier)
    print(result.plan.executive_summary)
"""
import json
from datetime import datetime
from pydantic import BaseModel, Field

from models import (
    AISystemProfile,
    AssessmentReport,
    RemediationPlan,
)
from assessment_agent import run_assessment
from recommendation_agent import generate_recommendations


# =============================================================================
# Combined output model - the full deliverable
# =============================================================================
class FullAssessmentResult(BaseModel):
    """The complete output of the multi-agent pipeline."""
    
    profile: AISystemProfile = Field(
        description="The AI system profile that was assessed"
    )
    report: AssessmentReport = Field(
        description="Gap assessment across all three frameworks"
    )
    plan: RemediationPlan = Field(
        description="Phased remediation roadmap"
    )
    generated_at: str = Field(
        description="ISO timestamp when this assessment was generated"
    )


# =============================================================================
# The orchestrator
# =============================================================================
def run_full_pipeline(profile: AISystemProfile) -> FullAssessmentResult:
    """
    Run the complete assessment pipeline on a profile.
    
    This is the main entry point post-intake. It runs:
      1. Assessment (5-phase analysis against frameworks)
      2. Recommendations (phased remediation plan)
      3. Bundles everything with a timestamp
    
    Total runtime: ~2-3 minutes (paid Gemini tier).
    """
    print("\n" + "🚀 " * 20)
    print("FULL ASSESSMENT PIPELINE")
    print(f"System: {profile.system_name}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🚀 " * 20)
    
    # Stage 1: Run the 5-phase assessment
    report = run_assessment(profile)
    
    # Stage 2: Generate the remediation plan from the assessment
    plan = generate_recommendations(profile, report)
    
    # Stage 3: Bundle everything
    result = FullAssessmentResult(
        profile=profile,
        report=report,
        plan=plan,
        generated_at=datetime.now().isoformat(),
    )
    
    print("\n" + "✅ " * 20)
    print("PIPELINE COMPLETE")
    print(f"Findings: {len(report.findings)}")
    print(f"Cross-framework themes: {len(report.cross_framework_themes)}")
    total_actions = (
        len(plan.quick_wins) + len(plan.foundation_phase) +
        len(plan.maturity_phase) + len(plan.optimization_phase)
    )
    print(f"Remediation actions: {total_actions} across 4 phases")
    print("✅ " * 20)
    
    return result


# =============================================================================
# Optional: save and load results
# =============================================================================
def save_result(result: FullAssessmentResult, path: str) -> None:
    """Save a complete result as JSON for later viewing or analysis."""
    with open(path, "w") as f:
        json.dump(result.model_dump(), f, indent=2)
    print(f"💾 Saved to {path}")


def load_result(path: str) -> FullAssessmentResult:
    """Load a previously saved result."""
    with open(path, "r") as f:
        data = json.load(f)
    return FullAssessmentResult(**data)