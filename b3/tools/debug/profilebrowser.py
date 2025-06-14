#!/usr/bin/env python3
"""
ProfileBrowser - A command-line profile statistics browser.
This is a simplified version for Python 3 compatibility.
"""
import cmd
import pstats
import sys

class ProfileBrowser(cmd.Cmd):
    """Command-line interface for browsing profile statistics."""
    
    def __init__(self, prof=None):
        cmd.Cmd.__init__(self)
        self.stream = sys.stdout
        self.stats = None
        if prof:
            self.stats = pstats.Stats(prof)
            self.prompt = prof + "% "
        else:
            self.prompt = "% "

    def generic(self, func, line):
        """Generic function for handling profile commands."""
        if self.stats:
            if line.strip():
                # Parse arguments
                args = line.split()
                try:
                    getattr(self.stats, func)(*args)
                except Exception as e:
                    print(f"Error: {e}", file=self.stream)
            else:
                getattr(self.stats, func)()
        else:
            print("No statistics object is loaded.", file=self.stream)
        return 0

    def generic_help(self):
        """Print generic help for profile commands."""
        print("Arguments may be:", file=self.stream)
        print("* An integer maximum number of entries to print.", file=self.stream)
        print("* A decimal fractional number between 0 and 1, controlling", file=self.stream)
        print("  what fraction of selected entries to print.", file=self.stream)
        print("* A regular expression; only entries with function names", file=self.stream)
        print("  that match it are printed.", file=self.stream)

    def do_add(self, line):
        """Add profile info from given file to current statistics object."""
        if line and self.stats:
            self.stats.add(line)
        return 0

    def help_add(self):
        print("Add profile info from given file to current statistics object.", file=self.stream)

    def do_callees(self, line):
        """Print callees statistics from the current stat object."""
        return self.generic('print_callees', line)

    def help_callees(self):
        print("Print callees statistics from the current stat object.", file=self.stream)
        self.generic_help()

    def do_callers(self, line):
        """Print callers statistics from the current stat object."""
        return self.generic('print_callers', line)

    def help_callers(self):
        print("Print callers statistics from the current stat object.", file=self.stream)
        self.generic_help()

    def do_EOF(self, line):
        print("", file=self.stream)
        return 1

    def help_EOF(self):
        print("Leave the profile browser.", file=self.stream)

    def do_quit(self, line):
        return 1

    def help_quit(self):
        print("Leave the profile browser.", file=self.stream)

    def do_read(self, line):
        """Read in profile data from a specified file."""
        if line:
            try:
                self.stats = pstats.Stats(line)
                self.prompt = line + "% "
            except IOError as e:
                print(f"Error reading file: {e}", file=self.stream)
                return
        else:
            print("No file specified.", file=self.stream)
        return 0

    def help_read(self):
        print("Read in profile data from a specified file.", file=self.stream)

    def do_reverse(self, line):
        """Reverse the sort order of the profiling report."""
        if self.stats:
            self.stats.reverse_order()
        return 0

    def help_reverse(self):
        print("Reverse the sort order of the profiling report.", file=self.stream)

    def do_sort(self, line):
        """Sort profile data according to specified keys."""
        if self.stats:
            if line:
                args = line.split()
                try:
                    self.stats.sort_stats(*args)
                except Exception as e:
                    print(f"Error sorting: {e}", file=self.stream)
            else:
                print("Valid sort keys:", file=self.stream)
                print("calls, cumulative, file, line, module, name, nfl, pcalls, stdname, time", file=self.stream)
        return 0

    def help_sort(self):
        print("Sort profile data according to specified keys.", file=self.stream)
        print("(Typing 'sort' without arguments lists valid keys.)", file=self.stream)

    def do_stats(self, line):
        """Print statistics from the current stat object."""
        return self.generic('print_stats', line)

    def help_stats(self):
        print("Print statistics from the current stat object.", file=self.stream)
        self.generic_help()

    def do_strip(self, line):
        """Strip leading path information from filenames in the report."""
        if self.stats:
            self.stats.strip_dirs()
        return 0

    def help_strip(self):
        print("Strip leading path information from filenames in the report.", file=self.stream)