# Run from the ProtocolGenerator/Code/ directory
# Converts the WEI-format workflow YAML to MADSci format, then runs the full system.

# Step 1: Find the WEI-format YAML (any .yaml that isn't workflow.yaml, module_map.yaml, or *_backup*)
WEI_YAML=$(find projects/prism -maxdepth 1 -name "*.yaml" \
    ! -name "workflow.yaml" \
    ! -name "module_map.yaml" \
    ! -name "*_backup*" \
    -print -quit)

if [ -z "$WEI_YAML" ]; then
    echo "Error: No WEI-format YAML file found in projects/prism/"
    exit 1
fi

echo "Converting $WEI_YAML to MADSci format..."
python tools/wei_2_yaml.py -q --module-map projects/prism/module_map.yaml "$WEI_YAML" projects/prism/workflow.yaml

if [ $? -ne 0 ]; then
    echo "Error: Failed to convert workflow YAML"
    exit 1
fi

echo "Converted workflow saved to projects/prism/workflow.yaml"

# Step 2: Run the full system
python tools/orchestrate.py \
    --isaac-cmd "source activate-isaacsim.sh && cd projects/prism && python run_sim.py" \
    --gateway-cmd "source activate-madsci.sh && python -m slcore.gateway.rest_gateway --num-envs 1 --robot-types ot2,pf400,sealer,peeler,thermocycler,hidex" \
    --madsci-cmd "./tools/run_madsci.sh projects/prism" \
    --workflow-cmd "source activate-madsci.sh && cd projects/prism && python run_workflow.py workflow.yaml" \
    --timeout 600
