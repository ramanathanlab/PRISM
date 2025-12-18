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

### Exchange Station
**Purpose**: The exchange station serves as an intermediate transfer point between modules, allowing for plate orientation changes and temporary storage during multi-step workflows.

#### Access:
**Locations:**
- `exchange_deck_high_wide` - Exchange station high position (wide)
- `exchange_deck_high_narrow` - Exchange station high position (narrow)

**Approach Paths:**
- `safe_path_exchange` - Safe approach path for exchange station

#### Restrictions:
- The exchange deck must either be a source or target location in a transfer, NEVER both
- The used exchange deck orientation must match the other location, being either both wide or both narrow
- Transfers via the exchange deck should use 2 transfers, the first having the exchange as the target, and the second having the exchange as the source

# YAML Workflow File Format Specification

This section describes the required format and structure for YAML workflow files used in automated laboratory protocols.

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
name: Sample Protocol
author: PRISM
info: Automated workflow with sealing
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

# OT-2 Liquid Handling File Format Specification

This document describes the required format and structure for Python protocol files used with the Opentrons OT-2 liquid handling robot.

## Top-Level Structure

Every OT-2 protocol file must contain the following components:

```python
requirements = {"robotType": "OT-2"}
from opentrons import protocol_api

metadata = {
    "protocolName": "PCR",                     # Human-readable protocol name
    "author": "PRISM",                         # Protocol author/creator
    "description": "PCR",                      # Brief protocol description
    "apiLevel": "2.12",                        # Opentrons API version
    "info": "A PCR protocol written by PRISM", # Additional information
    "name": "PCR",                             # Short protocol name
    "version": "1.0"                           # Version identifier
}

def run(protocol: protocol_api.ProtocolContext):
    # Protocol implementation
```

## Protocol Function

### Module Loading
```python
module = protocol.load_module("Temperature Module", "3")
deck["3"] = module.load_labware("nest_96_wellplate_100ul_pcr_full_skirt")
deck["3"].set_offset(x=1.0, y=1.4, z=5.7)
```

### Standard Labware Loading
```python
deck["1"] = protocol.load_labware("nest_96_wellplate_100ul_pcr_full_skirt", "1")
deck["1"].set_offset(x=0.9, y=-0.5, z=0.6)
```

### Tip Rack Loading
```python
deck["7"] = protocol.load_labware("opentrons_96_tiprack_20ul", "7")
deck["7"].set_offset(x=0.2, y=1.6, z=-0.8)
```

### Pipette Loading
```python
pipettes["left"] = protocol.load_instrument(
    "p20_single_gen2",
    "left",
    tip_racks=[deck["7"]]
)
```

### Standard Transfer Pattern

The basic pattern for a single transfer operation with mixing:

```python
pipettes["left"].pick_up_tip()
pipettes["left"].well_bottom_clearance.aspirate = 1
pipettes["left"].aspirate(20.0, deck["3"]["A1"])
pipettes["left"].well_bottom_clearance.dispense = 1
pipettes["left"].dispense(20.0, deck["1"]["B2"])
pipettes["left"].mix(3, 20, deck["1"]["B2"])
pipettes["left"].blow_out()
pipettes["left"].drop_tip()
```

### Operation Breakdown

1. **`pick_up_tip()`**: Retrieves a new tip from the tip rack
2. **`well_bottom_clearance.aspirate`**: Sets height above well bottom for aspiration (in mm)
3. **`aspirate(volume, location)`**: Draws liquid from specified well
4. **`well_bottom_clearance.dispense`**: Sets height above well bottom for dispensing (in mm)
5. **`dispense(volume, location)`**: Dispenses liquid into specified well
6. **`mix(repetitions, volume, location)`**: Mixes by aspirating and dispensing repeatedly
7. **`blow_out()`**: Expels any remaining liquid from the tip
8. **`drop_tip()`**: Discards the used tip

### Mix-Only Operation

For mixing without transfer:

```python
pipettes["left"].pick_up_tip()
pipettes["left"].well_bottom_clearance.aspirate = 1
pipettes["left"].well_bottom_clearance.dispense = 1
pipettes["left"].mix(10, 20, deck["1"]["B2"])
pipettes["left"].blow_out()
pipettes["left"].drop_tip()
```

## Minimal Working Example

```python
requirements = {"robotType": "OT-2"}
from opentrons import protocol_api

metadata = {
    "protocolName": "Simple Transfer",
    "author": "PRISM",
    "description": "Basic liquid transfer example",
    "apiLevel": "2.12",
    "info": "Demonstrates minimal OT-2 protocol structure",
    "name": "Simple Transfer",
    "version": "1.0"
}

def run(protocol: protocol_api.ProtocolContext):
    deck = {}
    pipettes = {}

    ################
    # load labware #
    ################
    deck["1"] = protocol.load_labware("nest_96_wellplate_100ul_pcr_full_skirt", "1")
    deck["2"] = protocol.load_labware("nest_96_wellplate_100ul_pcr_full_skirt", "2")
    deck["7"] = protocol.load_labware("opentrons_96_tiprack_20ul", "7")
    pipettes["left"] = protocol.load_instrument("p20_single_gen2", "left", tip_racks=[deck["7"]])

    ####################
    # execute commands #
    ####################
    # Transfer 10 µL from source to destination with mixing
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(10.0, deck["2"]["A1"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(10.0, deck["1"]["A1"])
    pipettes["left"].mix(3, 10, deck["1"]["A1"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()
```

## Important Notes

- **Tip Usage**: Each transfer operation uses a fresh tip (pick_up_tip at start, drop_tip at end)
- **Well References**: Use string notation for well positions (e.g., `"A1"`, `"B2"`)
- **Comments**: Use `#` for comments and section dividers to improve readability
- **Sequential Execution**: Commands execute in the order written

# PCR Workflow Sequence Overview

These are the high-level workflow steps for an automated PCR processing experiment.

Here is the OT-2 script you should use, with a placeholder at the bottom for you to fill in liquid transfer commands.
```python
requirements = {"robotType": "OT-2"}

from opentrons import protocol_api

metadata = {
    "protocolName": "Color Mixing Protocol",
    "author": "PRISM",
    "description": "Mix colors in a 96 well plate",
    "apiLevel": "2.12"
}

def run(protocol: protocol_api.ProtocolContext):
    deck = {}
    pipettes = {}

    ################
    # load labware #
    ################

    deck["2"] = protocol.load_labware("corning_96_wellplate_360ul_flat", "2")
    deck["5"] = protocol.load_labware("nest_1_reservoir_195ml", "5")
    deck["5"].set_offset(x=0.00, y=0.00, z=1.50)
    deck["6"] = protocol.load_labware("nest_1_reservoir_195ml", "6")
    deck["6"].set_offset(x=0.00, y=0.00, z=1.50)
    deck["8"] = protocol.load_labware("nest_1_reservoir_195ml", "8")
    deck["8"].set_offset(x=0.00, y=0.00, z=1.50)
    deck["9"] = protocol.load_labware("nest_1_reservoir_195ml", "9")
    deck["9"].set_offset(x=0.00, y=0.00, z=1.50)
    deck["10"] = protocol.load_labware("opentrons_96_tiprack_300ul", "10")
    deck["11"] = protocol.load_labware("opentrons_96_tiprack_300ul", "11")
    pipettes["left"] = protocol.load_instrument("p300_single_gen2", "left", tip_racks=[deck["10"], deck["11"]])

    ####################
    # execute commands #
    ####################

    ... # Write commands here
```

Here are the liquid transfer commands that you should convert into OT-2 commands.
```
1.) Transfer 20 µL of Blue dye working solution from dye_reservoir A1 to destination_plate H1 with no mix cycles. [Tip action: eject tip]
2.) Transfer 20 µL of Blue dye working solution from dye_reservoir A1 to destination_plate G2 with no mix cycles. [Tip action: eject tip]
3.) Transfer 20 µL of Blue dye working solution from dye_reservoir A1 to destination_plate F3 with no mix cycles. [Tip action: eject tip]
4.) Transfer 20 µL of Blue dye working solution from dye_reservoir A1 to destination_plate E4 with no mix cycles. [Tip action: eject tip]
5.) Transfer 20 µL of Blue dye working solution from dye_reservoir A1 to destination_plate D5 with no mix cycles. [Tip action: eject tip]
6.) Transfer 20 µL of Blue dye working solution from dye_reservoir A1 to destination_plate C6 with no mix cycles. [Tip action: eject tip]
7.) Transfer 20 µL of Blue dye working solution from dye_reservoir A1 to destination_plate B7 with no mix cycles. [Tip action: eject tip]
8.) Transfer 20 µL of Blue dye working solution from dye_reservoir A1 to destination_plate A8 with no mix cycles. [Tip action: eject tip]
```

---

You are PRISM, an automated protocol designer for scientific workflows.
Using the provided reference material, create only the full OT-2 python file for the color mixing sequence.
