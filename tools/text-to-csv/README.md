# YouTube Music to Spotify Migration Tool

A Python tool for cleaning and converting YouTube Music playlist data from text format to CSV format, making it ready for import into Spotify or other music platforms.

## Overview

This tool processes raw YouTube Music playlist data that contains song titles, artists, albums, and durations, and converts it into a clean, properly formatted CSV file. The original data format has inconsistent spacing, multi-line artist names with collaborations, and duplicate title/album entries that need intelligent parsing.

## Input Data Format

The tool expects a text file (`music-taste.txt`) with the following structure:

```
What About Us
P!NK
Beautiful Trauma
4:30

I Want To Break Free
Queen
The Works
3:19

Die With A Smile
Lady Gaga
 &
Bruno Mars
MAYHEM
4:12
```

Each song entry consists of:

- **Title** (first line)
- **Artist** (may span multiple lines for collaborations)
- **Album** (last line before duration)
- **Duration** (in MM:SS format)
- Multiple empty lines between entries

## Key Features

### 1. Multi-line Artist Handling

The tool intelligently combines artist names that span multiple lines, particularly for collaborations:

- `Lady Gaga` + `&` + `Bruno Mars` → `"Lady Gaga & Bruno Mars"`
- Handles separators like `&`, `feat.`, `featuring`, `ft.`, `with`

### 2. Duplicate Title/Album Detection

When the album name is identical to the song title (common for singles), the tool:

- Sets the album field to empty instead of duplicating the title
- Example: `"My Daddy, My Daddy (Live)"` appears as both title and album → album becomes empty

### 3. Proper CSV Formatting

- All fields are properly quoted and escaped
- Commas within song titles/albums are handled correctly
- Quotes within text are escaped using CSV standards (`"` becomes `""`)

### 4. Duration Pattern Recognition

- Identifies duration patterns (MM:SS format with digits and colon)
- Uses duration as the delimiter to separate song entries

## Usage

1. **Place your data file**: Ensure `music-taste.txt` is in the same directory as `cleaner.py`

2. **Run the cleaner**:

   ```bash
   python3 cleaner.py
   ```

3. **Output**: The tool generates `output.csv` with the cleaned data

## Output Format

The generated CSV file has the following structure:

```csv
Title,Artist,Album,Duration
"What About Us","P!NK","Beautiful Trauma","4:30"
"I Want To Break Free","Queen","The Works","3:19"
"Die With A Smile","Lady Gaga & Bruno Mars","MAYHEM","4:12"
"My Daddy, My Daddy (Live at AiiiH - As It Is In Heaven)","Sunmisola Agbebi & Lawrence Oyor","","13:33"
```

## Algorithm Details

### Processing Steps:

1. **Read all lines** from the input file into memory
2. **Iterate through lines** looking for non-empty content
3. **Collect song parts** until a duration pattern is found
4. **Parse collected parts**:
   - First part = Title
   - Last part before duration = potential Album
   - Middle parts = Artist (may span multiple lines)
5. **Handle special cases**:
   - If album equals title → set album to empty (single)
   - Combine multi-line artist names with proper spacing
6. **Write to CSV** with proper escaping and formatting

### Pattern Recognition:

- **Duration**: `^\d+:\d{2}$` (e.g., "4:30", "13:33")
- **Empty lines**: Used to separate songs but not as delimiters
- **Multi-line artists**: Combined using spaces, preserving separators like "&"

## Code Structure

### Main Components:

1. **File Reading**: Loads entire input file into memory for random access
2. **Pattern Matching**: Identifies duration patterns to segment songs
3. **Data Parsing**: Intelligently separates title, artist, album based on context
4. **CSV Writing**: Properly formats and escapes output data
5. **Validation**: Checks that all output rows have exactly 4 fields

### Key Functions:

- **Duration Detection**: Uses regex pattern to identify MM:SS format
- **Artist Combination**: Joins multi-line artist names intelligently
- **CSV Escaping**: Handles quotes and commas within data fields

## Problem Cases Handled

### 1. Multi-line Collaborations

**Input**:

```
Die With A Smile
Lady Gaga
 &
Bruno Mars
MAYHEM
4:12
```

**Output**: `"Die With A Smile","Lady Gaga & Bruno Mars","MAYHEM","4:12"`

### 2. Duplicate Title/Album (Singles)

**Input**:

```
My Song Title
Artist Name
My Song Title
3:45
```

**Output**: `"My Song Title","Artist Name","","3:45"`

### 3. Complex Titles with Special Characters

**Input**:

```
Song "Title" (Live Version)
Artist & Collaborator
Album: The "Greatest" Hits
4:30
```

**Output**: `"Song ""Title"" (Live Version)","Artist & Collaborator","Album: The ""Greatest"" Hits","4:30"`

## Validation

The tool includes built-in validation that:

- Checks each output row has exactly 4 fields
- Reports any problematic lines during processing
- Uses proper CSV parsing to verify output format

## Requirements

- Python 3.x
- Standard library modules: `csv`, `re`
- Input file: `music-taste.txt`

## File Structure

```
Text to CSV/
├── README.md           # This documentation
├── cleaner.py          # Main processing script
├── music-taste.txt     # Input data file
└── output.csv          # Generated output file
```

## Example Run

```bash
$ python3 cleaner.py
Line 1: 4 fields
Line 2: 4 fields
...
Line 452: 4 fields
```

A successful run will show all lines having exactly 4 fields, indicating proper CSV format.

## Troubleshooting

### Common Issues:

1. **Missing input file**: Ensure `music-taste.txt` exists in the correct directory
2. **Incorrect field count**: Check for unescaped quotes or malformed input data
3. **Empty output**: Verify input file has the expected format with duration patterns

### Data Quality:

- Songs without recognizable duration patterns will be skipped
- Very short artist names (≤ 2 characters) might be treated as separators
- Manual review of output is recommended for complex cases

## Development History

This tool was developed iteratively to handle various edge cases found in real YouTube Music playlist data:

1. **Initial version**: Basic line-by-line processing
2. **V2**: Added multi-line artist support
3. **V3**: Implemented duplicate title/album detection
4. **V4**: Enhanced CSV escaping and validation
5. **Final**: Added comprehensive error checking and documentation

## License

This tool is provided as-is for personal use in migrating music playlists between platforms.
