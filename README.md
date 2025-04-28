# MCP (Model Context Protocol) server for Dataverse

Credits: this work is funded by [SSHOC-NL](https://sshoc.nl) project developing [Semantic Croissant](https://docs.google.com/document/d/1fi9Lb6x5Wm0L9CZftqjSGElV_ifcSW_IT-H8ZlpbrtQ/edit?tab=t.0). First version of [Croissant ML](https://docs.mlcommons.org/croissant/docs/croissant-spec.html) export for Dataverse was implemented by Phil Durbin (Harvard IQSS) and Slava Tykhonov (DANS-KNAW).

Installation:
```
cp .env-sample .env
docker-compose build
docker-compose up -d
```

Go to http://127.0.0.1:8000/tools to get an overview of available tools.

You can register MCP in Cursor, Visual Studio or Windsurf Editor, or other IDE with AI Agents support. For example, create configuration file for Cursor [~/.cursor/mcp.json](https://docs.cursor.com/context/model-context-protocol):
```
{
  "mcpServers": {
    "Croissant": {
      "url": "http://127.0.0.1:8000/sse",
      "headers": {
        "Content-Type": "application/json"
      }
    }
}
}
```

## Test Croissant ML support for Dataverse
```
curl -X POST "http://localhost:8000/tools/dataset_convert_to_croissant_ml" -H "Content-Type: application/json" -d '{"doi":"doi:10.7910/DVN/WGCRY7"}'
```

## Connect MCP to your favourite IDE

Type in the chat of Agent:
```
Connect to MCP server running on http://127.0.0.1:8000 and explore all tools.

Explore dataset doi:10.7910/DVN/6TFFPG
```
If everything is connected properly you should see this response from the Agent:
```
Based on the dataset information, this is a scientific dataset related to quantum physics research. Here are the key details:
Dataset Title: "Replication Data for: All-Optical Photoluminescence Spectra of Nitrogen-Vacancy Ensembles in Diamond at Low Magnetic Fields"
Description:
This dataset contains experimental data from research on Nitrogen-Vacancy (NV) centers in diamond
It includes data shown in both the main text and supplemental material of the associated scientific paper
The research focuses on photoluminescence spectra at low magnetic fields
Content:
The dataset contains 30 CSV files organized into several categories:
Main figures data (Fig.2b, Fig.2c, Fig.2d, etc.)
Supplemental figures data (Fig.S2, Fig.S6, Fig.S7, etc.)
Experimental and simulation data for different conditions:
Different nitrogen isotopes (14N and 15N)
Various magnetic field strengths (0.5mT, 1mT, etc.)
Different power levels (2mW, 50mW)
Lock-in amplifier measurements
File Types:
All files are in CSV format
Files are named according to their corresponding figures in the paper
Some files are 1D data (single measurements)
Some files are 2D data (spectra or multiple measurements)
Technical Details:
License: CC0 1.0 (Public Domain)
Keywords: All-Optical, Nitrogen vacancy centers in diamond, Quantum Sensing
Created: April 28, 2025
This dataset would be valuable for:
Quantum physics researchers studying NV centers
Scientists working on quantum sensing applications
Researchers developing diamond-based quantum technologies
Those interested in reproducing or verifying the published results
Would you like me to:
Download and analyze specific data files?
Look for patterns in the experimental results?
Compare experimental and simulation data?
Focus on a particular aspect of the research?
Please let me know what aspect you'd like to explore further.
```
