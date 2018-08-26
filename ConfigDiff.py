#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ConfigDiffReports

A Tool to report on the configuration changes that have happened in the last week
and gather the commit info that happened for the repo
"""

__author__ = "Ajaydeep Singh / asingh@rsglab.com"
__version__ = "0.1.0"

import argparse
import logging
import git
from git import Repo
import os
import os.path as osp

DATE_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S%z"
EMPTY_TREE_SHA   = "4b825dc642cb6eb9a060e54bf8d69288fbee4904" # Github secret empty tree SHA 

join = osp.join
path = "/Users/asingh/Github/device_config" # local path of repo you want to report diffs on
diffStats = [] # Initialize list for commit information 

def main():
    """Entry point of the app."""
    logging.basicConfig(filename='debug.log', level=logging.DEBUG)
    WEEK = 355


    for x in versions(path):
        diffStats.append(x)

    current = diffStats[0] # Get latest commit
    weekago = diffStats[WEEK] # Get commit from a week ago
    twoweeksago = diffStats[WEEK*2]

    # initialize the Repo object to use for git diff
    repo = git.Repo(path) 

    # Create file for .diff
    f = open('week.diff','w')
    # print out diff to file
    f.write(repo.git.diff(current['commit'], weekago['commit'], exclude='*.cfg'))
    f.close

    # Create file for .diff
    f = open('twoweek.diff', 'w')
    # print out diff to file
    f.write(repo.git.diff(current['commit'], twoweeksago['commit'], exclude='*.cfg'))
    f.close



def versions(path, branch='master'):
    """This function returns a generator which iterates through all commits of
    the repository located in the given path for the given branch. It yields
    file diff information to show a timeseries of file changes."""
    repo = git.Repo(path)
    # Iterate through every commit for the given branch in the repository
    for commit in repo.iter_commits(branch):
        parent = commit.parents[0] if commit.parents else EMPTY_TREE_SHA
        diffs = {
            diff.a_path: diff for diff in commit.diff(parent)
        }
        # The stats on the commit is a summary of all the changes for this
        # commit, we'll iterate through it to get the information we need.
        for objpath, stats in commit.stats.files.items():
            # Select the diff for the path in the stats
            diff = diffs.get(objpath)
            # If the path is not in the dictionary, it's because it was
            # renamed, so search through the b_paths for the current name.
            if not diff:
                for diff in diffs.values():
                    if diff.b_path == path and diff.renamed:
                        break
            # Update the stats with the additional information
            stats.update({
                'object': os.path.join(path, objpath),
                'commit': commit.hexsha,
                'author': commit.author.email,
                'timestamp': commit.authored_datetime.strftime(DATE_TIME_FORMAT),
                'size': diff_size(diff),
                'type': diff_type(diff),
            })

            yield stats


def diff_size(diff):
    """
    Computes the size of the diff by comparing the size of the blobs.
    """
    if diff.b_blob is None and diff.deleted_file:
        return diff.a_blob.size * -1

    if diff.a_blob is None and diff.new_file:
        return diff.b_blob.size

    # Otherwise just return the size a-b
    return diff.a_blob.size - diff.b_blob.size


def diff_type(diff):
    """
    Determines the type of the diff by looking at the diff flags.
    """
    if diff.renamed: return 'R'
    if diff.deleted_file: return 'D'
    if diff.new_file: return 'A'
    return 'M'
    
# Dont really need an argparse
# This is all boilerplate for argparse if its needed down the line
if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("arg", help="Required positional argument")
    # parser.add_argument("-f", "--flag", action="store_true", default=False)
    # parser.add_argument("-n", "--name", action="store", dest="name")
    
    # # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    # parser.add_argument(
    #     "-v",
    #     "--verbose",
    #     action="count",
    #     default=0,
    #     help="Verbosity (-v, -vv, etc)")

    # # Specify output of "--version"
    # parser.add_argument(
    #     "--version",
    #     action="version",
    #     version="%(prog)s (version {version})".format(version=__version__))

    # args = parser.parse_args()
    main()
