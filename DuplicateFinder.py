"""
A module that helps to detetc duplicate videos in a folder.
Supports mp4, mov, webm. More formats may be included in the future.
Supports recursive search in a folder.
Separates videos into buckets of unique videos.
"""

from io import BufferedReader
from os import walk, path
import subprocess
import time
import hashlib
from collections import defaultdict
from typing import Callable


def timeit(method):
    """
    decorator method to measure execution time
    """

    def timed(*args, **kw):
        time_start = time.time()
        result = method(*args, **kw)
        time_end = time.time()
        print((time_end - time_start) * 1000)
        return result

    return timed


class DuplicateFinder:
    """
    DuplicateFinder class.
    Contains methods etc.
    Idk how to write a class docstring.
    Inspired by this StackOverflow post:
    https://stackoverflow.com/a/3593153
    """

    def __init__(self, video_dir: str, recursive: bool = False):
        """
        video_dir (String): Path to videos.
        recursive (Boolean): Toggle recursive search on/off. Default off.
        """
        super().__init__()

        if not isinstance(video_dir, str):
            raise TypeError("Argument videoDir must be a string!")
        self.video_dir = video_dir

        if not isinstance(recursive, bool):
            raise TypeError("Optional argument Recursive must be a Boolean!")
        self.recursive = recursive

        # accepted file formats
        self.types = ["mp4", "mov", "webm"]

        # list of videos
        self.videos_list = []

        # buckets of dups
        self.buckets = []

    def generate_videos_list(self):
        """
        Returns a list of all videos in directory
        May/May not be recursive
        """
        videos_list = []
        for (dirpath, _, filenames) in walk(self.video_dir):
            videos = [
                path.join(dirpath, f)
                for f in filenames
                if f.split(".")[-1] in self.types
            ]
            videos_list.extend(videos)
            if not self.recursive:
                break
        return videos_list

    def get_duration(self, _video_path):
        """
        Returns duration of video in milliseconds
        """
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                _video_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=True,
        )
        return float(result.stdout)

    def chunk_reader(self, fobj: BufferedReader, chunk_size: int = 1024):
        """
        Generator that reads a file in chunks of bytes
        """
        while True:
            chunk = fobj.read(chunk_size)
            if not chunk:
                return
            yield chunk

    def get_hash(
        self,
        filename: str,
        first_chunk_only: bool = False,
        hash_algo: Callable = hashlib.sha1,
    ):
        """
        Gets the hash of either the first chunk of file or whole file.
        """
        hashobj = hash_algo()
        with open(filename, "rb") as _f:
            if first_chunk_only:
                hashobj.update(_f.read(1024))
            else:
                for chunk in self.chunk_reader(_f):
                    hashobj.update(chunk)
        return hashobj.digest()

    def pure_dups(self):
        """
        Finds exact duplicates.
        Inspired by https://gist.github.com/tfeldmann/fc875e6630d11f2256e746f67a09c1ae
        """
        files_by_size = defaultdict(list)
        files_by_small_hash = defaultdict(list)
        files_by_full_hash = dict()

        for full_path in self.videos_list:
            try:
                # if the target is a symlink (soft one), this will
                # dereference it - change the value to the actual target file
                full_path = path.realpath(full_path)
                file_size = path.getsize(full_path)
            except OSError:
                # not accessible (permissions, etc) - pass on
                continue
            files_by_size[file_size].append(full_path)

        # For all files with the same file size, get their hash on the first 1024 bytes
        for size, files in files_by_size.items():
            if len(files) < 2:
                continue  # this file size is unique, no need to spend cpu cycles on it

            for filename in files:
                try:
                    small_hash = self.get_hash(filename, first_chunk_only=True)
                except OSError:
                    # the file access might've changed till the exec point got here
                    continue
                files_by_small_hash[(size, small_hash)].append(filename)

        # For all files with the hash on the first 1024 bytes, get their hash on the full
        # file - collisions will be duplicates
        for files in files_by_small_hash.values():
            if len(files) < 2:
                # the hash of the first 1k bytes is unique -> skip this file
                continue

            for filename in files:
                try:
                    full_hash = self.get_hash(filename, first_chunk_only=False)
                except OSError:
                    # the file access might've changed till the exec point got here
                    continue

                if full_hash in files_by_full_hash:
                    files_by_full_hash[full_hash].append(filename)
                else:
                    files_by_full_hash[full_hash] = [filename]

        dups = [items for items in files_by_full_hash.values() if len(items) > 1]
        self.buckets = dups

    def advanced_dups(self):
        """
        Finds non-exact duplicates
        """
        raise NotImplementedError

    def find_dups(self):
        """
        Find duplicates
        """
        self.videos_list = self.generate_videos_list()

        # find exact copies
        self.pure_dups()

        # exclude exact copies from file list
        flattened_dups = []
        for bucket in self.buckets:
            for filepath in bucket[1:]:
                flattened_dups.append(filepath)

        def to_keep(filepath):
            return filepath not in flattened_dups

        self.videos_list = list(filter(to_keep, self.videos_list))

        # self.advanced_dups()

    def get_results(self):
        """
        Prints detected duplicates in a formatted view.
        """
        dup_buckets = [bucket for bucket in self.buckets if len(bucket) > 1]
        deep_dup_len = sum([len(buckets) for buckets in dup_buckets])
        print("{} duplicate files found\n".format(deep_dup_len - len(dup_buckets)))

        for bucket in dup_buckets:
            for file_path in bucket:
                print("- {}".format(file_path))
            print("\n")


if __name__ == "__main__":
    DUPLICATE_FINDER = DuplicateFinder("test-folder-here", True)
    DUPLICATE_FINDER.find_dups()
    DUPLICATE_FINDER.get_results()
