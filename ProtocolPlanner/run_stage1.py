#!/usr/bin/env python3
"""
PRISM Stage 1: Automated Protocol Planning Pipeline

Automates the multi-agent and single-agent protocol planning pipeline
for the PRISM framework. Chains LLM API calls to produce structured
liquid-handling steps from experimental protocols.

Usage:
    # Multi-agent PCR constrained with GPT-5
    python run_pipeline.py --experiment pcr --paradigm constrained --model gpt-5

    # Multi-agent PCR open-ended with Claude Opus
    python run_pipeline.py --experiment pcr --paradigm open-ended --model claude-opus

    # Multi-agent Cell Painting with Gemini Pro
    python run_pipeline.py --experiment cellpainting --paradigm multi_agent --model gemini-pro

    # Single-agent PCR with fixed constraints
    python run_pipeline.py --experiment pcr --paradigm fixed --model gpt-5 --mode single-agent
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Load .env file if present (for API keys)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass  # dotenv not installed; rely on environment variables

# ---------------------------------------------------------------------------
# Prompt directory configurations
# Keys: (experiment, paradigm, mode) -> config dict
# ---------------------------------------------------------------------------
PROMPT_CONFIGS = {
    # ---- PCR Multi-Agent ----
    ("pcr", "constrained", "multi-agent"): {
        "path": "Prompts/PCR/Multi-agent-constrained",
        "agents": ["websurfer", "planner", "critique", "validator"],
        "files": {
            "websurfer": "websurfer_prompt.txt",
            "planner": "protocol_planner_prompt.txt",
            "critique": "Critique_prompt.txt",
            "validator": "Validator_prompt.txt",
        },
        "combined_critique_validator": False,
    },
    ("pcr", "constrained-detailed", "multi-agent"): {
        "path": "Prompts/PCR/multi-agent-constrained-detailed",
        "agents": ["websurfer", "planner", "critique", "validator"],
        "files": {
            "websurfer": "websurfer_prompt.txt",
            "planner": "Robotic_setup_prompt.txt",
            "critique": "Critique_prompt.txt",
            "validator": "Validator_prompt.txt",
        },
        "combined_critique_validator": False,
    },
    ("pcr", "open-ended", "multi-agent"): {
        "path": "Prompts/PCR/Multi-agent-open-ended",
        "agents": ["websurfer", "planner", "critique_validator"],
        "files": {
            "websurfer": "PRISM_WebSurfer_Prompt.txt",
            "planner": "PRISM_Protocol_Planner_Prompt.txt",
            "critique_validator": "PRISM_Critique_Validator_Prompt_v2.txt",
        },
        "combined_critique_validator": True,
    },
    # ---- Cell Painting Multi-Agent ----
    ("cellpainting", "multi_agent", "multi-agent"): {
        "path": "Prompts/CellPainting/multi_agent",
        "agents": ["websurfer", "planner", "critique", "validator"],
        "files": {
            "websurfer": "Websurfer_prompt_updated.txt",
            "planner": "Robotic_setup_prompt_cellpainting.txt",
            "critique": "Critique_prompt_cellpainting.txt",
            "validator": "Validator_prompt_cellpainting.txt",
        },
        "combined_critique_validator": False,
    },
    # ---- PCR Single-Agent ----
    ("pcr", "fixed", "single-agent"): {
        "path": "Prompts/PCR/single_agent",
        "agents": ["single"],
        "files": {"single": "prompt_fixed.txt"},
    },
    ("pcr", "not-set", "single-agent"): {
        "path": "Prompts/PCR/single_agent",
        "agents": ["single"],
        "files": {"single": "prompt_not_set.txt"},
    },
    ("pcr", "open-ended", "single-agent"): {
        "path": "Prompts/PCR/single_agent",
        "agents": ["single"],
        "files": {"single": "open_ended.txt"},
    },
    # ---- Cell Painting Single-Agent ----
    ("cellpainting", "single", "single-agent"): {
        "path": "Prompts/CellPainting/single_agent",
        "agents": ["single"],
        "files": {"single": "prompt.txt"},
    },
}

# ---------------------------------------------------------------------------
# Model name -> provider + model ID
# ---------------------------------------------------------------------------
MODEL_MAP = {
    # OpenAI
    "gpt-5": {"provider": "openai", "model_id": "gpt-5"},
    "gpt-4o": {"provider": "openai", "model_id": "gpt-4o"},
    # Anthropic
    "claude-opus": {"provider": "anthropic", "model_id": "claude-opus-4-6"},
    "claude-sonnet": {"provider": "anthropic", "model_id": "claude-sonnet-4-6"},
    # Google
    "gemini-pro": {"provider": "google", "model_id": "gemini-2.5-pro"},
    "gemini-flash": {"provider": "google", "model_id": "gemini-2.5-flash"},
    "gemini-flash-lite": {"provider": "google", "model_id": "gemini-2.5-flash-lite"},
}


class LLMClient:
    """Unified LLM client supporting OpenAI, Anthropic, and Google APIs."""

    def __init__(self, provider: str, model_id: str):
        self.provider = provider
        self.model_id = model_id
        self._client = None
        self._init_client()

    def _init_client(self):
        if self.provider == "openai":
            from openai import OpenAI

            self._client = OpenAI()
        elif self.provider == "anthropic":
            import anthropic

            self._client = anthropic.Anthropic()
        elif self.provider == "google":
            import google.generativeai as genai

            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("GOOGLE_API_KEY environment variable not set")
            genai.configure(api_key=api_key)
            self._client = genai
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def generate(self, system_prompt: str, user_message: str, temperature: float = 0.7) -> str:
        """Generate a response from the LLM."""
        if self.provider == "openai":
            response = self._client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=temperature,
                max_tokens=8192,
            )
            return response.choices[0].message.content

        elif self.provider == "anthropic":
            response = self._client.messages.create(
                model=self.model_id,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
                temperature=temperature,
                max_tokens=8192,
            )
            return response.content[0].text

        elif self.provider == "google":
            model = self._client.GenerativeModel(
                self.model_id,
                system_instruction=system_prompt,
            )
            response = model.generate_content(
                user_message,
                generation_config=self._client.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=8192,
                ),
            )
            return response.text


def load_prompt(base_dir: Path, filename: str) -> str:
    """Load a prompt file from disk."""
    filepath = base_dir / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Prompt file not found: {filepath}")
    return filepath.read_text().strip()


def run_single_agent(client: LLMClient, prompt: str, output_dir: Path, temperature: float) -> str:
    """Run single-agent mode: one LLM call with the combined prompt."""
    print("\n--- Single Agent ---")
    print("  Generating protocol...")
    t0 = time.time()

    response = client.generate(
        system_prompt=prompt,
        user_message="Generate the complete protocol following all instructions above.",
        temperature=temperature,
    )

    elapsed = time.time() - t0
    (output_dir / "single_agent_output.txt").write_text(response)
    print(f"  Done ({elapsed:.1f}s, {len(response)} chars)")
    return response


def run_multi_agent(
    client: LLMClient,
    prompts: dict,
    config: dict,
    output_dir: Path,
    max_iterations: int = 3,
    temperature: float = 0.7,
) -> str:
    """Run multi-agent pipeline with iterative Critique/Validator refinement."""
    outputs = {}

    # --- Agent 1: WebSurfer ---
    print("\n--- Agent 1: WebSurfer ---")
    print("  Retrieving protocol information...")
    t0 = time.time()

    websurfer_output = client.generate(
        system_prompt=prompts["websurfer"],
        user_message=(
            "Please retrieve the protocol and extract all required information "
            "as specified in your instructions."
        ),
        temperature=temperature,
    )
    outputs["websurfer"] = websurfer_output
    (output_dir / "01_websurfer_output.txt").write_text(websurfer_output)
    print(f"  Done ({time.time() - t0:.1f}s, {len(websurfer_output)} chars)")

    # --- Agent 2: Protocol Planner ---
    print("\n--- Agent 2: Protocol Planner ---")
    print("  Generating structured protocol...")
    t0 = time.time()

    planner_output = client.generate(
        system_prompt=prompts["planner"],
        user_message=(
            "Here is the information gathered by the WebSurfer agent:\n\n"
            f"{websurfer_output}"
        ),
        temperature=temperature,
    )
    outputs["planner"] = planner_output
    (output_dir / "02_planner_output.txt").write_text(planner_output)
    print(f"  Done ({time.time() - t0:.1f}s, {len(planner_output)} chars)")

    # --- Agents 3-4: Critique + Validator ---
    if config.get("combined_critique_validator"):
        # Open-ended paradigm: combined Critique+Validator in a single agent
        print("\n--- Agent 3: Critique + Validator (Combined) ---")
        print("  Reviewing and validating protocol...")
        t0 = time.time()

        cv_output = client.generate(
            system_prompt=prompts["critique_validator"],
            user_message=(
                "Here is the WebSurfer report (CONSTANTS - source-of-truth):\n\n"
                f"{websurfer_output}\n\n"
                "---\n\n"
                "Here is the Protocol Planner's output to review and validate:\n\n"
                f"{planner_output}"
            ),
            temperature=temperature,
        )
        outputs["critique_validator"] = cv_output
        (output_dir / "03_critique_validator_output.txt").write_text(cv_output)
        print(f"  Done ({time.time() - t0:.1f}s, {len(cv_output)} chars)")
        return cv_output

    # Separate Critique and Validator with iterative refinement
    current_protocol = planner_output
    final_output = None

    for iteration in range(1, max_iterations + 1):
        # --- Critique ---
        print(f"\n--- Agent 3: Critique (iteration {iteration}/{max_iterations}) ---")
        print("  Reviewing protocol for errors...")
        t0 = time.time()

        if iteration == 1:
            critique_user_msg = (
                "Review the following protocol:\n\n"
                f"{current_protocol}"
            )
        else:
            critique_user_msg = (
                "The Validator returned the following feedback on the "
                "previous iteration:\n\n"
                f"{validator_output}\n\n"
                "---\n\n"
                "Original protocol to re-critique:\n\n"
                f"{current_protocol}"
            )

        critique_output = client.generate(
            system_prompt=prompts["critique"],
            user_message=critique_user_msg,
            temperature=temperature,
        )
        outputs[f"critique_iter{iteration}"] = critique_output
        (output_dir / f"03_critique_iter{iteration}.txt").write_text(critique_output)
        print(f"  Done ({time.time() - t0:.1f}s, {len(critique_output)} chars)")

        if "no issues found" in critique_output.lower():
            print("  No issues found by Critique.")

        # --- Validator ---
        print(f"\n--- Agent 4: Validator (iteration {iteration}/{max_iterations}) ---")
        print("  Validating corrected protocol...")
        t0 = time.time()

        validator_output = client.generate(
            system_prompt=prompts["validator"],
            user_message=(
                "Original protocol from Protocol Planner:\n\n"
                f"{current_protocol}\n\n"
                "---\n\n"
                "Critique agent feedback:\n\n"
                f"{critique_output}\n\n"
                "---\n\n"
                "Please apply the corrections and return the final validated protocol."
            ),
            temperature=temperature,
        )
        outputs[f"validator_iter{iteration}"] = validator_output
        (output_dir / f"04_validator_iter{iteration}.txt").write_text(validator_output)
        print(f"  Done ({time.time() - t0:.1f}s, {len(validator_output)} chars)")
        final_output = validator_output

        # Check whether the Validator accepted or rejected the protocol
        if "rejected" not in validator_output.lower():
            print(f"  Protocol validated after {iteration} iteration(s).")
            return final_output
        else:
            print("  Protocol rejected, iterating...")

    print(f"\n  Max iterations ({max_iterations}) reached. Returning last output.")
    return final_output


def list_configurations():
    """Print all available (experiment, paradigm, mode) combinations."""
    print("\nAvailable configurations:")
    print(f"  {'Experiment':<15} {'Paradigm':<25} {'Mode':<15} Agents")
    print("  " + "-" * 70)
    for (exp, par, mode), cfg in sorted(PROMPT_CONFIGS.items()):
        agents = ", ".join(cfg["agents"])
        print(f"  {exp:<15} {par:<25} {mode:<15} {agents}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="PRISM Stage 1: Automated Protocol Planning Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--experiment",
        choices=["pcr", "cellpainting"],
        help="Experiment type",
    )
    parser.add_argument(
        "--paradigm",
        help="Prompting paradigm (e.g. constrained, open-ended, fixed)",
    )
    parser.add_argument(
        "--model",
        choices=list(MODEL_MAP.keys()),
        help="LLM model to use",
    )
    parser.add_argument(
        "--model-id",
        help="Override the model ID (e.g. gpt-4o-2024-08-06). "
             "If set, --model is only used for provider selection.",
    )
    parser.add_argument(
        "--mode",
        default="multi-agent",
        choices=["multi-agent", "single-agent"],
        help="Pipeline mode (default: multi-agent)",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="Max Critique/Validator iterations (default: 3)",
    )
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="LLM sampling temperature (default: 0.7)",
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory (default: auto-generated under outputs/)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available configurations and exit",
    )
    args = parser.parse_args()

    if args.list:
        list_configurations()
        print("Available models:")
        for name, info in MODEL_MAP.items():
            print(f"  {name:<20} {info['provider']:<12} {info['model_id']}")
        return

    # Validate required args
    if not all([args.experiment, args.paradigm, args.model]):
        parser.error("--experiment, --paradigm, and --model are required (use --list to see options)")

    # Resolve configuration
    config_key = (args.experiment, args.paradigm, args.mode)
    if config_key not in PROMPT_CONFIGS:
        print(f"Error: Invalid combination: {config_key}")
        list_configurations()
        sys.exit(1)

    config = PROMPT_CONFIGS[config_key]
    model_info = MODEL_MAP[args.model]

    # Allow model ID override
    model_id = args.model_id if args.model_id else model_info["model_id"]

    # Set up output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = (
            Path(__file__).parent
            / "outputs"
            / f"{args.experiment}_{args.paradigm}_{args.model}_{timestamp}"
        )
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save run config
    run_config = {
        "experiment": args.experiment,
        "paradigm": args.paradigm,
        "model": args.model,
        "model_id": model_id,
        "provider": model_info["provider"],
        "mode": args.mode,
        "max_iterations": args.max_iterations,
        "temperature": args.temperature,
        "timestamp": datetime.now().isoformat(),
    }
    (output_dir / "run_config.json").write_text(json.dumps(run_config, indent=2))

    print("=" * 60)
    print("PRISM Stage 1: Protocol Planning Pipeline")
    print("=" * 60)
    print(f"  Experiment:  {args.experiment}")
    print(f"  Paradigm:    {args.paradigm}")
    print(f"  Mode:        {args.mode}")
    print(f"  Model:       {args.model} ({model_id})")
    print(f"  Provider:    {model_info['provider']}")
    print(f"  Temperature: {args.temperature}")
    print(f"  Max iter:    {args.max_iterations}")
    print(f"  Output:      {output_dir}")
    print("=" * 60)

    # Load prompts
    base_dir = Path(__file__).parent / config["path"]
    prompts = {}
    for agent_name, filename in config["files"].items():
        prompts[agent_name] = load_prompt(base_dir, filename)
        print(f"  Loaded: {agent_name} <- {filename}")

    # Initialize LLM client
    client = LLMClient(provider=model_info["provider"], model_id=model_id)

    # Run pipeline
    t_start = time.time()
    if args.mode == "single-agent":
        final_output = run_single_agent(client, prompts["single"], output_dir, args.temperature)
    else:
        final_output = run_multi_agent(
            client, prompts, config, output_dir, args.max_iterations, args.temperature
        )
    total_time = time.time() - t_start

    # Save final output
    final_path = output_dir / "final_protocol.txt"
    final_path.write_text(final_output)

    print("\n" + "=" * 60)
    print(f"Pipeline complete in {total_time:.1f}s")
    print(f"  Final protocol: {final_path}")
    print(f"  All outputs:    {output_dir}/")
    print("=" * 60)


if __name__ == "__main__":
    main()
