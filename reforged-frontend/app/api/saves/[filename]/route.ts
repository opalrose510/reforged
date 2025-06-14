import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

interface Situation {
  id: string;
  name: string;
  nextSituations: string[];
}

interface GraphNode {
  id: string;
  label?: string;
  edges?: Array<{ target: string }>;
}

interface ValidatedGraph {
  nodes: Array<{
    id: string;
    label: string;
  }>;
  edges: Array<{
    source: string;
    target: string;
  }>;
}

interface WorldContext {
  districts: Array<{
    id: string;
    factions: string[];
  }>;
  factions: Array<{
    name: string;
    relationships?: Record<string, string>;
  }>;
  npcs: Array<{
    id: string;
    name: string;
  }>;
}

export async function GET(
  request: Request,
  { params }: { params: { filename: string } }
) {
  try {
    const filename = params.filename;
    const savesDir = path.join(process.cwd(), '..', 'saves');
    
    // Resolve the full path and ensure it's within the saves directory
    const requestedPath = path.join(savesDir, filename);
    const normalizedPath = path.normalize(requestedPath);
    
    // Check if the resolved path is within the saves directory
    if (!normalizedPath.startsWith(savesDir)) {
      console.error('Attempted directory traversal:', normalizedPath);
      return NextResponse.json({ error: 'Invalid file path' }, { status: 403 });
    }

    if (!fs.existsSync(normalizedPath)) {
      console.error('File not found:', normalizedPath);
      return NextResponse.json({ error: 'File not found' }, { status: 404 });
    }

    const fileContent = fs.readFileSync(normalizedPath, 'utf-8');
    const data = JSON.parse(fileContent);

    // Extract situations from the data
    let situations: Situation[] = [];
    
    if (data.situations) {
      situations = data.situations;
    } else if (data.nodes && data.edges) {
      // For validated graph files
      const validatedGraph = data as ValidatedGraph;
      situations = validatedGraph.nodes.map(node => ({
        id: node.id,
        name: node.label,
        nextSituations: validatedGraph.edges
          .filter(edge => edge.source === node.id)
          .map(edge => edge.target)
      }));
    } else if (data.nodes) {
      // For other graph files
      situations = data.nodes.map((node: GraphNode) => ({
        id: node.id,
        name: node.label || node.id,
        nextSituations: node.edges?.map(edge => edge.target) || []
      }));
    } else if (data.world_context) {
      // For final export files
      const worldContext = data.world_context as WorldContext;
      
      // Create situations from districts
      const districtSituations = worldContext.districts.map(district => ({
        id: district.id,
        name: district.id,
        nextSituations: district.factions
      }));

      // Create situations from factions
      const factionSituations = worldContext.factions.map(faction => ({
        id: faction.name,
        name: faction.name,
        nextSituations: faction.relationships ? Object.keys(faction.relationships) : []
      }));

      // Create situations from NPCs
      const npcSituations = worldContext.npcs.map(npc => ({
        id: npc.id,
        name: npc.name,
        nextSituations: [] // NPCs don't have explicit next situations
      }));

      situations = [...districtSituations, ...factionSituations, ...npcSituations];
    }

    return NextResponse.json(situations);
  } catch (error) {
    console.error('Error reading file:', error);
    return NextResponse.json({ error: 'Failed to read file' }, { status: 500 });
  }
} 