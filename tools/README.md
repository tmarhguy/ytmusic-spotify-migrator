# Utility Tools

This directory contains utility tools that support the YouTube Music to Spotify migration workflow.

## Available Tools

### 🛠️ [text-to-csv](./text-to-csv/)

A preprocessing tool for cleaning and converting raw YouTube Music playlist data from text format to CSV format.

**Use Case**: When you export playlist data from YouTube Music and get an unstructured text file, this tool converts it into a clean CSV that can be processed by the main migration tool.

**Workflow Integration**:

```
Raw YouTube Music Data → text-to-csv → Clean CSV → yt2spot migrate
```

See the [text-to-csv README](./text-to-csv/README.md) for detailed usage instructions.

## Tool Development

Each tool in this directory should:

- Be self-contained with its own README
- Follow the same code quality standards as the main project
- Include sample data and clear usage examples
- Be integrated into the main documentation

## Contributing

When adding new tools:

1. Create a new subdirectory with a descriptive name
2. Include a comprehensive README with examples
3. Add the tool to this index
4. Update the main project documentation to reference the tool
