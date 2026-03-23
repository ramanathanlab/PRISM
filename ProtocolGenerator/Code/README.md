A simulation platform for autonomous laboratory environments that integrates Isaac Sim (NVIDIA's 3D simulation software) with [MADSci](https://github.com/AD-SDL/MADSci) (Argonne National Laboratory's experiment orchestration software). This system enables autonomous agents to convert scientific protocols into executable robot commands, run them in a physics-based simulation, and iteratively refine protocols based on execution feedback.

## Prerequisites

- Linux (tested on Ubuntu 22.04)
- Python 3.11+ and Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/) (for MADSci services)
- NVIDIA GPU with drivers supporting Isaac Sim 5.1

## Environment Setup

This project uses two separate virtual environments managed by uv.

**Isaac Sim environment** (Python 3.11): 3D physics simulation

| Component | Version |
|-----------|---------|
| Python | 3.11 |
| Isaac Sim | 5.1.0 |

**MADSci environment** (Python 3.12): Laboratory orchestration and robotics

| Component | Version |
|-----------|---------|
| Python | 3.12 |
| MADSci | 0.6.0 |
| Opentrons | 8.5.1 |

### Automated Setup

```bash
./setup-isaacsim.sh  # Creates Isaac Sim virtual environment
./setup-madsci.sh    # Creates MADSci virtual environment + applies Opentrons patches
```

The MADSci setup script applies patches to the Opentrons package (in `forks/`) that redirect hardware control commands to the Isaac Sim simulation via ZMQ.

### Activate Environments

```bash
source activate-isaacsim.sh  # For Isaac Sim work
source activate-madsci.sh    # For MADSci work
```

## Running the PRISM Project

The PRISM project (`projects/prism/`) implements an automated PCR workflow with 6 laboratory instruments: an OT-2 liquid handler, a PF400 plate transfer robot, a sealer, a thermocycler, a peeler, and a Hidex plate reader.

### Manual Execution

From the repository root:

```bash
bash projects/prism/run.sh
```

This script:
1. Converts the old WEI-format workflow YAML to MADSci format using `tools/wei_2_yaml.py`
2. Launches Isaac Sim with the laboratory simulation
3. Starts the REST Gateway (consolidated robot node API)
4. Starts MADSci services (Docker containers for orchestration)
5. Submits the workflow and monitors execution

All output is logged to `/tmp/simlab/<timestamp>/`. The run summary shows per-step results and log file paths.

### Automated Protocol Generation with Claude Code

The PRISM project uses [Claude Code](https://docs.anthropic.com/en/docs/claude-code) to autonomously generate OT-2 protocol files and workflow YAML files from a high-level experiment description, then iteratively test and refine them in the simulation.

The prompt is split into two parts:
- **`projects/prism/prompt_base.md`**: Format specifications, module definitions, constraints, and instructions (static across experiments)
- **`projects/prism/prompt_workflow.md`**: The high-level workflow description for a specific experiment (varies per experiment)

The `run_agent.sh` script combines these and launches Claude Code:

```bash
./run_agent.sh projects/prism/prompt_workflow.md
```

To use a different workflow description, create a new file with a `# Workflow` section describing the experiment steps, then pass it to the script:

```bash
./run_agent.sh path/to/my_experiment.md
```

Claude Code will:
1. Read the combined prompt (base specifications + workflow description)
2. Generate OT-2 Python protocol files and a WEI-format workflow YAML
3. Run `bash projects/prism/run.sh` to test in the simulation
4. Inspect error logs if the workflow fails
5. Revise the generated files and re-run until all steps succeed

The base prompt contains the complete YAML workflow format specification, OT-2 protocol format specification, module/location definitions, and constraints (e.g., plate orientation requirements, lid open/close ordering).

## Architecture

### Core Components

- **`slcore/`**: Python package with simulation integration code
  - `common/`: Shared utilities and parallel environment setup
  - `gateway/`: REST Gateway consolidating robot nodes into a single FastAPI process
  - `robots/`: Per-robot ZMQ servers (Isaac Sim side) and REST nodes (MADSci side)
- **`assets/`**: 3D simulation assets (robot models, labware, scenes)
- **`tools/`**: Orchestration script and workflow format converter
- **`forks/`**: Patches for third-party libraries (Opentrons ZMQ simulation backend)

### Communication

```
MADSci Workcell Manager
    |
    | HTTP POST /env_0/pf400/action/transfer
    v
REST Gateway (port 8000) --> ZMQ DEALER --> Isaac Sim ZMQ ROUTER (port 5555)
```

The system uses a ZMQ ROUTER-DEALER pattern. Isaac Sim runs a single ROUTER server; each robot node connects as a DEALER client with identity-based routing (e.g., `env_0.pf400`, `env_0.thermocycler`). The REST Gateway translates MADSci HTTP requests into ZMQ commands.

### Instruments

| Instrument | Type | Orientation | Actions |
|-----------|------|-------------|---------|
| OT-2 | Liquid handler | wide | `run_protocol` |
| PF400 | Plate transfer robot | -- | `transfer` |
| Sealer | Plate sealer | narrow | `seal` |
| Thermocycler | PCR cycler | wide | `open`, `close`, `run_program` |
| Peeler | Seal remover | narrow | `peel` |
| Hidex | Plate reader | narrow | `open`, `close`, `run_assay` |

Plate orientation (wide/narrow) is enforced in simulation. Transfers between instruments with different orientations must route through the exchange deck, which rotates the plate 90 degrees.

## Project Structure

```
ProtocolGenerator/Code/
+-- .venv-isaacsim/          # Isaac Sim environment (created by setup-isaacsim.sh)
+-- .venv-madsci/            # MADSci environment (created by setup-madsci.sh)
+-- slcore/                  # Simulation core library
|   +-- common/              # Shared utilities
|   +-- gateway/             # REST Gateway
|   +-- robots/              # Per-robot modules (ot2, pf400, sealer, peeler, thermocycler, hidex)
+-- assets/                  # 3D simulation assets (USD robot models, labware, scenes)
+-- run_agent.sh             # Combines prompt parts and launches Claude Code
+-- projects/
|   +-- prism/               # PCR automation project
|       +-- prompt_base.md   # Format specs, module definitions, and instructions
|       +-- prompt_workflow.md # Experiment-specific workflow description
|       +-- run.sh           # Full system launcher (converts YAML + runs simulation)
|       +-- run_sim.py       # Isaac Sim scene setup
|       +-- run_workflow.py  # MADSci workflow submission
|       +-- madsci/          # MADSci Docker services and workcell configuration
|       +-- module_map.yaml  # WEI module name to MADSci node name mapping
+-- tools/
|   +-- orchestrate.py       # Multi-process orchestrator
|   +-- wei_2_yaml.py        # WEI to MADSci workflow format converter
|   +-- run_madsci.sh        # MADSci Docker startup helper
+-- forks/                   # Patches for Opentrons ZMQ simulation backend
+-- requirements-isaacsim.in # Isaac Sim dependencies
+-- requirements-madsci.in   # MADSci dependencies
+-- setup-isaacsim.sh        # Isaac Sim environment setup
+-- setup-madsci.sh          # MADSci environment setup
```
