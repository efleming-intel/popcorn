# popcorn

popcorn is a cross-platform kernel trace log analyzer written in Python, intended to assist in triaging problems like performance regression.

## Installation

```bash
git clone https://www.github.com/efleming-intel/popcorn
cd popcorn
make install
```

__Dependencies:__

- openpyxl
- prettytable

## Quick Start

__Use all default settings:__
_(popcorn will decide which analyzers to use)_

```bash
popcorn trace_bad.json trace_good.json trace_weird.json ...
```

__Use all possible analyzers:__

```bash
popcorn -A trace.json
```

__Hotspots Analysis:__
_Find most time-intensive kernels in the given trace file(s)._

```bash
popcorn -a pops trace.json
```

__Kernel Differences Analysis:__
_Find the largest differences in duration between each run's kernels._

```bash
popcorn -a kdiff bad_run.json good_run.json
```
