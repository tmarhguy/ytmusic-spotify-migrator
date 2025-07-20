with open("music-taste.txt") as input_file:
    lines = input_file.readlines()

with open("output.csv", "w") as output_file:
    output_file.write("Title,Artist,Album,Duration" + "\n")

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line:  # Non-empty line
            # Check if this line contains a duration (song ending)
            if (
                any(char.isdigit() for char in line)
                and ":" in line
                and not any(char.isalpha() for char in line)
            ):
                # This is a duration, skip it for now (we'll handle it when building the song)
                i += 1
                continue

            # Start collecting song data
            song_parts = []
            song_parts.append(line)  # First line is the title
            i += 1

            # Collect all parts until we hit a duration
            while i < len(lines):
                current_line = lines[i].strip()

                if current_line:
                    # Check if this is a duration
                    if (
                        any(char.isdigit() for char in current_line)
                        and ":" in current_line
                        and not any(char.isalpha() for char in current_line)
                    ):
                        # Found duration, process the song
                        if len(song_parts) >= 2:  # Need at least title and artist
                            title = song_parts[0]

                            # Handle artist (may include &, feat., etc.)
                            if len(song_parts) == 2:
                                artist = song_parts[1]
                                album = ""
                            elif len(song_parts) == 3:
                                artist = song_parts[1]
                                album = song_parts[2]
                                # If album is same as title, it's likely a single
                                if album == title:
                                    album = ""
                            else:
                                # Multiple parts - need to figure out artist vs album
                                # Check if last part is same as title (indicating it's a single)
                                potential_album = song_parts[-1]
                                if potential_album == title:
                                    # It's a single, so no separate album name
                                    album = ""
                                    artist_parts = song_parts[
                                        1:-1
                                    ]  # Middle parts only (exclude title duplicate)
                                else:
                                    # Last part is different, so it's likely the album
                                    album = potential_album
                                    artist_parts = song_parts[
                                        1:-1
                                    ]  # Middle parts are artist

                                # Join artist parts, handling separators like &
                                artist = " ".join(artist_parts)

                            # Clean up artist field (remove extra spaces)
                            artist = " ".join(
                                artist.split()
                            )  # This removes extra whitespace

                            # Write to CSV (escape quotes and commas properly)
                            title = title.replace('"', '""')
                            artist = artist.replace('"', '""')
                            album = album.replace('"', '""')

                            output_file.write(
                                f'"{title}","{artist}","{album}","{current_line}"\n'
                            )

                        break
                    else:
                        song_parts.append(current_line)

                i += 1
        else:
            i += 1

import csv

with open("output.csv") as output_file:
    csv_reader = csv.reader(output_file)
    count = 1
    for row in csv_reader:
        print("Line " + str(count) + ": " + str(len(row)) + " fields")
        if len(row) != 4:
            print(f"  Problem line: {row}")
        count += 1
