/// Placeholder scheduler for triggering the morning brief.
///
/// In v1 this will be driven externally (cron / CLI).
/// The struct exists so later versions can add in-process scheduling.
pub struct Scheduler {
    pub enabled: bool,
}

impl Scheduler {
    pub fn new() -> Self {
        Self { enabled: false }
    }

    /// Placeholder: would trigger the morning brief pipeline.
    pub fn trigger_morning_brief(&self) {
        if self.enabled {
            println!("[scheduler] morning brief triggered (stub)");
        } else {
            println!("[scheduler] scheduler disabled — use CLI or cron instead");
        }
    }
}

impl Default for Scheduler {
    fn default() -> Self {
        Self::new()
    }
}
