# Converts a json input into a MermaidJS graph file.
import json
import re
from typing import Dict, Any, List, Set


def sanitize_node_id(text: str) -> str:
    """Sanitize text to be used as a Mermaid node ID."""
    # Remove all special characters except alphanumeric and spaces
    sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # Replace spaces with underscores
    sanitized = re.sub(r'\s+', '_', sanitized.strip())
    # Ensure it starts with a letter (Mermaid requirement)
    if sanitized and not sanitized[0].isalpha():
        sanitized = 'node_' + sanitized
    # If empty after sanitization, use a default
    if not sanitized:
        sanitized = 'node'
    return sanitized.lower()
def sanitize_text(text: str) -> str:
    """Sanitize text to be used as a Mermaid node text."""
    # Replace double quotes with single quotes
    text = text.replace('"', "'")
    return text

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to fit in Mermaid nodes."""
    # Replace double quotes with single quotes
    text = text.replace('"', "'")
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def generate_mermaid_graph(final_export: Dict[str, Any]) -> str:
    """
    Generate a MermaidJS flowchart from final export data.
    
    Args:
        final_export: Dictionary containing the final export data with arcs
        
    Returns:
        String containing the MermaidJS flowchart definition
    """
    print(f"Debug: final_export keys: {list(final_export.keys())}")
    
    if not final_export or "arcs" not in final_export:
        print(f"Debug: No arcs found in final_export")
        return "flowchart TD\n    A[No arcs found]"
    
    arcs = final_export["arcs"]
    print(f"Debug: Found {len(arcs)} arcs")
    
    if not arcs:
        return "flowchart TD\n    A[No arcs found]"
    
    # Extract all situations from all arcs
    all_situations = {}
    for arc in arcs:
        if isinstance(arc, dict) and "situations" in arc:
            arc_situations = arc["situations"]
            if isinstance(arc_situations, dict):
                all_situations.update(arc_situations)
    
    print(f"Debug: Found {len(all_situations)} situations across all arcs")
    
    if not all_situations:
        return "flowchart TD\n    A[No situations found]"
    
    # Track nodes and edges
    nodes = []
    edges = []
    node_ids = set()
    
    # First pass: create all situation nodes
    for situation_id, situation_data in all_situations.items():
        if not isinstance(situation_data, dict):
            continue
            
        # Create situation node
        situation_title = sanitize_text(situation_id + "\n\n" + situation_data.get("description", "Missing description"))
        sanitized_id = sanitize_node_id(situation_id)
        truncated_title = situation_title
        
        # Ensure unique node ID
        base_id = sanitized_id
        counter = 1
        while sanitized_id in node_ids:
            sanitized_id = f"{base_id}_{counter}"
            counter += 1
        node_ids.add(sanitized_id)
        
        # Add situation node (rectangular shape for situations)
        nodes.append(f'    {sanitized_id}[\'{truncated_title}\']')
    
    # Second pass: create all edges
    for situation_id, situation_data in all_situations.items():
        if not isinstance(situation_data, dict):
            continue
            
        # Get the sanitized ID for this situation
        sanitized_id = sanitize_node_id(situation_id)
        base_id = sanitized_id
        counter = 1
        while sanitized_id not in node_ids:
            sanitized_id = f"{base_id}_{counter}"
            counter += 1
        
        # Process choices
        choices = situation_data.get("choices", [])
        for choice in choices:
            if not isinstance(choice, dict):
                continue
                
            choice_text = sanitize_text(choice.get("id", "") + "\n\n" + choice.get("text", ""))
            next_situation_id = choice.get("next_situation_id")
            
            if next_situation_id and next_situation_id in all_situations:
                # Get the sanitized ID for the next situation
                next_sanitized_id = sanitize_node_id(next_situation_id)
                base_next_id = next_sanitized_id
                counter = 1
                while next_sanitized_id not in node_ids:
                    next_sanitized_id = f"{base_next_id}_{counter}"
                    counter += 1
                
                # Add edge with choice as label
                edges.append(f'    {sanitized_id} -->|{choice_text}| {next_sanitized_id}')
    
    # Build the Mermaid flowchart
    mermaid_lines = ["flowchart TD"]
    mermaid_lines.extend(nodes)
    mermaid_lines.extend(edges)
    
    return "\n".join(mermaid_lines)


def export_save_to_mermaid(save_path: str, output_path: str = None) -> str:
    """
    Export a save's final export to MermaidJS format.
    
    Args:
        save_path: Path to the save directory
        output_path: Optional path to save the Mermaid file
        
    Returns:
        String containing the MermaidJS graph definition
    """
    import os
    
    # Find the final export file
    final_export_files = []
    for file in os.listdir(save_path):
        if file.startswith("step_") and file.endswith("_final_export.json"):
            final_export_files.append(file)
    
    if not final_export_files:
        # If no final export found, find the latest file by creation time
        all_files = []
        for file in os.listdir(save_path):
            if file.endswith(".json"):
                file_path = os.path.join(save_path, file)
                ctime = os.path.getctime(file_path)
                all_files.append((file, ctime))
        
        if not all_files:
            raise FileNotFoundError(f"No JSON files found in {save_path}")
        
        # Sort by creation time (newest first) and take the latest
        all_files.sort(key=lambda x: x[1], reverse=True)
        latest_file = all_files[0][0]
        print(f"No final export found, using latest file: {latest_file}")
        final_export_file = os.path.join(save_path, latest_file)
    else:
        # Use the latest final export file
        final_export_files.sort()
        final_export_file = os.path.join(save_path, final_export_files[-1])
    
    # Load the final export data
    with open(final_export_file, 'r', encoding='utf-8') as f:
        final_export = json.load(f)
    
    # Generate the Mermaid graph
    mermaid_content = generate_mermaid_graph(final_export)
    
    # Save to file if output path provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(mermaid_content)
    
    return mermaid_content


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python mermaid_export.py <save_path> [output_path]")
        sys.exit(1)
    
    save_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        mermaid_content = export_save_to_mermaid(save_path, output_path)
        print("Mermaid graph generated successfully!")
        if not output_path:
            print("\nGraph content:")
            print(mermaid_content)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
