"""Command-line interface for the echochamber package."""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional
import typer

from echochamber import __version__
from echochamber.config import load_config
from echochamber.data.download import download_snap_datasets
from echochamber.data.fixtures import generate_synthetic_data
from echochamber.logging_utils import setup_logger
from echochamber.paths import PROJECT_ROOT, resolve_path
from echochamber.pipeline.runner import run_pipeline

app = typer.Typer(
    name="echochamber",
    help="Temporal Echo Chamber Detection in Online Social Networks.",
    add_completion=False,
)
logger = setup_logger("echochamber.cli")


@app.command()
def version():
    """Print package version."""
    typer.echo(f"echochamber version {__version__}")


@app.command()
def validate(
    config: Path = typer.Option(
        Path("configs/fixture.yaml"),
        "--config",
        "-c",
        help="Path to YAML configuration file to validate.",
    ),
):
    """Validate a configuration file schema and parameter constraints."""
    resolved = resolve_path(config)
    try:
        cfg = load_config(resolved)
        typer.echo(f"Configuration at {resolved} is valid.")
        typer.echo(f"Project: {cfg.project.name} (mode: {cfg.project.mode})")
        typer.echo(f"ECI weights: iso={cfg.eci.weights.isolation:.3f}, hom={cfg.eci.weights.homogeneity:.3f}, scar={cfg.eci.weights.exposure_scarcity:.3f}")
    except Exception as e:
        typer.secho(f"Configuration error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command()
def fixture(
    output_dir: Path = typer.Option(
        Path("data/fixture"),
        "--output-dir",
        "-o",
        help="Output directory for synthetic fixture data.",
    ),
    seed: int = typer.Option(42, "--seed", "-s", help="Random seed for generation."),
    quarters: int = typer.Option(4, "--quarters", "-q", help="Number of temporal quarters to generate."),
):
    """Generate deterministic synthetic test data for offline testing."""
    resolved = resolve_path(output_dir)
    tsv_file, emb_file = generate_synthetic_data(resolved, seed=seed, num_quarters=quarters)
    typer.secho(f"Generated fixture dataset at {resolved}", fg=typer.colors.GREEN)
    typer.echo(f"  Hyperlinks: {tsv_file}")
    typer.echo(f"  Embeddings: {emb_file}")


@app.command()
def download(
    raw_dir: Path = typer.Option(
        Path("data/raw"),
        "--raw-dir",
        "-d",
        help="Target directory for downloaded raw datasets.",
    ),
    datasets: Optional[List[str]] = typer.Option(
        None,
        "--dataset",
        help="Specific datasets to download (title, body, embeddings).",
    ),
    overwrite: bool = typer.Option(False, "--overwrite", help="Overwrite existing files."),
):
    """Download Stanford SNAP Reddit hyperlink and embedding datasets."""
    resolved = resolve_path(raw_dir)
    try:
        results = download_snap_datasets(resolved, datasets=datasets, overwrite=overwrite)
        typer.secho("Download completed successfully:", fg=typer.colors.GREEN)
        for k, p in results.items():
            typer.echo(f"  {k}: {p}")
    except Exception as e:
        typer.secho(f"Download failed: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command()
def run(
    config: Path = typer.Option(
        Path("configs/fixture.yaml"),
        "--config",
        "-c",
        help="Path to YAML configuration file.",
    ),
):
    """Execute the full 10-stage temporal echo chamber pipeline."""
    resolved_cfg = resolve_path(config)
    try:
        cfg = load_config(resolved_cfg)
        result = run_pipeline(cfg, base_dir=PROJECT_ROOT)
        typer.secho(
            f"Pipeline run '{cfg.paths.run_name}' completed successfully in {result['total_time']:.2f}s!",
            fg=typer.colors.GREEN,
            bold=True,
        )
        typer.echo(f"Artifacts saved in: {result['run_dir']}")
        typer.echo(f"Run manifest: {result['manifest_file']}")
    except Exception as e:
        typer.secho(f"Execution error: {e}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)


@app.command()
def dashboard(
    port: int = typer.Option(8501, "--port", "-p", help="Port to run Streamlit on."),
):
    """Launch the interactive Streamlit research dashboard."""
    app_path = PROJECT_ROOT / "app" / "Home.py"
    if not app_path.exists():
        typer.secho(f"Dashboard entry point not found at {app_path}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    typer.echo(f"Launching Streamlit dashboard from {app_path} on port {port}...")
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", str(port)]
    subprocess.run(cmd)


if __name__ == "__main__":
    app()
