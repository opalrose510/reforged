'use client';

import { useEffect, useState } from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Choice, Situation, Arc } from '@/baml_client/types';
import {Edge, Node, ReactFlow}  from '@xyflow/react';
import '@xyflow/react/dist/style.css';
interface GraphData {
  nodes: Node[];
  edges: Edge[];
}

interface SaveFolder {
  name: string;
  path: string;
}

interface SaveFile {
  name: string;
  path: string;
}

export default function GraphPage() {
  const [saveFolders, setSaveFolders] = useState<SaveFolder[]>([]);
  const [saveFiles, setSaveFiles] = useState<SaveFile[]>([]);
  const [selectedFolder, setSelectedFolder] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<string>('');
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] });

  useEffect(() => {
    // Fetch available save folders
    fetch('/api/saves')
      .then(res => res.json())
      .then(data => {
        setSaveFolders(data);
        // Auto-select the latest folder (assuming folders are sorted by timestamp)
        if (data.length > 0) {
          const latestFolder = data[data.length - 1];
          setSelectedFolder(latestFolder.path);
        }
      })
      .catch(err => console.error('Error fetching save folders:', err));
  }, []);

  useEffect(() => {
    if (!selectedFolder) {
      setSaveFiles([]);
      setSelectedFile('');
      return;
    }

    // Fetch files within the selected folder
    fetch(`/api/saves?folder=${encodeURIComponent(selectedFolder)}`)
      .then(res => res.json())
      .then(data => {
        setSaveFiles(data);
        // Auto-select the file with the highest step number
        if (data.length > 0) {
          setSelectedFile(data[data.length - 1].path);
        } else {
          setSelectedFile('');
        }
      })
      .catch(err => console.error('Error fetching save files:', err));
  }, [selectedFolder]);

  useEffect(() => {
    if (!selectedFile) {
      console.log('No file selected, returning early');
      return;
    }

    console.log('Fetching data for file:', selectedFile);

    // Fetch the selected save file data
    fetch(`/api/saves/${encodeURIComponent(selectedFile)}`)
      .then(res => {
        console.log('Response status:', res.status);
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then((data) => {
        console.log('Successfully fetched data:', data);
        processDataIntoGraph(data);
      })
      .catch(err => {
        console.error('Error fetching save file data:', err);
      });
  }, [selectedFile]);

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const processDataIntoGraph = (data: any) => {
    const arcSituationsFlattened = data.arcs.map((arc: Arc) => Object.values(arc.situations)).flat() as Situation[];
    const nodes: GraphData['nodes'] = [];
    const edges: GraphData['edges'] = [];
    // console.log(arcSituationsFlattened);
    Object.values(arcSituationsFlattened).forEach((situation: Situation, index: number) => {
      if(!nodes.find((n) => n.id === situation.id)) {
        console.log(`Adding situation ${situation.id}`);
        nodes.push({ id: situation.id, position: { x: index * 100, y: 0 }, data: { label: situation.id } });
      }
      console.log(situation);
      situation.choices.forEach((choice: Choice, choiceIndex: number) => {
        if(!arcSituationsFlattened.find((s) => s.id === choice.next_situation_id)) {
          console.log(`Choice ${choice.id} has a next_situation_id that doesn't exist: ${choice.next_situation_id}`);
          nodes.push({ id: choice.next_situation_id, position: { x: index * 100, y: choiceIndex * 100 }, data: { label: "MISSING: " + choice.next_situation_id } });
          edges.push({ id: choice.id, source: choice.next_situation_id, target: situation.id, label: choice.text });
        }

      });
    });
    console.log(nodes);
    console.log(edges);
    setGraphData({ nodes, edges });
  };

  return (
    <div className="container mx-auto p-4">
      <Card className="mb-4">
        <CardHeader>
          <CardTitle>Situation Graph Visualizer</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Select Save Folder</label>
            <Select value={selectedFolder} onValueChange={setSelectedFolder}>
              <SelectTrigger className="w-[300px]">
                <SelectValue placeholder="Select a save folder" />
              </SelectTrigger>
              <SelectContent>
                {saveFolders.map((folder) => (
                  <SelectItem key={folder.path} value={folder.path}>
                    {folder.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">Select Save File</label>
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
          </div>
        </CardContent>
      </Card>
      <Card>
        {graphData.nodes.length > 0 ? (
          <CardContent className="h-[2000px] w-[2000px]">
            <ReactFlow defaultNodes={graphData.nodes} defaultEdges={graphData.edges} />
          </CardContent>
        ) : (
          <CardContent>
            <p>No graph data available</p>
          </CardContent>
        )}
      </Card>
    </div>
  );
} 