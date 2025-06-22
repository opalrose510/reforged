import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

function findSaveFolders(dir: string): Array<{ name: string; path: string }> {
  const folders: Array<{ name: string; path: string }> = [];
  
  const items = fs.readdirSync(dir);
  
  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);
    
    if (stat.isDirectory()) {
      // Check if the folder contains any JSON files
      const hasJsonFiles = fs.readdirSync(fullPath).some(file => file.endsWith('.json'));
      if (hasJsonFiles) {
        folders.push({
          name: item,
          path: item
        });
      }
    }
  }
  
  return folders;
}

function findJsonFilesInFolder(dir: string, folderName: string): Array<{ name: string; path: string }> {
  const folderPath = path.join(dir, folderName);
  const files: Array<{ name: string; path: string }> = [];
  
  if (!fs.existsSync(folderPath)) {
    return files;
  }
  
  const items = fs.readdirSync(folderPath);
  
  for (const item of items) {
    if (item.endsWith('.json')) {
      files.push({
        name: item,
        path: `${folderName}/${item}`
      });
    }
  }
  
  return files;
}

export async function GET(request: Request) {
  try {
    const savesDir = path.join(process.cwd(), "..", "saves");
    
    if (!fs.existsSync(savesDir)) {
      console.error("Saves directory not found:", savesDir);
      return NextResponse.json({ error: "Saves directory not found" }, { status: 404 });
    }

    const { searchParams } = new URL(request.url);
    const folder = searchParams.get('folder');

    if (folder) {
      // Return files within the specified folder
      const files = findJsonFilesInFolder(savesDir, folder);
      return NextResponse.json(files);
    } else {
      // Return all save folders
      const folders = findSaveFolders(savesDir);
      return NextResponse.json(folders);
    }
  } catch (error) {
    console.error("Error reading saves directory:", error);
    return NextResponse.json({ error: "Failed to read saves directory" }, { status: 500 });
  }
} 