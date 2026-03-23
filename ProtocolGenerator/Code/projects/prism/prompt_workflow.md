# Workflow

These are the high-level workflow steps for an automated PCR processing experiment.

The `ot2bioalpha` OT-2 is prepared with the 96-well plates `react_plate` at deck position 3 and `dest_plate` at deck position 1

1.) Transfer 20 uL of qPCR Master Mix from react_plate to dest_plate: A1→B2, A2→B11, A1→G2, A2→G11 with 3 mix cycles. [Tip action – eject]
2.) Transfer 5 uL of Nuclease-free Biowater from react_plate to dest_plate: C1→B2, C2→B11, C3→G2, C4→G11 with 3 mix cycles. [Tip action – eject]
3.) Transfer 5 uL of Forward Primer from react_plate D1 to dest_plate wells B2, B11, G2, and G11 with 3 mix cycles. [Tip action – eject]
4.) Transfer 5 uL of Reverse Primer from react_plate E1 to dest_plate wells B2, B11, G2, and G11 with 3 mix cycles. [Tip action – eject]
5.) Transfer 5 uL of Template DNA from react_plate H1 to dest_plate wells B2 and G2 with 3 mix cycles. [Tip action – eject]
6.) Transfer 5 uL of Nuclease-free Biowater from react_plate to dest_plate: C2→B11, C4→G11 with 3 mix cycles. [Tip action – eject]
7.) Mix 10X with pipette set to 20 uL in wells B2, G2, B11, and G11
8.) Seal the plate to prepare it for thermocycling
9.) Perform a thermocycling operation (program #5)
10.) Peel the plate to prepare it for reading
11.) Perform an absorbance reading using the Hidex plate reader (protocol "PCR_Final_Results")
12.) Open the Hidex plate reader lid after analysis completion