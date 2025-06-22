import { NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';


export async function GET(
  request: Request,
  { params }: { params: { filename: string } }
) {
  try {
    const {filename} = await params;
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
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error reading file:', error);
    return NextResponse.json({ error: 'Failed to read file' }, { status: 500 });
  }
} 