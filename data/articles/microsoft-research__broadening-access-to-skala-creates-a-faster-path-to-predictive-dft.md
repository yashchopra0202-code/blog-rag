---
url: https://www.microsoft.com/en-us/research/blog/broadening-access-to-skala-creates-a-faster-path-to-predictive-dft/
title: Broadening access to Skala creates a faster path to predictive DFT
site: microsoft-research
date: 2026-08-20
scraped_at: 2026-09-04T13:20:55+00:00
---

Published

By

Share this page

Since

, our deep-learning exchange-correlation functional, we have continued to advance along two complementary fronts: improving accuracy and expanding accessibility across the computational chemistry ecosystem.

On the accuracy front, the

provides the first demonstration of the continuous-improvement paradigm underlying Skala. Trained on 2.5x more data than the first public version of Skala, the updated  model delivers substantially improved performance across key challenges in molecular simulation, including main-group thermochemistry, reaction kinetics, and molecular structure prediction.

But accuracy alone is not enough. DFT is the computational engine behind a vast range of scientific and industrial workflows, spanning chemistry, materials science, catalysis, energy technologies, and drug discovery. To have real-world impact, advanced functionals must be accessible where scientists already perform their calculations. That is why we are also expanding the Skala ecosystem through collaborations with leading electronic-structure software developers.

Today, we are announcing that Skala is available in

and is being integrated into

,

,

and

,  bringing next-generation DFT accuracy closer to the communities that rely on these codes every day. Alongside these integration efforts, we are introducing a living benchmark that tracks the computational performance of successive, increasingly optimized Skala releases. By providing a transparent and continuously updated reference for implementations across software packages and hardware platforms, this resource will help the community measure and accelerate progress toward ever greater accuracy and efficiency.

Together, these developments mark another milestone toward a future in which computational chemistry simulations are both predictive and accessible across a broader range of relevant scientific and industrial workflows.

Want to learn more about Skala and why DFT plays such an important role in in-silico discovery? Read also

.

Unlike the traditional “functional zoo”, where new functionals accumulate without replacing older ones, Skala follows a different philosophy: each release is designed to supersede the previous one. As new data, model architectures, and training strategies become available, the model improves while maintaining the same practical computational cost.

is the latest demonstration of this approach. It achieves a weighted average error of

, a widely used benchmark suite comprising 55 categories of chemistry, including thermochemistry, reaction barriers, and noncovalent interactions. This level of accuracy surpasses today’s leading global (range-separated) hybrid functionals while retaining the efficiency of a semi-local functional. Beyond energies, Skala-1.1 also provides highly accurate electron densities, dipole moments, and molecular geometries.

These advances were enabled by major expansions of the

, our large-scale collection of high-accuracy quantum-chemistry reference data generated with expensive wavefunction methods. For Skala-1.1, we added new categories, including electron affinities and noncovalent clusters, increasing both the size and, crucially, the diversity of the training data. This data-driven approach allows Skala to improve systematically with each generation, moving us closer to a truly scalable and predictive DFT framework.

To fully realize the potential of Skala’s continuously evolving approach to DFT, we need dedicated infrastructure that allows new releases to be rapidly and seamlessly integrated into the major software packages used by scientists in industry and academia. In turn, this will establish the fast feedback loop essential for accelerating Skala’s ongoing development.

We first made Skala available through our

, built on (GPU4)

and

. This enables researchers to evaluate and apply Skala with minimal effort while benefiting from highly optimized CPU and GPU performance.

But no single software package can meet the needs of every application or research community. Computational chemistry and materials science rely on a rich ecosystem of electronic-structure codes, each shaped over decades to tackle specific scientific and industrial challenges. Bringing Skala to this broader ecosystem has therefore been a major focus of the past year. We are fortunate to build on the remarkable foundations created by the DFT community and grateful to the many researchers and developers who are helping to make Skala available within the software platforms that scientists use every day.

Discover how Microsoft is learning from other domains to advance evaluation and testing as a pillar of AI governance.

In collaboration with the team of Prof. Thomas D. Kühne at the

, Skala has been successfully integrated into the open-source

package. With more than 25 years of development, CP2K is a powerhouse for DFT simulations, particularly for large-scale systems and long-timescale molecular dynamics, while also providing a rich portfolio of high-accuracy electronic-structure methods. Skala expands the frontiers of what is possible within CP2K, delivering a step change in DFT accuracy while preserving the computational efficiency needed for simulations at scale. We are excited to see how CP2K’s scale and versatility, combined with Skala’s continuously improving accuracy, will enable new scientific applications and discoveries in the years ahead.

There is more to come. Together with its vibrant developer’s community , we are actively integrating Skala into the open-source

package, an essential platform for molecular electronic-structure research. Combined with the PySCF-based Skala Community Edition, this will make Skala available in three widely used open-source quantum chemistry packages.

Beyond open-source software, we are working closely with leading developers behind

,

, and

, with the goal of making Skala broadly accessible across the major software platforms used in computational chemistry and materials science.

Thorough testing is essential for any new implementation. We want to ensure that Skala delivers consistent accuracy across different codes and computational settings. Together with the CP2K team, we developed a comprehensive suite of integration tests to verify that Skala produces numerically correct and reliable results. We are particularly grateful to the CASUS team, whose deep expertise in the numerical verification of computational methods was instrumental in designing and validating this testing framework.

A detailed discussion of the implementation, validation strategy, and testing infrastructure for Skala in CP2K can be found in our joint paper with the CASUS team: “

.”

Accuracy and broad availability only translate into scientific impact if Skala is also fast. Today, Skala can deliver performance comparable to semi-local meta-GGAs on both CPU’s (with an overhead that disappears for molecules with more than 20-30 atoms) and GPUs, and we are committed to preserving that efficiency as it is integrated across the electronic-structure software ecosystem.

But performance is not a fixed property. New Skala releases, improvements in libraries such as GauXC, and hardware-specific optimizations continuously improve efficiency and reveal new opportunities for further gains. Capturing this progress requires more than a single benchmark snapshot.

To provide a transparent and up-to-date view of Skala’s performance, we are publishing a

that will be updated as new optimizations become available. This report tracks performance across a range of tasks and hardware platforms, while the harness enables package developers to benchmark, validate, and improve their own Skala implementations.

Skala is the product of a truly collaborative effort across AI for Science, and we thank our engineering, project management, and business operations teams for making this work possible. We also thank MSR Accelerator for their partnership in advancing data generation efforts and accelerating software integrations that help bring Skala to the broader scientific community.

Senior Researcher

Senior Researcher

Senior Research Software Engineer

Principal Research Manager

Senior Software Engineer

Senior Researcher

Senior Researcher

Senior Researcher

Senior Researcher

Senior Research Engineer

Senior Data Engineer

Senior Researcher

Senior Researcher

Senior Researcher

Senior Principal Research Manager

Senior Principal Research Manager
