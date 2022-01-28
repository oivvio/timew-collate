#!/usr/bin/env python3
#
# timew-taylor
#
# A timewarrior extension to report make csv reports
# that displays cumulative durations for intervals
# with the same set of tags.
#
# These can then be feed into csvlook which will produce output like this
#

import os
import sys

from timewreport.parser import TimeWarriorParser
from collections import Counter


def charbar(width, num):
    """
    Returns a char representation of num that is <width> wide when num == 1.
    """
    block_width = 1.0 / width
    n_whole_blocks = int(num / block_width)

    whole_blocks = chr(0x2588) * n_whole_blocks
    rest = num - (n_whole_blocks * block_width)
    fractions = int((rest / block_width) * 8)
    fraction_char = ["", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"][fractions]

    padding = (width - n_whole_blocks - 1) * " "

    return whole_blocks + fraction_char + padding


def tags2key(tags):
    """A hashable string from a list of tags"""
    return tuple(sorted(tags))


def find_tags_that_are_in_all_intervals(intervals):
    n = len(intervals)
    result = []
    counter = Counter()
    for interval in intervals:
        for tag in interval.get_tags():
            counter[tag] += 1

    for tag, count in counter.items():
        if count == n:
            result.append(tag)
    return result


def get_intervals():
    # Get all intervals in range coming in from stdin
    parser = TimeWarriorParser(sys.stdin)
    return parser.get_intervals()


def get_count(intervals, common_tags):
    """Get a counter mapping tag sets to durations"""
    counter = Counter()
    for interval in intervals:
        tags = interval.get_tags()
        for tag in common_tags:
            tags.remove(tag)
        key = tags2key(tags)
        counter[key] += interval.get_duration().seconds
    return counter


def seconds2hours_minutes_seconds(seconds):
    """seconds -> (hours, minutes, seconds)"""
    hours = int(seconds / 3600)
    seconds = seconds - hours * 3600
    minutes = int(seconds / 60)
    seconds = seconds - minutes * 60
    seconds = int(seconds)
    return (hours, minutes, seconds)


def hms(seconds):
    """seconds -> HH:MM:SS"""
    hours, minutes, seconds = seconds2hours_minutes_seconds(seconds)
    return f"{hours:4}:{minutes:02}:{seconds:02}"


def get_hours(seconds):
    """seconds -> HH.hh"""
    return f"{seconds/3600:.2f}"


def tag_string(tags):
    return " ".join([t.replace(",", " ") for t in tags])


intervals = get_intervals()
common_tags = find_tags_that_are_in_all_intervals(intervals)
counter = get_count(intervals, common_tags)

total_seconds = sum(counter.values())
max_duration = max(counter.values())


header = f"{' '.join(common_tags)} - total hours {get_hours(total_seconds)}, HH:MM:SS, "
print(header)
for key, duration in sorted(counter.items(), key=lambda p: -p[1]):
    bar = charbar(10, duration / max_duration)
    tags = tag_string(key)[:60]
    print(f"{tags}, {hms(duration)},{bar}")
