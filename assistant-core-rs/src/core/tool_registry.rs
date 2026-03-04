use std::collections::HashMap;

use super::types::{RiskLevel, ToolRequest, ToolResponse};

#[derive(Debug, Clone)]
pub struct ToolSpec {
    pub name: String,
    pub description: String,
    pub risk_level: RiskLevel,
}

pub struct ToolRegistry {
    tools: HashMap<String, ToolSpec>,
}

impl ToolRegistry {
    pub fn new() -> Self {
        Self {
            tools: HashMap::new(),
        }
    }

    pub fn register(&mut self, spec: ToolSpec) {
        self.tools.insert(spec.name.clone(), spec);
    }

    pub fn list_tools(&self) -> Vec<&ToolSpec> {
        let mut specs: Vec<&ToolSpec> = self.tools.values().collect();
        specs.sort_by_key(|s| &s.name);
        specs
    }

    pub fn get(&self, name: &str) -> Option<&ToolSpec> {
        self.tools.get(name)
    }

    /// Placeholder: execute a tool request. Real connectors will be wired in later.
    pub fn execute(&self, req: &ToolRequest) -> ToolResponse {
        match self.tools.get(&req.tool_name) {
            Some(_spec) => ToolResponse {
                tool_name: req.tool_name.clone(),
                success: true,
                data: serde_json::json!({ "stub": true, "message": "tool executed (stub)" }),
                error: None,
            },
            None => ToolResponse {
                tool_name: req.tool_name.clone(),
                success: false,
                data: serde_json::Value::Null,
                error: Some(format!("tool '{}' not found in registry", req.tool_name)),
            },
        }
    }
}

impl Default for ToolRegistry {
    fn default() -> Self {
        Self::new()
    }
}

/// Build the default v1 registry with placeholder tools.
pub fn default_registry() -> ToolRegistry {
    let mut reg = ToolRegistry::new();

    reg.register(ToolSpec {
        name: "email_event_reader".into(),
        description: "Read-only Gmail access to extract calendar events and deadlines".into(),
        risk_level: RiskLevel::Low,
    });

    reg.register(ToolSpec {
        name: "weather_lookup".into(),
        description: "Fetch current weather and forecast from OpenWeatherMap".into(),
        risk_level: RiskLevel::Low,
    });

    reg.register(ToolSpec {
        name: "memory_store".into(),
        description: "Persist and retrieve user preferences and facts in Postgres".into(),
        risk_level: RiskLevel::Medium,
    });

    reg
}
