# Paper and citation

## WisIO: Automated I/O Bottleneck Detection with Multi-Perspective Views for HPC Workflows

**Authors:** Izzet Yildirim, Hariharan Devarajan, Anthony Kougkas, Xian-He Sun,
Kathryn Mohror

**Venue:** Proceedings of the 2025 ACM International Conference on
Supercomputing (ICS'25), Salt Lake City, UT, USA, June 8–11, 2025

**DOI:** [10.1145/3721145.3725742](https://doi.org/10.1145/3721145.3725742)

## Abstract

Modern HPC workloads are increasingly data-dependent, and the growing
diversity of storage technologies makes I/O performance analysis difficult to
do by hand. WisIO analyzes I/O traces from multiple complementary
perspectives — time, process, and file — instead of a single view, scores the
resulting observations, and applies an extensible rule engine to separate
significant bottlenecks from noise and explain their likely causes. The
implementation uses parallel, out-of-core processing so that traces at the
multi-terabyte scale remain tractable.

## Contributions

The paper describes four main contributions:

1. **Multi-perspective analysis framework.** Complementary time-, process-, and
   file-based views increase bottleneck detection coverage substantially
   compared with single-perspective analysis.
2. **Search-space reduction.** The approach prunes the set of candidate
   observations before rule evaluation, making large traces practical to
   analyze.
3. **Metric-driven classification.** A high-throughput classification and
   reasoning pipeline ranks candidate bottlenecks and attaches root causes.
4. **Extensible rule engine.** I/O characteristics map to bottlenecks and
   reasons through rules that can be extended for domain-specific needs.

```{note}
The concrete speedup and throughput numbers are reported in the paper. They
depend on the workload, trace size, and cluster; use the paper's evaluation
section rather than treating any single figure as a general guarantee.
```

## BibTeX

```bibtex
@inproceedings{yildirim2025wisio,
  author    = {Yildirim, Izzet and Devarajan, Hariharan and Kougkas, Anthony
               and Sun, Xian-He and Mohror, Kathryn},
  title     = {{WisIO}: Automated {I/O} Bottleneck Detection with
               Multi-Perspective Views for {HPC} Workflows},
  booktitle = {Proceedings of the 2025 ACM International Conference on
               Supercomputing (ICS'25)},
  address   = {Salt Lake City, UT, USA},
  year      = {2025},
  doi       = {10.1145/3721145.3725742}
}
```

## Citing the software

If you use WisIO itself, cite both the paper and the software. The repository
provides a
[`CITATION.cff`](https://github.com/grc-iit/wisio/blob/main/CITATION.cff)
file, which GitHub renders as a **Cite this repository** button:

```bibtex
@software{wisio,
  title   = {{WisIO}: Workflow I/O Analysis Tool},
  author  = {Yildirim, Izzet and Devarajan, Hariharan and Kougkas, Anthony
             and Sun, Xian-He and Mohror, Kathryn},
  version = {0.2.2},
  url     = {https://github.com/grc-iit/wisio},
  license = {MIT}
}
```

## Resources

- [Paper (DOI)](https://doi.org/10.1145/3721145.3725742)
- [Source code](https://github.com/grc-iit/wisio)
- [Issue tracker](https://github.com/grc-iit/wisio/issues)
- [PyPI package](https://pypi.org/project/wisio/)
