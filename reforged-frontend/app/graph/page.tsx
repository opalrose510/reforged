'use client';

import { useEffect, useState } from 'react';
import { GraphCanvas } from 'reagraph';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface SaveFile {
  name: string;
  path: string;
}

interface Choice {
  id: string;
  text: string;
  next_situation_id: string;
}

interface Situation {
  id: string;
  title: string;
  choices: Choice[];
}

interface GraphData {
  nodes: Array<{
    id: string;
    label: string;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
  }>;
}

export default function GraphPage() {
  const [saveFiles, setSaveFiles] = useState<SaveFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<string>('');
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] });

  useEffect(() => {
    // Fetch available save files
    fetch('/api/saves')
      .then(res => res.json())
      .then(data => {
        // Remove the 'saves/' prefix from paths
        const files = data.map((file: SaveFile) => ({
          ...file,
          path: file.path.replace(/^saves\//, '')
        }));
        setSaveFiles(files);
      })
      .catch(err => console.error('Error fetching save files:', err));
  }, []);

  useEffect(() => {
    if (!selectedFile) return;

    // Fetch the selected save file data
    fetch(`/api/saves/${encodeURIComponent(selectedFile)}`)
      .then(res => res.json())
      .then((data) => {
        const nodes: GraphData['nodes'] = [];
        const edges: GraphData['edges'] = [];

        // Handle the raw JSON data structure
        if (data && typeof data === 'object') {
          // Create nodes from situations
          Object.entries(data).forEach(([id, situation]) => {
            if (
              situation && 
              typeof situation === 'object' && 
              'title' in situation && 
              typeof situation.title === 'string'
            ) {
              nodes.push({
                id,
                label: situation.title.split('.')[0] // Use first sentence as label
              });

              // Create edges from choices
              if (
                'choices' in situation && 
                Array.isArray(situation.choices)
              ) {
                situation.choices.forEach((choice: unknown) => {
                  if (
                    choice && 
                    typeof choice === 'object' && 
                    'next_situation_id' in choice && 
                    typeof choice.next_situation_id === 'string'
                  ) {
                    edges.push({
                      id: `${id}-${choice.next_situation_id}`,
                      source: id,
                      target: choice.next_situation_id
                    });
                  }
                });
              }
            }
          });
        }

        setGraphData({ nodes, edges });
      })
      .catch(err => console.error('Error fetching save file data:', err));
  }, [selectedFile]);

  return (
    <div className="container mx-auto p-4">
      <Card className="mb-4">
        <CardHeader>
          <CardTitle>Situation Graph Visualizer</CardTitle>
        </CardHeader>
        <CardContent>
          <Select value={selectedFile} onValueChange={setSelectedFile}>
            <SelectTrigger className="w-[300px]">
              <SelectValue placeholder="Select a save file" />
            </SelectTrigger>
            <SelectContent>
              {saveFiles.map((file) => (
                <SelectItem key={file.path} value={file.path}>
                  {file.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="h-[600px] p-0">
          {graphData.nodes.length > 0 ? (
            <GraphCanvas
              nodes={graphData.nodes}
              edges={graphData.edges}
              layoutType="forceDirected2d"
              labelType="all"
              theme={{
                node: {
                  fill: "#2563eb",
                  activeFill: "#1d4ed8",
                  opacity: 1,
                  selectedOpacity: 1,
                  inactiveOpacity: 0.2,
                  label: {
                    color: "#ffffff",
                    activeColor: "#ffffff",
                    stroke: "#000000"
                  }
                },
                edge: {
                  fill: "#94a3b8",
                  activeFill: "#64748b",
                  opacity: 1,
                  selectedOpacity: 1,
                  inactiveOpacity: 0.2,
                  label: {
                    color: "#64748b",
                    activeColor: "#475569"
                  }
                },
                ring: {
                  fill: "#2563eb",
                  activeFill: "#1d4ed8"
                },
                arrow: {
                  fill: "#94a3b8",
                  activeFill: "#64748b"
                },
                lasso: {
                  border: "#2563eb",
                  background: "rgba(37, 99, 235, 0.1)"
                }
              }}
            />
          ) : (
            <div className="flex h-full items-center justify-center text-gray-500">
              Select a save file to view the situation graph
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 