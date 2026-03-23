requirements = {"robotType": "OT-2"}
from opentrons import protocol_api

metadata = {
    "protocolName": "PCR Master Mix and Sample Preparation",
    "author": "PRISM",
    "description": "Prepares qPCR reactions by combining master mix, water, primers, and template DNA",
    "apiLevel": "2.12",
    "info": "A PCR master mix and sample preparation protocol written by PRISM",
    "name": "PCR Master Mix and Sample Preparation",
    "version": "1.0",
}


def run(protocol: protocol_api.ProtocolContext):
    deck = {}
    pipettes = {}

    ################
    # load labware #
    ################

    # dest_plate - destination plate at deck position 1
    deck["1"] = protocol.load_labware("nest_96_wellplate_100ul_pcr_full_skirt", "1")
    deck["1"].set_offset(x=0.9, y=-0.5, z=0.6)

    # react_plate - reagent plate at deck position 3
    deck["3"] = protocol.load_labware("nest_96_wellplate_100ul_pcr_full_skirt", "3")
    deck["3"].set_offset(x=1.0, y=1.4, z=5.7)

    # Tip racks
    deck["7"] = protocol.load_labware("opentrons_96_tiprack_20ul", "7")
    deck["7"].set_offset(x=0.2, y=1.6, z=-0.8)
    deck["8"] = protocol.load_labware("opentrons_96_tiprack_20ul", "8")
    deck["8"].set_offset(x=0.2, y=1.6, z=-0.8)

    # Pipette
    pipettes["left"] = protocol.load_instrument(
        "p20_single_gen2",
        "left",
        tip_racks=[deck["7"], deck["8"]],
    )

    ####################
    # execute commands #
    ####################

    # Step 1: Transfer 20 uL qPCR Master Mix from react_plate to dest_plate
    # A1->B2
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(20.0, deck["3"]["A1"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(20.0, deck["1"]["B2"])
    pipettes["left"].mix(3, 20, deck["1"]["B2"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # A2->B11
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(20.0, deck["3"]["A2"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(20.0, deck["1"]["B11"])
    pipettes["left"].mix(3, 20, deck["1"]["B11"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # A1->G2
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(20.0, deck["3"]["A1"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(20.0, deck["1"]["G2"])
    pipettes["left"].mix(3, 20, deck["1"]["G2"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # A2->G11
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(20.0, deck["3"]["A2"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(20.0, deck["1"]["G11"])
    pipettes["left"].mix(3, 20, deck["1"]["G11"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # Step 2: Transfer 5 uL Nuclease-free Biowater from react_plate to dest_plate
    # C1->B2
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(5.0, deck["3"]["C1"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(5.0, deck["1"]["B2"])
    pipettes["left"].mix(3, 5, deck["1"]["B2"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # C2->B11
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(5.0, deck["3"]["C2"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(5.0, deck["1"]["B11"])
    pipettes["left"].mix(3, 5, deck["1"]["B11"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # C3->G2
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(5.0, deck["3"]["C3"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(5.0, deck["1"]["G2"])
    pipettes["left"].mix(3, 5, deck["1"]["G2"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # C4->G11
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(5.0, deck["3"]["C4"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(5.0, deck["1"]["G11"])
    pipettes["left"].mix(3, 5, deck["1"]["G11"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # Step 3: Transfer 5 uL Forward Primer from react_plate D1 to dest_plate wells
    # D1->B2
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(5.0, deck["3"]["D1"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(5.0, deck["1"]["B2"])
    pipettes["left"].mix(3, 5, deck["1"]["B2"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # D1->B11
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(5.0, deck["3"]["D1"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(5.0, deck["1"]["B11"])
    pipettes["left"].mix(3, 5, deck["1"]["B11"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # D1->G2
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(5.0, deck["3"]["D1"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(5.0, deck["1"]["G2"])
    pipettes["left"].mix(3, 5, deck["1"]["G2"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # D1->G11
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(5.0, deck["3"]["D1"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(5.0, deck["1"]["G11"])
    pipettes["left"].mix(3, 5, deck["1"]["G11"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # Step 4: Transfer 5 uL Reverse Primer from react_plate E1 to dest_plate wells
    # E1->B2
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(5.0, deck["3"]["E1"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(5.0, deck["1"]["B2"])
    pipettes["left"].mix(3, 5, deck["1"]["B2"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # E1->B11
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(5.0, deck["3"]["E1"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(5.0, deck["1"]["B11"])
    pipettes["left"].mix(3, 5, deck["1"]["B11"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # E1->G2
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(5.0, deck["3"]["E1"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(5.0, deck["1"]["G2"])
    pipettes["left"].mix(3, 5, deck["1"]["G2"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # E1->G11
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(5.0, deck["3"]["E1"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(5.0, deck["1"]["G11"])
    pipettes["left"].mix(3, 5, deck["1"]["G11"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # Step 5: Transfer 5 uL Template DNA from react_plate H1 to dest_plate B2 and G2
    # H1->B2
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(5.0, deck["3"]["H1"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(5.0, deck["1"]["B2"])
    pipettes["left"].mix(3, 5, deck["1"]["B2"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # H1->G2
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(5.0, deck["3"]["H1"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(5.0, deck["1"]["G2"])
    pipettes["left"].mix(3, 5, deck["1"]["G2"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # Step 6: Transfer 5 uL Nuclease-free Biowater (NTC controls) to dest_plate B11 and G11
    # C2->B11
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(5.0, deck["3"]["C2"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(5.0, deck["1"]["B11"])
    pipettes["left"].mix(3, 5, deck["1"]["B11"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # C4->G11
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].aspirate(5.0, deck["3"]["C4"])
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].dispense(5.0, deck["1"]["G11"])
    pipettes["left"].mix(3, 5, deck["1"]["G11"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # Step 7: Final mix 10x at 20 uL in all destination wells
    # B2
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].mix(10, 20, deck["1"]["B2"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # G2
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].mix(10, 20, deck["1"]["G2"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # B11
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].mix(10, 20, deck["1"]["B11"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()

    # G11
    pipettes["left"].pick_up_tip()
    pipettes["left"].well_bottom_clearance.aspirate = 1
    pipettes["left"].well_bottom_clearance.dispense = 1
    pipettes["left"].mix(10, 20, deck["1"]["G11"])
    pipettes["left"].blow_out()
    pipettes["left"].drop_tip()
