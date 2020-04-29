# duplicate-video-finder
DuplicateFinder is a Python module (heavily WIP) to detect duplicate videos in a directory.

## Features

- [x] Detect exact video duplicates
- [ ] Detect similar video duplicates
- [x] Recursive directory support
- [x] Multi file format support (mp4, mov, webm)
- [ ] Interactive Manual CLI deletion
- [ ] Auto deletion mode

## Usage Examples

In your script, import the module DuplicateFinder:

``` Python
import DuplicateFinder
```

Create a new instance of DuplicateFnder:

``` Python
duplicate_finder = DuplicateFinder('path_to_dir')
```

Find duplicates:

``` Python
DuplicateFinder.find_dups()
```

Show formatted results:
``` Python
DuplicateFinder.get_results()
```

### Recursion

Recursive searching is disabled by default. To enable it, when initialising DuplicateFInder, use:
``` Python
duplicate_finder = DuplicateFinder('path_to_dir', recursive=True)
```