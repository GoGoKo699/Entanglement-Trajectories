# Primary References

The repository separates exact spectral geometry, product-formula simulation, random-matrix references, and empirical trajectory analysis. The primary sources below anchor those layers.

## M. A. Nielsen
**Conditions for a Class of Entanglement Transformations.** Physical Review Letters 83, 436–439 (1999). DOI: `10.1103/PhysRevLett.83.436`.

## D. N. Page
**Average Entropy of a Subsystem.** Physical Review Letters 71, 1291–1294 (1993). DOI: `10.1103/PhysRevLett.71.1291`.

## S. Sen
**Average Entropy of a Quantum Subsystem.** Physical Review Letters 77, 1–3 (1996). DOI: `10.1103/PhysRevLett.77.1`.

## J. Wishart
**The Generalised Product Moment Distribution in Samples from a Normal Multivariate Population.** Biometrika 20A, 32–52 (1928). DOI: `10.1093/biomet/20A.1-2.32`.

## V. A. Marchenko and L. A. Pastur
**Distribution of Eigenvalues for Some Sets of Random Matrices.** Mathematics of the USSR-Sbornik 1, 457–483 (1967). DOI: `10.1070/SM1967v001n04ABEH001994`.

## J. Baik, G. Ben Arous, and S. Péché
**Phase Transition of the Largest Eigenvalue for Nonnull Complex Sample Covariance Matrices.** Annals of Probability 33, 1643–1697 (2005). DOI: `10.1214/009117905000000233`.

## H. Li and F. D. M. Haldane
**Entanglement Spectrum as a Generalization of Entanglement Entropy.** Physical Review Letters 101, 010504 (2008). DOI: `10.1103/PhysRevLett.101.010504`.

## M. B. Hastings
**An Area Law for One-Dimensional Quantum Systems.** Journal of Statistical Mechanics P08024 (2007). DOI: `10.1088/1742-5468/2007/08/P08024`.

## U. Schollwöck
**The Density-Matrix Renormalization Group in the Age of Matrix Product States.** Annals of Physics 326, 96–192 (2011). DOI: `10.1016/j.aop.2010.09.012`.

## D. Gross, S. T. Flammia, and J. Eisert
**Most Quantum States Are Too Entangled To Be Useful as Computational Resources.** Physical Review Letters 102, 190501 (2009). DOI: `10.1103/PhysRevLett.102.190501`.

## A. M. Childs, Y. Su, M. C. Tran, N. Wiebe, and S. Zhu
**Theory of Trotter Error with Commutator Scaling.** Physical Review X 11, 011020 (2021). DOI: `10.1103/PhysRevX.11.011020`.

## Closest Conceptual Literature

These papers are included because they share the project’s conceptual move or methodological neighborhood. The ordering reflects proximity to the present spectrum-path and multi-metric viewpoint, not priority or citation count. See [`docs/CONCEPTUAL_NEIGHBORS.md`](docs/CONCEPTUAL_NEIGHBORS.md) for the full relationship map.

### 1. Po-Yao Chang, Xiao Chen, Sarang Gopalakrishnan, and J. H. Pixley
**Evolution of Entanglement Spectra under Generic Quantum Dynamics.** *Physical Review Letters* **123**, 190602 (2019). DOI: [`10.1103/PhysRevLett.123.190602`](https://doi.org/10.1103/PhysRevLett.123.190602).

**Relationship to this project:** Treats the entanglement spectrum itself as a dynamical object and separates local random-matrix statistics from the global evolving spectrum. The project studies cross-metric trajectory morphology rather than primarily entanglement-level statistics and relaxation timescales.

### 2. Zhi-Cheng Yang, Alioscia Hamma, Salvatore M. Giampaolo, Eduardo R. Mucciolo, and Claudio Chamon
**Entanglement Complexity in Quantum Many-Body Dynamics, Thermalization and Localization.** *Physical Review B* **96**, 020408 (2017). DOI: [`10.1103/PhysRevB.96.020408`](https://doi.org/10.1103/PhysRevB.96.020408).

**Relationship to this project:** Starts from the same motivation that entanglement has structure that cannot be compressed faithfully into one scalar entropy. The paper emphasizes entanglement-spectrum statistics and disentangling complexity; the project emphasizes relations among several metric trajectories.

### 3. Xiao Chen and Andreas W. W. Ludwig
**Universal Spectral Correlations in the Chaotic Wave Function and the Development of Quantum Chaos.** *Physical Review B* **98**, 064309 (2018). DOI: [`10.1103/PhysRevB.98.064309`](https://doi.org/10.1103/PhysRevB.98.064309).

**Relationship to this project:** Uses subsystem density-matrix eigenvalues, including the top of the spectrum, to diagnose the development of chaos in a wave function. The project does not define chaos through a spectral ramp and does not claim every tested condition is independently chaotic.

### 4. Zhi-Cheng Yang, Claudio Chamon, Alioscia Hamma, and Eduardo R. Mucciolo
**Two-Component Structure in the Entanglement Spectrum of Highly Excited States.** *Physical Review Letters* **115**, 267206 (2015). DOI: [`10.1103/PhysRevLett.115.267206`](https://doi.org/10.1103/PhysRevLett.115.267206).

**Relationship to this project:** Provides a close analogy to a shared universal component coexisting with nonuniversal information in the same entanglement-spectrum object. The two-component paper decomposes an entanglement spectrum; the project analyzes common and residual structure across projected trajectories.

### 5. Shreya Vardhan and Sanjay Moudgalya
**Entanglement Dynamics from Universal Low-Lying Modes.** *Physical Review B* **113**, 014308 (2026). DOI: [`10.1103/prp6-y5hl`](https://doi.org/10.1103/prp6-y5hl).

**Relationship to this project:** Explains how distinct Rényi entropies can display common late-time structure because of shared low-lying modes in replicated dynamics. The project does not derive a universal quasiparticle or membrane-mode theory and its finite deterministic dataset has narrower scope.

### 6. Yi-Zhuang You and Yingfei Gu
**Entanglement Features of Random Hamiltonian Dynamics.** *Physical Review B* **98**, 014309 (2018). DOI: [`10.1103/PhysRevB.98.014309`](https://doi.org/10.1103/PhysRevB.98.014309).

**Relationship to this project:** Replaces one preferred entropy with a structured collection of entanglement features describing a unitary process. Entanglement features range over bipartitions and replicated quantities; the project follows several functionals of one declared spectrum path.

### 7. Hui Li and F. D. M. Haldane
**Entanglement Spectrum as a Generalization of Entanglement Entropy: Identification of Topological Order in Non-Abelian Fractional Quantum Hall Effect States.** *Physical Review Letters* **101**, 010504 (2008). DOI: [`10.1103/PhysRevLett.101.010504`](https://doi.org/10.1103/PhysRevLett.101.010504).

**Relationship to this project:** Established the spectrum-first viewpoint and the idea that spectral structure can serve as a physical fingerprint beyond one entropy. The project makes no topological-order claim and does not identify its trajectory class with a mathematical topological invariant.

### 8. M. A. Nielsen
**Conditions for a Class of Entanglement Transformations.** *Physical Review Letters* **83**, 436 (1999). DOI: [`10.1103/PhysRevLett.83.436`](https://doi.org/10.1103/PhysRevLett.83.436).

**Relationship to this project:** Supplies the majorization order that mathematically organizes when Schur-concave entanglement measures must agree. Nielsen studies deterministic LOCC convertibility; the project studies metric ordering and trajectories under physical dynamics.

### 9. Tianci Zhou and Adam Nahum
**Emergent Statistical Mechanics of Entanglement in Random Unitary Circuits.** *Physical Review B* **99**, 174205 (2019). DOI: [`10.1103/PhysRevB.99.174205`](https://doi.org/10.1103/PhysRevB.99.174205).

**Relationship to this project:** Provides a clear example in which different Rényi entropies share one emergent dynamical framework without becoming identical. The project is a deterministic finite-size numerical atlas rather than an analytical statistical-mechanics theory of random circuits.

### 10. Anushya Chandran, Vedika Khemani, and S. L. Sondhi
**How Universal Is the Entanglement Spectrum?.** *Physical Review Letters* **113**, 060501 (2014). DOI: [`10.1103/PhysRevLett.113.060501`](https://doi.org/10.1103/PhysRevLett.113.060501).

**Relationship to this project:** Provides the necessary caution that informative entanglement-spectrum features need not be universal phase invariants. The project studies dynamical metric projections and does not claim a phase invariant, entanglement-Hamiltonian universality, or topological theorem.
