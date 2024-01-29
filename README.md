# <img src="popcorn.svg" width=64/> popcorn

![license](https://img.shields.io/badge/license-MIT-green)
![build](https://img.shields.io/badge/build-successful-brightgreen)
![tests](https://img.shields.io/badge/tests-passing-brightgreen)
![coverage](https://img.shields.io/badge/test_coverage-90%25-green)

popcorn is a cross-platform kernel trace log analyzer written in Python, intended to assist in triaging problems like performance regression. This tool was built with [Intel's Level Zero Tracer](https://github.com/intel/pti-gpu/blob/master/tools/ze_tracer/README.md) in mind.

## Installation

Note: _Python 3.10 or higher_ is required for popcorn to run correctly.

```bash
git clone https://www.github.com/efleming-intel/popcorn
cd popcorn
make install
```

__Dependencies:__

- openpyxl
- prettytable

## Usage
``` sh
> popcorn +[LOG] .. [-h] [-a ANALYZER] [-cat CATEGORY] [-o OUTPUT]
          [-ot OUTPUT_TYPE] [-f, --folder] [--no-uniques]
          [-q, --quiet] [-v, --verbose] [-dnnl] 
```

### Arguments
  - `{-h,--help}` -- display help message and exit.
  - `{-a,--analyzer} STRING` -- pops -> hotspots; kdiff -> kernel differences. Default is `all`.
  - `{-o,--output} STRING` -- output file name. Default is `result`.
  - `{-ot,--output-type} STRING` -- output type. Default is `result`.
  - `{-dnnl}` -- enable oneDNN verbose log parser mode. Default is `False`.
  - `{--no-uniques}` -- disable grouping for similar types. Default is `False`.
  - `{-f,--folder}` -- enable directory as input. Default is `False`.
  - `{-v,--verbose}` -- verbose mode. Default is `False`.
  - `{-q,--quiet}` -- Display minimal report to console. Default is `False`.



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
