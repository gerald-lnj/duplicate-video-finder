# duplicate-video-finder

DuplicateFinder is a Python module (heavily WIP) to detect duplicate videos in a directory.

## Features

- [x] Detect exact video duplicates
- [ ] Detect similar video duplicates
- [x] Recursive directory support
- [x] Multi file format support (mp4, mov, webm)
- [ ] Interactive Manual CLI deletion
- [ ] Auto deletion mode

## Requirements

- Python 3
- ffprobe

## Usage Examples

In your script, import the module DuplicateFinder:

``` Python
import DuplicateFinder
```

Create a new instance of DuplicateFnder:

``` Python
duplicate_finder = DuplicateFinder("test-folder-here")
```

Find duplicates:

``` Python
duplicate_finder.find_dups()
```

Show formatted results:

``` Python
duplicate_finder.get_results()
```

### Recursion

Recursive searching is disabled by default. To enable it, when initialising DuplicateFinder, use:

``` Python
duplicate_finder = DuplicateFinder('path_to_dir', recursive=True)
```
