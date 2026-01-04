---
title: 'CM-Colors: Perceptually-Minimal Color Optimization for Web Accessibility'
tags:
  - Python
  - web accessibility
  - color contrast
  - WCAG compliance
  - perceptual uniformity
  - OKLCH color space
  - optimization
authors:
  - name: Lalitha A R
    orcid: 0009-0001-7466-3531
    affiliation: 1
affiliations:
  - name: Indian Institute of Technology Madras, India
    index: 1
date: 4 January 2026
bibliography: paper.bib
---

# Summary

Web accessibility guidelines require sufficient color contrast between text and backgrounds to ensure readability for users with visual impairments. However, manually adjusting colors to meet Web Content Accessibility Guidelines (WCAG) often forces designers to make arbitrary modifications that compromise brand aesthetics. `CM-Colors` is a Python library that automatically generates WCAG-compliant colors while minimizing perceptual change to original design choices. The library treats accessibility correction as a constrained optimization problem in the perceptually uniform OKLCH color space, preserving brand identity through absolute hue invariance while adjusting only lightness and chroma as needed. With a median perceptual change of only 0.76 ΔE₂₀₀₀ for successful corrections and sub-millisecond processing times, `CM-Colors` enables developers to achieve accessibility compliance without sacrificing visual design integrity.

# Statement of Need

Insufficient color contrast is one of the most prevalent web accessibility issues, affecting millions of websites [@webaim2025; @martins2024]. WCAG 2.1 requires minimum contrast ratios of 4.5:1 for normal text and 3:1 for large text to meet AA compliance standards [@wcag21]. While color contrast checking tools readily identify violations, existing solutions typically suggest binary fixes—making text darker or lighter by arbitrary amounts—that frequently compromise carefully crafted brand identities.

Current accessibility tools fall into two categories: **checkers** that identify violations without providing corrections, and **adjusters** that operate in perceptually non-uniform color spaces (RGB, HSL) leading to excessive visual changes [@webaim_contrast; @accessible_colors]. Neither approach balances accessibility requirements with aesthetic preservation, creating friction between inclusive design and brand consistency.

`CM-Colors` addresses this gap by implementing a multi-phase optimization algorithm that:

1. **Operates in perceptually uniform OKLCH color space** [@oklab_model], ensuring numerical changes correspond to equal visual differences
2. **Preserves brand identity through absolute hue constraint**, modifying only lightness and chroma
3. **Provides context-adaptive optimization modes** for different use cases (enterprise brand compliance vs. general web development)
4. **Achieves real-time performance** (0.876ms median per color pair) suitable for interactive design tools

The library successfully resolves accessibility violations in 77.22% of cases (strict mode) to 98.73% (relaxed mode) with 88.51% of successful corrections being virtually imperceptible (ΔE₂₀₀₀ < 2.0). This represents a practical implementation of the Design Harmony principle from the Comfort Mode Framework [@comfort_mode_framework], demonstrating that accessibility and aesthetics need not be competing objectives.

# Key Features and Algorithm

`CM-Colors` employs a three-phase optimization strategy:

**Phase 1: Binary Search on Lightness** - Adjusts the L component in OKLCH space through precision-matched binary search (20 iterations ≈ 10⁶ precision levels), as most accessibility violations can be resolved through lightness modifications alone.

**Phase 2: Gradient Descent on Lightness and Chroma** - When lightness adjustments are insufficient, simultaneously optimizes both L and C using numerical gradient computation with adaptive learning rate decay.

**Phase 3: Progressive Constraint Relaxation** - Orchestrates the optimization across incrementally increasing ΔE thresholds (0.8 to 5.0), tracking the globally optimal solution that minimizes perceptual change while meeting WCAG requirements.

The library provides three optimization modes for different contexts:

- **Mode 0 (Strict)**: Limits ΔE ≤ 5.0 for enterprise contexts requiring minimal brand deviation (66.45% success rate)
- **Mode 1 (Recursive - Default)**: Applies iterative refinement with per-step ΔE ≤ 3.0, achieving 93.68% success through compounded small adjustments
- **Mode 2 (Relaxed)**: Accessibility-first mode with extended ΔE budget (≤ 15.0) for challenging cases (98.73% success rate)

Crucially, all modes maintain **absolute hue preservation**, ensuring colors retain their perceptual identity. A "yellow" modified by the algorithm remains recognizably "yellow" because hue—the dominant cue for color naming and brand recognition [@fairchild2013]—is never altered.

# Comparison to Related Work

Existing accessibility tools include WebAIM Contrast Checker [@webaim_contrast], Stark, and axe DevTools (checkers only), and Accessible Colors [@accessible_colors] and Colorable (non-perceptual adjusters). None employ perceptually-aware optimization to minimize aesthetic impact. Academic color science research has established perceptual uniformity principles [@oklab_model; @cie_de2000] but lacks application to accessibility optimization.

`CM-Colors` uniquely combines established color science with modern optimization techniques, providing:

- **Perceptual awareness**: Operations in OKLCH rather than RGB/HSL
- **Brand preservation**: Hue-invariant transformations
- **Context adaptability**: Multiple optimization modes for different use cases
- **Production readiness**: Real-time performance and comprehensive documentation

Commercial design systems (Adobe Color, Material Design) provide pre-defined accessible palettes but cannot correct arbitrary color combinations. `CM-Colors` enables correction of any color pair while preserving design intent.

# Research Applications

The library has been used to generate evaluation datasets for accessibility research, demonstrating algorithm effectiveness on 10,000 procedurally generated color pairs representing realistic web design scenarios. The approach has broader implications for any color manipulation task where brand identity matters, including theming systems, color grading, and automated design tools.

Beyond immediate accessibility compliance, `CM-Colors` demonstrates that perceptual color science can be practically deployed in developer tooling. The hue-preservation insight—that larger ΔE values are acceptable when only lightness and chroma change—challenges conventional assumptions about perceptual change thresholds and opens directions for future work in adaptive interfaces and personalized accessibility optimization.

# Acknowledgements

My deepest gratitude to Mr. Krishna, whose constancy forms the foundation upon which all my work rests. I thank Ms. Aakriti Jain for technical review assistance, and the open-source community for feedback that motivated algorithm improvements.

# References
