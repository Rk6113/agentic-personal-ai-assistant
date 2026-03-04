use super::types::{RiskLevel, ToolRequest};

/// V1 policy: allow Low and Medium risk only. High / Critical are blocked.
pub fn evaluate(request: &ToolRequest) -> PolicyDecision {
    match request.risk_level {
        RiskLevel::Low | RiskLevel::Medium => PolicyDecision::Allow,
        RiskLevel::High | RiskLevel::Critical => PolicyDecision::Deny {
            reason: format!(
                "v1 policy blocks {:?}-risk tool '{}'",
                request.risk_level, request.tool_name
            ),
        },
    }
}

#[derive(Debug, Clone)]
pub enum PolicyDecision {
    Allow,
    Deny { reason: String },
}
