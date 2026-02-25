import sys
import subprocess
import os


# Get the absolute path of the directory containing my_agent.py
project_root = os.path.dirname(os.path.abspath(__file__))


def _setup_pythonpath_env():
    """
    Prepares the environment variables, adding the project root to PYTHONPATH.
    Returns the modified environment dictionary.
    """
    env = os.environ.copy()
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = project_root + os.pathsep + env["PYTHONPATH"]
    else:
        env["PYTHONPATH"] = project_root
    return env


def run_web(env):
    print("Starting Web UI...")
    # Get the absolute path to src/web_ui.py
    web_ui_path = os.path.join(project_root, "src", "web_ui.py")
    subprocess.run([sys.executable, "-m", "streamlit",
                   "run", web_ui_path], env=env)


def run_telegram(env):
    print("Starting Telegram Bot...")
    # Get the absolute path to src/telegram_bot.py
    telegram_bot_path = os.path.join(project_root, "src", "telegram_bot.py")
    subprocess.run([sys.executable, telegram_bot_path], env=env)


def main():
    # Set up the environment for subprocesses
    subprocess_env = _setup_pythonpath_env()

    if len(sys.argv) < 3:
        print("Usage: python my_agent.py run [web|telegram]")
        return

    command = sys.argv[1]
    target = sys.argv[2]

    if command == "run":
        if target == "web":
            run_web(subprocess_env)
        elif target == "telegram":
            run_telegram(subprocess_env)
        else:
            print(f"Unknown target: {target}")
            print("Supported targets: web, telegram")
    else:
        print(f"Unknown command: {command}")
        print("Usage: python my_agent.py run [web|telegram]")


if __name__ == "__main__":
    main()
