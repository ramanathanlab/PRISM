# YAML Workflow File Documentation

## Modules and Actions

### Module: `biopf400`
**Purpose**: Robotic transfer system (main plate handling robot)

#### Access:
This module does not have its own locations, and instead facilitates transfers between all other locations.

#### Restrictions:
- `transfer` requires that a plate is present at the source location
- `transfer` requires that the target location is available/empty
- `transfer` can only occur between locations with the same plate rotation (both narrow or both wide)
- If a transfer needs to change plate orientation (narrow to wide or wide to narrow), it must first go through the exchange station as an intermediate step

#### Actions:
- **`transfer`**: Moves plates between different locations/stations with configurable positioning
  - **Arguments**:
    - `source`: Source location identifier
    - `source_approach`: Approach path identifier for source pickup
    - `source_plate_rotation`: Plate orientation at source (`wide` or `narrow`)
    - `target`: Target location identifier
    - `target_approach`: Approach path identifier for target placement
    - `target_plate_rotation`: Plate orientation at target (`wide` or `narrow`)

### Module: `ot2bioalpha`
**Purpose**: OT-2 liquid handling robot

#### Access:
**Locations:**
- `ot2bioalpha_deck1_wide` - OT-2 robot deck position 1 (wide)

**Approach Paths:**
- `safe_path_ot2bioalpha` - Safe approach path for OT-2 robot

#### Restrictions:
- `run_protocol` can only be executed when plates and consumables are properly loaded on the deck

#### Actions:
- **`run_protocol`**: Executes a liquid handling protocol using a specified protocol file
  - **Arguments**:
    - `files`: Dictionary containing protocol files
    - `protocol`: Path to the OT-2 protocol file (e.g., `payload.ot2_protocol`)

### Module: `bio_sealer`
**Purpose**: Plate sealing station

#### Access:
**Locations:**
- `sealer_nest` - Plate sealing station nest (narrow)

**Approach Paths:**
- `safe_path_sealer` - Safe approach path for sealing station

#### Restrictions:
- `seal` can only be executed when a plate is present in the sealer nest

#### Actions:
- **`seal`**: Seals plates (typically with adhesive film or heat seal)
  - **Arguments**: None (empty args)

### Module: `bio_biometra3_96`
**Purpose**: Biometra thermocycler for PCR

#### Access:
**Locations:**
- `bio_biometra3_nest` - Biometra thermocycler nest (wide)

**Approach Paths:**
- `safe_path_biometra3` - Safe approach path for Biometra thermocycler

#### Restrictions:
- Must be `open` before a plate can be placed in or removed from the nest
- Must be `close`d before `run_program` can be executed
- `run_program` can only be executed when closed and with a plate present in the nest
- Must be `open`ed again after `run_program` completes to remove the plate

#### Actions:
- **`open`**: Opens the thermocycler lid
  - **Arguments**: None (empty args)
- **`close`**: Closes the thermocycler lid
  - **Arguments**: None (empty args)
- **`run_program`**: Executes a pre-programmed thermocycling protocol
  - **Arguments**:
    - `program_number`: Integer specifying which stored program to run (e.g., `5`)

### Module: `bio_peeler`
**Purpose**: Plate peeling/unsealing station

#### Access:
**Locations:**
- `peeler_nest` - Plate peeling station nest (narrow)

**Approach Paths:**
- `safe_path_peeler` - Safe approach path for peeling station

#### Restrictions:
- `peel` can only be executed when a sealed plate is present in the peeler nest

#### Actions:
- **`peel`**: Removes seals from plates
  - **Arguments**: None (empty args)

### Module: `hidex_geraldine`
**Purpose**: Hidex plate reader for assays/measurements

#### Access:
**Locations:**
- `hidex_geraldine_high_nest` - Hidex plate reader high nest position (narrow)

**Approach Paths:**
- `safe_path_hidex` - Safe approach path for Hidex plate reader

#### Restrictions:
- Must be `open` before a plate can be placed in or removed from the nest
- Must be `close`d before `run_assay` can be executed
- `run_assay` can only be executed when closed and with a plate present in the nest
- Must be `open`ed again after `run_assay` completes to remove the plate

#### Actions:
- **`open`**: Opens the plate reader lid
  - **Arguments**: None (empty args)
- **`close`**: Closes the plate reader lid
  - **Arguments**: None (empty args)
- **`run_assay`**: Runs a specified assay protocol
  - **Arguments**:
    - `assay_name`: String name of the assay protocol (e.g., `"PCR_Final_Results"`)

### Module: `incubator`
**Purpose**: Controlled temperature and lighting for incubation

#### Access:
**Locations:**
- `incubator_nest` - Incubator nest position (narrow)

**Approach Paths:**
- `safe_path_incubator` - Safe approach path for Incubator

#### Restrictions:
- `incubate` can only be executed when a plate is present in the incubator nest

#### Actions:
- **`incubate`**: Incubates a plate at a certain temperature
  - **Arguments**:
    - `temperature`: Integer specifying the incubation temperature in Celsius
    - `time`: Integer specifying the number of minutes to incubate for

### Exchange Station
**Purpose**: The exchange station serves as an intermediate transfer point between modules, allowing for plate orientation changes and temporary storage during multi-step workflows.

#### Access:
**Locations:**
- `exchange_deck_high_wide` - Exchange station high position (wide)
- `exchange_deck_high_narrow` - Exchange station high position (narrow)
- `exchange_deck_low_narrow` - Exchange station low position (narrow)

**Approach Paths:**
- `safe_path_exchange` - Safe approach path for exchange station

#### Restrictions:
- The exchange deck must either be a source or target location in a transfer, NEVER both
- The used exchange deck orientation must match the other location, being either both wide or both narrow
- Transfers via the exchange deck should use 2 transfers, the first having the exchange as the target, and the second having the exchange as the source

# YAML Workflow File Format Specification

This document describes the required format and structure for YAML workflow files used in automated laboratory protocols.

## Top-Level Structure

Every YAML workflow file must contain the following top-level fields followed by a `flowdef` section:

```yaml
name: [Protocol Name]
author: [Author/Organization]
info: [Description of the protocol]
version: '[Version Number]'

flowdef:
  # List of actions goes here
```

## Metadata Fields

### `name` (Required)
- **Type**: String
- **Purpose**: Human-readable name of the protocol
- **Example**: `"Test Protocol"`, `"PCR Amplification Workflow"`

### `author` (Required)
- **Type**: String  
- **Purpose**: Name of the person or organization that created the protocol
- **Example**: `"Autoprotocol"`, `"Lab Automation Team"`

### `info` (Required)
- **Type**: String
- **Purpose**: Brief description of what the protocol accomplishes
- **Example**: `"A PCR protocol written by Autoprotocol"`, `"Automated qPCR workflow for gene expression analysis"`

### `version` (Required)
- **Type**: String (quoted)
- **Purpose**: Version identifier for protocol tracking and updates
- **Example**: `'0.1'`, `'1.2.3'`, `'2024.01'`

## Flow Definition (`flowdef`)

The `flowdef` section contains an ordered list of actions that define the workflow execution sequence.

### Action Structure

Each action in the `flowdef` list must have the following structure:

```yaml
- action: [action_name]
  name: [human_readable_description]
  module: [module_identifier]
  args: [arguments_object]        # Optional
  files: [files_object]           # Optional
```

### Action Fields

#### `action` (Required)
- **Type**: String
- **Purpose**: Specifies which action to perform
- **Valid Values**: See module documentation for available actions
- **Examples**: `run_protocol`, `transfer`, `seal`, `open`, `close`, `run_program`, `peel`, `run_assay`

#### `name` (Required)
- **Type**: String
- **Purpose**: Human-readable description of what this specific action does
- **Example**: `"Run liquid protocol"`, `"Transfer the destination plate from OT-2 to exchange"`

#### `module` (Required)
- **Type**: String
- **Purpose**: Identifies which equipment module will execute the action
- **Valid Values**: `ot2bioalpha`, `biopf400`, `bio_sealer`, `bio_biometra3_96`, `bio_peeler`, `hidex_geraldine`

#### `args` (Optional)
- **Type**: Object/Dictionary
- **Purpose**: Contains arguments specific to the action being performed
- **Usage**: Required for actions that need parameters (e.g., transfer locations, program numbers)
- **Example**:
```yaml
args:
  source: ot2bioalpha_deck1_wide
  target: exchange_deck_high_wide
  source_approach: safe_path_ot2bioalpha
  target_approach: safe_path_exchange
  source_plate_rotation: wide
  target_plate_rotation: wide
```

#### `files` (Optional)
- **Type**: Object/Dictionary
- **Purpose**: Specifies file references needed for the action
- **Usage**: Used primarily with `run_protocol` actions
- **Example**:
```yaml
files:
  protocol: payload.ot2_protocol
```

## Complete Example

```yaml
name: Sample PCR Protocol
author: Laboratory Team
info: Automated PCR workflow with sealing and analysis
version: '1.0'

flowdef:

- action: run_protocol
  name: Execute liquid handling protocol
  module: ot2bioalpha
  files:
    protocol: payload.ot2_protocol

- action: transfer
  name: Move plate from OT-2 to sealer
  module: biopf400
  args:
    source: ot2bioalpha_deck1_wide
    source_approach: safe_path_ot2bioalpha
    source_plate_rotation: wide
    target: sealer_nest
    target_approach: safe_path_sealer
    target_plate_rotation: narrow

- action: seal
  name: Seal the reaction plate
  module: bio_sealer
  args: {}
```

## Important Notes

- **YAML Syntax**: Ensure proper indentation (2 spaces recommended) and valid YAML formatting
- **Action Order**: Actions execute sequentially in the order listed
- **Empty Args**: Use `args: {}` for actions that require the args field but take no parameters
- **Comments**: Use `#` for comments and section dividers to improve readability
- **String Quoting**: Quote version numbers and strings containing special characters

# Cell Painting Workflow Sequence Overview

This document describes the high-level workflow phases for a Cell Painting protocol, based on the provided YAML workflow file.

## Steps

```
1.) Transfer 30 µl of 1X Mito Staining Solution from stain reservoir well A1 to reaction plate well A1.
2.) Transfer 30 µl of 1X Mito Staining Solution from stain reservoir well A1 to reaction plate well A2.
3.) Transfer 30 µl of 1X Mito Staining Solution from stain reservoir well A1 to reaction plate well A3.
4.) Transfer 30 µl of 1X Mito Staining Solution from stain reservoir well A1 to reaction plate well A4.
5.) Transfer 30 µl of 1X Mito Staining Solution from stain reservoir well A1 to reaction plate well A5.
# Incubate for 30 minutes at 37°C in dark (manual step)
6.) Transfer 10 µl of 16% Paraformaldehyde (PFA) from fixative reservoir well A1 to reaction plate well A1.
7.) Transfer 10 µl of 16% Paraformaldehyde (PFA) from fixative reservoir well A1 to reaction plate well A2.
8.) Transfer 10 µl of 16% Paraformaldehyde (PFA) from fixative reservoir well A1 to reaction plate well A3.
9.) Transfer 10 µl of 16% Paraformaldehyde (PFA) from fixative reservoir well A1 to reaction plate well A4.
10.) Transfer 10 µl of 16% Paraformaldehyde (PFA) from fixative reservoir well A1 to reaction plate well A5.
# Incubate for 20 minutes at room temperature in dark (manual step)
11.) Transfer 70 µl of 1X HBSS from wash reservoir well A1 to reaction plate well A1.
12.) Transfer 70 µl of 1X HBSS from wash reservoir well A1 to reaction plate well A2.
13.) Transfer 70 µl of 1X HBSS from wash reservoir well A1 to reaction plate well A3.
14.) Transfer 70 µl of 1X HBSS from wash reservoir well A1 to reaction plate well A4.
15.) Transfer 70 µl of 1X HBSS from wash reservoir well A1 to reaction plate well A5.
51.) Transfer 70 µl of Waste from reaction plate well A1 to waste reservoir well A1.
52.) Transfer 70 µl of Waste from reaction plate well A2 to waste reservoir well A1.
53.) Transfer 70 µl of Waste from reaction plate well A3 to waste reservoir well A1.
54.) Transfer 70 µl of Waste from reaction plate well A4 to waste reservoir well A1.
55.) Transfer 70 µl of Waste from reaction plate well A5 to waste reservoir well A1.
16.) Transfer 30 µl of 0.1% Triton X-100 in HBSS from permeabilization reservoir well A1 to reaction plate well A1.
17.) Transfer 30 µl of 0.1% Triton X-100 in HBSS from permeabilization reservoir well A1 to reaction plate well A2.
18.) Transfer 30 µl of 0.1% Triton X-100 in HBSS from permeabilization reservoir well A1 to reaction plate well A3.
19.) Transfer 30 µl of 0.1% Triton X-100 in HBSS from permeabilization reservoir well A1 to reaction plate well A4.
20.) Transfer 30 µl of 0.1% Triton X-100 in HBSS from permeabilization reservoir well A1 to reaction plate well A5.
# Incubate for 15 minutes at room temperature in dark (manual step)
21.) Transfer 70 µl of 1X HBSS from wash reservoir well A2 to reaction plate well A1.
22.) Transfer 70 µl of 1X HBSS from wash reservoir well A2 to reaction plate well A2.
23.) Transfer 70 µl of 1X HBSS from wash reservoir well A2 to reaction plate well A3.
24.) Transfer 70 µl of 1X HBSS from wash reservoir well A2 to reaction plate well A4.
25.) Transfer 70 µl of 1X HBSS from wash reservoir well A2 to reaction plate well A5.
26.) Transfer 70 µl of 1X HBSS from wash reservoir well A2 to reaction plate well A1.
27.) Transfer 70 µl of 1X HBSS from wash reservoir well A2 to reaction plate well A2.
28.) Transfer 70 µl of 1X HBSS from wash reservoir well A2 to reaction plate well A3.
29.) Transfer 70 µl of 1X HBSS from wash reservoir well A2 to reaction plate well A4.
30.) Transfer 70 µl of 1X HBSS from wash reservoir well A2 to reaction plate well A5.
56.) Transfer 70 µl of Waste from reaction plate well A1 to waste reservoir well A1.
57.) Transfer 70 µl of Waste from reaction plate well A2 to waste reservoir well A1.
58.) Transfer 70 µl of Waste from reaction plate well A3 to waste reservoir well A1.
59.) Transfer 70 µl of Waste from reaction plate well A4 to waste reservoir well A1.
60.) Transfer 70 µl of Waste from reaction plate well A5 to waste reservoir well A1.
31.) Transfer 30 µl of Cell Painting Cocktail (Stain 2) from stain reservoir well A2 to reaction plate well A1.
32.) Transfer 30 µl of Cell Painting Cocktail (Stain 2) from stain reservoir well A2 to reaction plate well A2.
33.) Transfer 30 µl of Cell Painting Cocktail (Stain 2) from stain reservoir well A2 to reaction plate well A3.
34.) Transfer 30 µl of Cell Painting Cocktail (Stain 2) from stain reservoir well A2 to reaction plate well A4.
35.) Transfer 30 µl of Cell Painting Cocktail (Stain 2) from stain reservoir well A2 to reaction plate well A5.
# Incubate for 30 minutes at room temperature in dark (manual step)
36.) Transfer 70 µl of 1X HBSS from wash reservoir well A3 to reaction plate well A1.
37.) Transfer 70 µl of 1X HBSS from wash reservoir well A3 to reaction plate well A2.
38.) Transfer 70 µl of 1X HBSS from wash reservoir well A3 to reaction plate well A3.
39.) Transfer 70 µl of 1X HBSS from wash reservoir well A3 to reaction plate well A4.
40.) Transfer 70 µl of 1X HBSS from wash reservoir well A3 to reaction plate well A5.
41.) Transfer 70 µl of 1X HBSS from wash reservoir well A3 to reaction plate well A1.
42.) Transfer 70 µl of 1X HBSS from wash reservoir well A3 to reaction plate well A2.
43.) Transfer 70 µl of 1X HBSS from wash reservoir well A3 to reaction plate well A3.
44.) Transfer 70 µl of 1X HBSS from wash reservoir well A3 to reaction plate well A4.
45.) Transfer 70 µl of 1X HBSS from wash reservoir well A3 to reaction plate well A5.
46.) Transfer 70 µl of 1X HBSS from wash reservoir well A3 to reaction plate well A1.
47.) Transfer 70 µl of 1X HBSS from wash reservoir well A3 to reaction plate well A2.
48.) Transfer 70 µl of 1X HBSS from wash reservoir well A3 to reaction plate well A3.
49.) Transfer 70 µl of 1X HBSS from wash reservoir well A3 to reaction plate well A4.
50.) Transfer 70 µl of 1X HBSS from wash reservoir well A3 to reaction plate well A5.
# Do not aspirate after final wash — leave 70 µl in each well
# Seal reaction plate and store at 4°C in dark until imaging (manual step)
51.) Transfer 70 µl of Waste from reaction plate well A1 to waste reservoir well A1.
52.) Transfer 70 µl of Waste from reaction plate well A2 to waste reservoir well A1.
53.) Transfer 70 µl of Waste from reaction plate well A3 to waste reservoir well A1.
54.) Transfer 70 µl of Waste from reaction plate well A4 to waste reservoir well A1.
55.) Transfer 70 µl of Waste from reaction plate well A5 to waste reservoir well A1.
56.) Transfer 70 µl of Waste from reaction plate well A1 to waste reservoir well A1.
57.) Transfer 70 µl of Waste from reaction plate well A2 to waste reservoir well A1.
58.) Transfer 70 µl of Waste from reaction plate well A3 to waste reservoir well A1.
59.) Transfer 70 µl of Waste from reaction plate well A4 to waste reservoir well A1.
60.) Transfer 70 µl of Waste from reaction plate well A5 to waste reservoir well A1.
61.) Transfer 70 µl of Waste from reaction plate well A1 to waste reservoir well A1.
62.) Transfer 70 µl of Waste from reaction plate well A2 to waste reservoir well A1.
63.) Transfer 70 µl of Waste from reaction plate well A3 to waste reservoir well A1.
64.) Transfer 70 µl of Waste from reaction plate well A4 to waste reservoir well A1.
65.) Transfer 70 µl of Waste from reaction plate well A5 to waste reservoir well A1.
```

You are Autoprotocol, an automated protocol designer for scientific workflows. Using the provided reference material, create a yaml file for the Cell Painting workflow.
Each consecutive group of liquid transfers should be modeled as a single execution of a liquid handling protocol on the OT-2 robot, with a unique file protocol name for each. Come up with a unique and descriptive name for each OT-2 protocol files, but do not write the OT-2 protocol files.
All steps, including any marked as manual, should be handled in the yaml file.