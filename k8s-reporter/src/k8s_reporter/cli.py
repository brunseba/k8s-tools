"""
CLI interface for k8s-reporter.

This module provides command-line interface for launching the Streamlit app.
"""

import argparse
import sys
import subprocess
from pathlib import Path


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="K8s Reporter - Web UI for analyzing Kubernetes cluster data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  k8s-reporter                        # Launch web UI
  k8s-reporter --port 8501            # Launch on custom port
  k8s-reporter --database cluster.db  # Launch with pre-loaded database
        """
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8501,
        help="Port to run the Streamlit app (default: 8501)"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="localhost",
        help="Host to bind the Streamlit app (default: localhost)"
    )
    
    parser.add_argument(
        "--database",
        type=str,
        help="Path to SQLite database file to load automatically"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode (no browser auto-open)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    args = parser.parse_args()
    
    # Validate database path if provided
    if args.database:
        db_path = Path(args.database)
        if not db_path.exists():
            print(f"Error: Database file not found: {args.database}")
            sys.exit(1)
        
        # Set environment variable for the app to pick up
        import os
        os.environ["K8S_REPORTER_DATABASE"] = str(db_path.absolute())
    
    # Get the path to the app.py file
    app_path = Path(__file__).parent / "app.py"
    
    # Build Streamlit command
    cmd = [
        "streamlit", "run", str(app_path),
        "--server.port", str(args.port),
        "--server.address", args.host,
        "--server.headless", str(args.headless).lower(),
        "--theme.base", "light",
        "--theme.primaryColor", "#1f77b4",
        "--theme.backgroundColor", "#ffffff",
        "--theme.secondaryBackgroundColor", "#f0f2f6",
    ]
    
    if not args.headless:
        cmd.extend(["--server.runOnSave", "true"])
    
    if args.debug:
        cmd.extend(["--logger.level", "debug"])
    
    print("🚀 Starting K8s Reporter...")
    print(f"📊 Web UI will be available at: http://{args.host}:{args.port}")
    if args.database:
        print(f"🗄️  Pre-loading database: {args.database}")
    print()
    
    try:
        # Launch Streamlit
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error launching Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down K8s Reporter...")
        sys.exit(0)


if __name__ == "__main__":
    main()
