import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

function findJsonFiles(dir: string): Array<{ name: string; path: string }> {
  const files: Array<{ name: string; path: string }> = [];
  
  const items = fs.readdirSync(dir);
  
  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);
    
    if (stat.isDirectory()) {
      // Recursively search subdirectories
      files.push(...findJsonFiles(fullPath));
    } else if (item.endsWith('.json')) {
      // Get the relative path from the saves directory
      const relativePath = path.relative(path.join(process.cwd(), '..', 'saves'), fullPath);
      files.push({
        name: item,
        path: relativePath
      });
    }
  }
  
  return files;
}

export async function GET() {
  try {
    const savesDir = path.join(process.cwd(), "..", "saves");
    
    if (!fs.existsSync(savesDir)) {
      console.error("Saves directory not found:", savesDir);
      return NextResponse.json({ error: "Saves directory not found" }, { status: 404 });
    }
    
    const saveFiles = findJsonFiles(savesDir);
    return NextResponse.json(saveFiles);
  } catch (error) {
    console.error("Error reading saves directory:", error);
    return NextResponse.json({ error: "Failed to read saves directory" }, { status: 500 });
  }
} 