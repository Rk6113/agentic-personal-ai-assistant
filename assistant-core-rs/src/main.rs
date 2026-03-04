use assistant_core::tool_registry;

fn main() {
    let args: Vec<String> = std::env::args().collect();

    match args.get(1).map(|s| s.as_str()) {
        Some("--health") => {
            println!("ok");
        }
        Some("--list-tools") => {
            let registry = tool_registry::default_registry();
            for tool in registry.list_tools() {
                println!("  {} — {}", tool.name, tool.description);
            }
        }
        Some("--brief") => {
            println!("[morning-brief] pipeline not yet implemented");
            let scheduler = assistant_core::Scheduler::new();
            scheduler.trigger_morning_brief();
        }
        _ => {
            eprintln!("Usage: assistant-core <--health | --list-tools | --brief>");
            std::process::exit(1);
        }
    }
}
