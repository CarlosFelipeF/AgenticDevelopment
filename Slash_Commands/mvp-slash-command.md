# Slash Command: /mvp [FILENAME]

Usage: `/mvp prd.md` or `/mvp path/to/spec-file.md`

Please use a tracer bullet MVP process-driven approach based on the product specification file provided. Read the file first, then apply these principles:

**Important: Ask clarifying questions throughout the planning process to ensure you provide the optimal solution. Do not make assumptions.**

## Methodology

- **Critical Path Planning**: Identify essential features and dependencies first
- **TDD Methodology**: Write tests/requirements before implementation
- **Tracer Bullet Approach**: Build simplest working version first, then iterate
- **Process-Driven**: Break down into clear, ordered steps with dependencies mapped

## Modular Context Architecture (Context Window Optimization)

- Propose a modular documentation structure (not one massive file)
- Split by concern: components.md, api.md, auth.md, etc.
- Each file should be small and focused, loadable on-demand
- Goal: Only load what's relevant for the current task to keep context lean
- Avoid polluting context with irrelevant information
- Specify which files should be loaded for which type of work (e.g., "Load api.md when working on backend")

## Structure your response as:

- Core MVP features (absolute minimum to work)
- Critical path order (what must happen first)
- Test scenarios to validate each step
- Proposed modular file structure

## Plan Output

At the end, create a **plan.md** file that includes:

- Numbered phases (Phase 1, Phase 2, etc.)
- Each phase with clear deliverables and dependencies
- TDD test scenarios per phase
- A note at the top instructing Claude to ask which phase to implement when loaded in a new conversation

**Tools, Frameworks & Infrastructure:**

Unless already specified in the product specification file, please choose the best tools, frameworks, and technologies appropriate for this project. When selecting infrastructure:

- Research online before making any decisions to ensure you're using the latest and most cost-effective solutions
- Prefer the cheapest solution on AWS, ideally one that works within the free tier
- Prefer serverless architecture when possible
