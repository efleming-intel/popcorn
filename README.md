# <img src="popcorn.svg" width=64/> popcorn

![license](https://img.shields.io/badge/license-MIT-green)
![build](https://img.shields.io/badge/build-successful-brightgreen)
![tests](https://img.shields.io/badge/tests-passing-brightgreen)
[![Coverage Status](https://coveralls.io/repos/github/efleming-intel/popcorn/badge.svg?branch=main)](https://coveralls.io/github/efleming-intel/popcorn?branch=main)

popcorn is a cross-platform kernel trace log analyzer written in Python, intended to assist in triaging problems like performance regression. This tool was built with [Intel's Unified Tracing and Profiling Tool](https://github.com/intel/pti-gpu/tree/master/tools/unitrace/README.md) in mind.

## Installation

Note: _Python 3.10 or higher_ is required for popcorn to run correctly.

```bash
git clone https://www.github.com/efleming-intel/popcorn
cd popcorn
pip install .
```

__Dependencies:__

- ijson
- openpyxl
- prettytable

## Quick Start

### Step 1: Generate trace logs using Unitrace

Use unitrace with one of the --chrome-XXXX-logging options to generate a json file which popcorn can read.
(It is recommended that you use **_--chrome-kernel-logging_**).

### Step 2: Use popcorn to analyze the traces

Analyze three files and print result to console:

```bash
popcorn trace_v339.json trace_v226.json trace_v113.json
```

Analyze all .json files in the given folder and output result to an Excel file:

```bash
popcorn -f ./trace_logs -ot xlsx
```

## Usage

```bash
$ popcorn -h
usage: popcorn [-h] [-f] [-o O] [-ot {xlsx,csv,md}] [-a {pops,kdiff} | -A] [-v | -q] [-cat CATEGORY] [--no-uniques] [--version] files [files ...]

analyze kernel hotspots to solve problems like performance regression

positional arguments:
  files                 input trace files (provide at least one)

options:
  -h, --help            show this help message and exit
  -f, --folder, --dir, --directory
                        input name(s) reference(s) folder(s) and not file(s)
  -o O, --output O      output file name (default: result)
  -ot {xlsx,csv,md}, --output-type {xlsx,csv,md}
                        specify output type (default: xlsx)
  -a {pops,kdiff}, --analyzer {pops,kdiff}
                        pops - hotspots; kdiff - kernel differences
  -A, --full-analysis   Use all possible analyzers on the files provided.
  -v, --verbose         give a detailed report (console output only)
  -q, --quiet           give a minimal report (console output only)
  -cat CATEGORY, --restrict-cat CATEGORY
                        e.g. -cat gpu_op
  --no-uniques          disallow collapsing items of the same name into one entry
  --version             show program version number
```

## Understanding the Results

Generally when reading the reports, the most interesting attribute will be located on the far left.

### Reading a hotspots report (pops)

For a hotspots analysis, the kernels are sorted based on their total duration in descending order.
This means the most time consuming kernels are located at the top.

```bash
Displaying the most interesting 20 items out of 188:
+----------------------------------------------------------------------------------------------------------------------+
|                                                     pops__trace                                                     |
+--------+---------+----+------------+-----------------------------------------------+--------------+------------------+
|  dur   |  calls  | ph |    pid     |                      name                     |   category   |    timestamp     |
+--------+---------+----+------------+-----------------------------------------------+--------------+------------------+
| 765602 |   4420  | X  | 4294959103 |                    gen_conv                   |    gpu_op    | 1695711406516161 |
| 377543 |   540   | X  | 4294959103 |    itex::SplitGpuKernel<Eigen::bfloat16, 8>   |    gpu_op    | 1695711399239346 |
| 197115 |    40   | X  | 4294959103 | itex::functor::impl::UnsortedKernel<Eigen::bf |    gpu_op    | 1695711403451535 |
| 194010 |   100   | X  | 4294959103 | itex::functor::internal::NmsPerClassKernel<10 |    gpu_op    | 1695711400642027 |
| 177128 |   919   | X  | 4294959103 |       zeCommandListAppendMemoryCopy(M2D)      |    gpu_op    | 1695711387928273 |
| 168089 |   320   | X  | 4294959103 | itex::InlinedConcatFixedKernel<Eigen::bfloat1 |    gpu_op    | 1695711400512263 |
| 122553 |    60   | X  | 4294959103 |  itex::ConvertFromFp32Kernel<Eigen::bfloat16> |    gpu_op    | 1695711403458005 |
| 106751 |   600   | X  | 4294959103 |                  gemm_kernel                  |    gpu_op    | 1695711401765552 |
| 84550  |    80   | X  | 4294959103 | itex::functor::internal::TopkScoresKernel<8,  |    gpu_op    | 1695711400641661 |
| 67586  |   280   | X  | 4294959103 |  itex::impl::OneHotEncodingKernel<float, int> |    gpu_op    | 1695711401707508 |
|   93   |    20   | X  | 4294959103 | Eigen::internal::ExecExprFunctorKernel<Eigen: |    gpu_op    | 1695711401978327 |
|   89   |    11   | X  | 4294959103 | itex::functor::FillRandomKernel<itex::random: |    gpu_op    | 1695711389384256 |
|   87   |    20   | X  | 4294959103 | Eigen::internal::ExecExprFunctorKernel<Eigen: |    gpu_op    | 1695711402805000 |
|   83   |    20   | X  | 4294959103 | Eigen::internal::ExecExprFunctorKernel<Eigen: |    gpu_op    | 1695711401978418 |
|   82   |    20   | X  | 4294959103 | Eigen::internal::ExecExprFunctorKernel<Eigen: |    gpu_op    | 1695711401992409 |
|   78   |    20   | X  | 4294959103 | Eigen::internal::ExecExprFunctorKernel<Eigen: |    gpu_op    | 1695711401992197 |
|   7    |    1    | X  | 4294959103 | Eigen::internal::ExecExprFunctorKernel<Eigen: |    gpu_op    | 1695711393089695 |
|   0    |  127326 | t  | 4294959103 |                      dep                      | Flow_H2D_1_1 | 1695711387928273 |
|   0    |    2    | M  |   78154    |                  process_name                 |     N/A      | 1695711384948305 |
|   0    |    4    | M  | 4294959103 |                  thread_name                  |     N/A      | 1695711388188134 |
+--------+---------+----+------------+-----------------------------------------------+--------------+------------------+
```

### Reading a kernel differences report (kdiff)

The kernel differences report looks for the largest differences in duration between two kernels of the same name across two traces.
The difference (diff) is located on the far left.
The largest regressions are located at the top while the largest performance increases are located at the bottom.

```bash
Displaying the most interesting 20 items out of 188:
+------------------------------------------------------------------------------------------------------------------------+
|                                                  kdiff__trace1_trace0                                                  |
+--------+------------------------------------------------------------------------------------------------------+--------+
|  diff  |                                                 name                                                 |  cat   |
+--------+------------------------------------------------------------------------------------------------------+--------+
| 291869 |                               itex::SplitGpuKernel<Eigen::bfloat16, 8>                               | gpu_op |
| 133448 |                       itex::InlinedConcatFixedKernel<Eigen::bfloat16, int, 8>                        | gpu_op |
| 18880  |                                  zeCommandListAppendMemoryCopy(M2D)                                  | gpu_op |
| 18489  |   itex::functor::impl::UnsortedKernel<Eigen::bfloat16, int, itex::functor::SumOpGpu<float>, void>    | gpu_op |
|  2179  |         itex::functor::BnBackwardOptimizedKernel<Eigen::bfloat16, float, 4, 2, false, false>         | gpu_op |
|  1543  | Eigen::internal::ExecExprFunctorKernel<Eigen::TensorEvaluator<Eigen::TensorAssignOp<Eigen::TensorMap | gpu_op |
|  1529  | Eigen::internal::ExecExprFunctorKernel<Eigen::TensorEvaluator<Eigen::TensorAssignOp<Eigen::TensorMap | gpu_op |
|  1524  | Eigen::internal::ExecExprFunctorKernel<Eigen::TensorEvaluator<Eigen::TensorAssignOp<Eigen::TensorMap | gpu_op |
|  1516  | itex::GroupReduceKernel<float, float, itex::reduciton_helper::Identity<float const>, itex::reduciton | gpu_op |
|  1286  | Eigen::internal::ExecExprFunctorKernel<Eigen::TensorEvaluator<Eigen::TensorAssignOp<Eigen::TensorMap | gpu_op |
|  -973  |                                               zero_out                                               | gpu_op |
| -1082  | Eigen::internal::ExecExprFunctorKernel<Eigen::TensorEvaluator<Eigen::TensorAssignOp<Eigen::TensorMap | gpu_op |
| -1121  |      itex::functor::BnForwardOptimizedKernel<Eigen::bfloat16, float, 4, 2, false, true, false>       | gpu_op |
| -1218  | itex::functor::internal::TopkScoresKernel<8, 1024, itex::GroupRadixPerBitSelector<unsigned int, 8, 1 | gpu_op |
| -1336  |                                  zeCommandListAppendMemoryCopy(D2M)                                  | gpu_op |
| -1509  |                                             conv_reorder                                             | gpu_op |
| -1790  |                             itex::ConvertFromFp32Kernel<Eigen::bfloat16>                             | gpu_op |
| -2718  |                                             gemm_kernel                                              | gpu_op |
| -6736  | Eigen::internal::ExecExprFunctorKernel<Eigen::TensorEvaluator<Eigen::TensorAssignOp<Eigen::TensorMap | gpu_op |
| -15826 |                                               gen_conv                                               | gpu_op |
+--------+------------------------------------------------------------------------------------------------------+--------+
```

The key to reading this is in the title: kdiff__trace1_trace0. For a given matching kernel, the duration in the second trace (in this case trace 0) is subtracted from the first trace (in this case trace 1). This means that...

- Positive differences are _regressions_ in **trace1** compared to **trace0**.
- Negative differences are _performance increases_ in **trace1** compared to **trace0**.