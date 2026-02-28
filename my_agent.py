import sys
import subprocess
import os
import argparse


# Get the absolute path of the directory containing my_agent.py
project_root = os.path.dirname(os.path.abspath(__file__))


def _setup_pythonpath_env(base_dir=None):
    """
    Prepares the environment variables, adding the project root to PYTHONPATH.
    Returns the modified environment dictionary.
    """
    env = os.environ.copy()
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = project_root + os.pathsep + env["PYTHONPATH"]
    else:
        env["PYTHONPATH"] = project_root
    
    if base_dir:
        env["DOCS_BASE_DIR"] = os.path.abspath(base_dir)
        
    return env


def run_web(env, port=None):
    print("Starting Web UI...")
    # Get the absolute path to src/web_ui.py
    web_ui_path = os.path.join(project_root, "src", "web_ui.py")
    cmd = [sys.executable, "-m", "streamlit", "run", web_ui_path]
    if port:
        cmd.extend(["--server.port", str(port)])
    subprocess.run(cmd, env=env)


def run_telegram(env):
    print("Starting Telegram Bot...")
    # Get the absolute path to src/telegram_bot.py
    telegram_bot_path = os.path.join(project_root, "src", "telegram_bot.py")
    subprocess.run([sys.executable, telegram_bot_path], env=env)


def main():
    parser = argparse.ArgumentParser(description="My Agent CLI")
    parser.add_argument("--run", choices=["web", "telegram"], required=True, help="Target to run")
    parser.add_argument("--dir", default="docs", help="Base directory for DocumentManager (default: docs)")
    parser.add_argument("--port", type=int, help="Port for the Streamlit server (default: use Streamlit's default)")
    
    args = parser.parse_args()

    # Set up the environment for subprocesses
    subprocess_env = _setup_pythonpath_env(args.dir)

    if args.run == "web":
        run_web(subprocess_env, args.port)
    elif args.run == "telegram":
        run_telegram(subprocess_env)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass  # Quiet exit on Ctrl+C
