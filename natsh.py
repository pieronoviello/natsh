#!/usr/bin/env python3
"""
natsh - Natural Shell
Talk to your terminal in plain English

Supports multiple AI providers: Gemini, OpenAI, Claude
"""

VERSION = "1.2.3"

import os
import sys
import subprocess
import platform
import json
from datetime import datetime
from pathlib import Path

# Windows compatibility for readline
try:
    import readline
except ImportError:
    try:
        import pyreadline3 as readline
    except ImportError:
        readline = None

# Detect OS
IS_WINDOWS = platform.system() == "Windows"

# Paths
if IS_WINDOWS:
    HOME = Path(os.environ.get("USERPROFILE", os.path.expanduser("~")))
else:
    HOME = Path.home()

NATSH_DIR = HOME / ".natsh"
CONFIG_FILE = NATSH_DIR / "config.json"
HISTORY_FILE = NATSH_DIR / "history.json"
ENV_FILE = NATSH_DIR / ".env"

# Default configuration
DEFAULT_CONFIG = {
    "provider": "gemini",
    "model": {
        "gemini": "gemini-2.5-flash",
        "openai": "gpt-4o-mini",
        "claude": "claude-3-haiku-20240307"
    },
    "safe_mode": True,
    "max_history": 100,
    "aliases": {},
    "dangerous_commands": ["del", "rmdir", "rd", "format", "rm", "rm -rf", "shutdown", "restart"]
}

# Global state
config = {}
command_history = []
session_history = []
ai_client = None

# Ctrl+C handling is done via try/except KeyboardInterrupt in main loop

# ============== Configuration ==============

def load_config():
    """Load configuration from file"""
    global config
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                saved_config = json.load(f)
                # Deep merge for nested dicts
                config = DEFAULT_CONFIG.copy()
                for key, value in saved_config.items():
                    if key in config and isinstance(config[key], dict) and isinstance(value, dict):
                        config[key] = {**config[key], **value}
                    else:
                        config[key] = value
        except (json.JSONDecodeError, IOError):
            config = DEFAULT_CONFIG.copy()
    else:
        config = DEFAULT_CONFIG.copy()
    return config

def save_config():
    """Save configuration to file"""
    NATSH_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def load_env():
    """Load environment variables from .env file"""
    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value

def save_env_key(key: str, value: str):
    """Save or update a key in .env file"""
    NATSH_DIR.mkdir(parents=True, exist_ok=True)
    env_vars = {}

    if ENV_FILE.exists():
        with open(ENV_FILE) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k] = v

    env_vars[key] = value

    with open(ENV_FILE, "w") as f:
        for k, v in env_vars.items():
            f.write(f"{k}={v}\n")

    os.environ[key] = value

# ============== History ==============

def load_history():
    """Load command history from file"""
    global command_history
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE) as f:
                command_history = json.load(f)
                # Keep only last max_history entries
                max_hist = config.get("max_history", 100)
                command_history = command_history[-max_hist:]
        except (json.JSONDecodeError, IOError):
            command_history = []
    return command_history

def save_history():
    """Save command history to file"""
    NATSH_DIR.mkdir(parents=True, exist_ok=True)
    max_hist = config.get("max_history", 100)
    with open(HISTORY_FILE, "w") as f:
        json.dump(command_history[-max_hist:], f, indent=2)

def add_to_history(user_input: str, command: str, output: str = "", executed: bool = True):
    """Add command to history"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "input": user_input,
        "command": command,
        "output": output[:500] if output else "",
        "executed": executed,
        "cwd": os.getcwd()
    }
    command_history.append(entry)
    session_history.append(entry)
    save_history()

def show_history(count: int = 20):
    """Display command history"""
    entries = command_history[-count:]
    if not entries:
        print("\033[90mNo history yet.\033[0m")
        return

    print(f"\033[36mLast {len(entries)} commands:\033[0m\n")
    for i, entry in enumerate(entries, 1):
        ts = entry.get("timestamp", "")[:16].replace("T", " ")
        cmd = entry.get("command", "")
        executed = "+" if entry.get("executed", True) else "-"
        print(f"\033[90m{ts}\033[0m [{executed}] \033[33m{cmd}\033[0m")
    print()

def format_context_history() -> str:
    """Format recent history for AI context"""
    entries = session_history[-5:] if session_history else command_history[-5:]
    if not entries:
        return "No previous commands."

    lines = []
    for i, entry in enumerate(entries, 1):
        cmd = entry.get("command", "")
        output = entry.get("output", "")
        lines.append(f"{i}. > {cmd}")
        if output:
            output_lines = output.strip().split('\n')[:2]
            for line in output_lines:
                lines.append(f"   {line}")
    return "\n".join(lines)

# ============== AI Providers ==============

class AIProvider:
    """Base class for AI providers"""
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_command(self, prompt: str) -> str:
        raise NotImplementedError

class GeminiProvider(AIProvider):
    """Google Gemini provider"""
    def __init__(self, api_key: str):
        super().__init__(api_key)
        from google import genai
        self.client = genai.Client(api_key=api_key)
        self.model = config.get("model", {}).get("gemini", "gemini-2.5-flash")

    def get_command(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )
        return response.text.strip()

class OpenAIProvider(AIProvider):
    """OpenAI provider"""
    def __init__(self, api_key: str):
        super().__init__(api_key)
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = config.get("model", {}).get("openai", "gpt-4o-mini")

    def get_command(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()

class ClaudeProvider(AIProvider):
    """Anthropic Claude provider"""
    def __init__(self, api_key: str):
        super().__init__(api_key)
        from anthropic import Anthropic
        self.client = Anthropic(api_key=api_key)
        self.model = config.get("model", {}).get("claude", "claude-3-haiku-20240307")

    def get_command(self, prompt: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text.strip()

def get_provider_key_name(provider: str) -> str:
    """Get environment variable name for provider API key"""
    return {
        "gemini": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "claude": "ANTHROPIC_API_KEY"
    }.get(provider, "GEMINI_API_KEY")

def get_provider_url(provider: str) -> str:
    """Get URL to obtain API key"""
    return {
        "gemini": "https://aistudio.google.com/apikey",
        "openai": "https://platform.openai.com/api-keys",
        "claude": "https://console.anthropic.com/settings/keys"
    }.get(provider, "")

def init_ai_client(provider: str = None) -> AIProvider:
    """Initialize AI client for specified provider"""
    global ai_client

    if provider is None:
        provider = config.get("provider", "gemini")

    key_name = get_provider_key_name(provider)
    api_key = os.environ.get(key_name)

    if not api_key:
        return None

    try:
        if provider == "gemini":
            ai_client = GeminiProvider(api_key)
        elif provider == "openai":
            ai_client = OpenAIProvider(api_key)
        elif provider == "claude":
            ai_client = ClaudeProvider(api_key)
        else:
            ai_client = GeminiProvider(api_key)
        return ai_client
    except Exception as e:
        print(f"\033[31mError initializing {provider}: {e}\033[0m")
        return None

def setup_api_key(provider: str = None):
    """Prompt user to enter API key"""
    if provider is None:
        provider = config.get("provider", "gemini")

    key_name = get_provider_key_name(provider)
    url = get_provider_url(provider)

    print(f"\n\033[36mGet your {provider.upper()} API key at: {url}\033[0m\n")
    api_key = input(f"\033[33mEnter your {provider.upper()} API key:\033[0m ").strip()

    if not api_key:
        print("No API key provided.")
        return False

    save_env_key(key_name, api_key)
    print(f"\033[32mAPI key saved!\033[0m\n")
    return True

# ============== Command Translation ==============

def build_prompt(user_input: str, cwd: str) -> str:
    """Build prompt for AI"""
    history_context = format_context_history()

    if IS_WINDOWS:
        shell_info = "Windows CMD (cmd.exe)"
        shell_rules = """- Use Windows CMD commands (dir, del, copy, move, type, cls, start, etc.)
- Use backslashes for paths (C:\\Users\\...)
- Use 'dir' instead of 'ls'
- Use 'del' or 'rmdir /s /q' instead of 'rm -r'
- Use 'copy' instead of 'cp'
- Use 'move' instead of 'mv'
- Use 'type' instead of 'cat'
- Use 'cls' instead of 'clear'
- Use 'start' to open applications or files
- Use '%USERPROFILE%' for home directory
- For deleting folders use 'rmdir /s /q foldername'"""
    else:
        shell_info = "bash/zsh"
        shell_rules = """- Use Unix shell commands (ls, rm, cp, mv, cat, etc.)
- Use forward slashes for paths
- Use '~' for home directory
- Use 'open' on macOS or 'xdg-open' on Linux to open files"""

    return f"""You are a shell command translator. Convert the user's natural language request into a shell command for {shell_info}.

Current directory: {cwd}

Recent command history:
{history_context}

STRICT RULES:
- Output ONLY the command, nothing else
- No explanations, no markdown, no backticks, no quotes around the command
- If unclear, make a reasonable assumption
- Use the command history for context (e.g., "do that again", "undo that")
{shell_rules}

User request: {user_input}"""

def build_explain_prompt(command: str) -> str:
    """Build prompt to explain a command"""
    return f"""Explain this shell command in simple terms. Be concise (2-3 sentences max).

Command: {command}

Explain what it does and any important flags/options."""

def get_command(user_input: str, cwd: str) -> str:
    """Use AI to translate natural language to shell command"""
    if ai_client is None:
        return None

    prompt = build_prompt(user_input, cwd)
    return ai_client.get_command(prompt)

def explain_command(command: str) -> str:
    """Use AI to explain a command"""
    if ai_client is None:
        return "AI not initialized"

    prompt = build_explain_prompt(command)
    return ai_client.get_command(prompt)

# ============== Command Detection ==============

def is_natural_language(text: str) -> bool:
    """Check if input is natural language or a direct command"""
    if text.startswith(("!", "?")):
        return False

    text_lower = text.lower().strip()
    words = text_lower.split()

    # Common natural language words that indicate it's not a shell command
    natural_indicators = ["to", "the", "a", "an", "my", "all", "me", "this", "that",
                          "please", "can", "could", "would", "should", "what", "how",
                          "show", "list", "create", "make", "delete", "remove", "open",
                          "go", "navigate", "switch", "change", "find", "search", "get"]

    # If second word is a natural language indicator, it's likely natural language
    if len(words) >= 2 and words[1] in natural_indicators:
        return True

    if IS_WINDOWS:
        shell_commands = ["dir", "cls", "exit", "quit", "whoami", "date", "time",
                          "type", "copy", "move", "del", "ren", "md", "rd", "tree",
                          "find", "findstr", "sort", "more", "ver", "vol", "path",
                          "set", "echo", "pause", "title", "color", "start", "tasklist",
                          "ipconfig", "ping", "netstat", "systeminfo", "hostname"]
        shell_starters = ["cd ", "cd\\", "dir ", "echo ", "type ", "mkdir ", "md ",
                          "del ", "rmdir ", "rd ", "copy ", "move ", "ren ", "rename ",
                          "git ", "npm ", "node ", "npx ", "python ", "pip ", "curl ",
                          "code ", "start ", "set ", "docker ", "kubectl ", "aws ",
                          "powershell ", "pwsh ", "wsl ", "where ", "taskkill ",
                          ".\\", "c:\\", "d:\\", "e:\\", "%", ">", ">>", "|", "&&"]
    else:
        shell_commands = ["ls", "pwd", "clear", "exit", "quit", "whoami", "date", "cal",
                          "top", "htop", "history", "which", "man", "touch", "head", "tail",
                          "grep", "find", "sort", "wc", "diff", "tar", "zip", "unzip"]
        shell_starters = ["cd ", "ls ", "echo ", "cat ", "mkdir ", "rm ", "cp ", "mv ",
                          "git ", "npm ", "node ", "npx ", "python", "pip ", "brew ", "curl ",
                          "wget ", "chmod ", "chown ", "sudo ", "vi ", "vim ", "nano ", "code ",
                          "open ", "export ", "source ", "docker ", "kubectl ", "aws ", "gcloud ",
                          "./", "/", "~", "$", ">", ">>", "|", "&&"]

    if text_lower in [cmd.lower() for cmd in shell_commands]:
        return False
    return not any(text_lower.startswith(s.lower()) for s in shell_starters)

def is_dangerous_command(command: str) -> bool:
    """Check if command is potentially dangerous"""
    if not config.get("safe_mode", True):
        return False

    dangerous = config.get("dangerous_commands", DEFAULT_CONFIG["dangerous_commands"])
    cmd_lower = command.lower().strip()

    for d in dangerous:
        if cmd_lower.startswith(d.lower()) or f" {d.lower()}" in cmd_lower:
            return True
    return False

# ============== Help & UI ==============

def show_help():
    """Display available commands"""
    provider = config.get("provider", "gemini")
    model = config.get("model", {}).get(provider, "default")
    print(f"""
\033[1mnatsh\033[0m - Natural Shell
\033[90mProvider: {provider.upper()} | Model: {model}\033[0m

\033[36mCommands:\033[0m
  !help              Show this help
  !api [provider]    Set API key (gemini/openai/claude)
  !provider <name>   Switch AI provider
  !model [name]      Show or set AI model (!model default to reset)
  !history [n]       Show last n commands (default: 20)
  !config            Show current configuration
  !alias <name>=<cmd> Create alias
  !aliases           List all aliases
  !update            Update to latest version
  !uninstall         Remove natsh

\033[36mSpecial:\033[0m
  ?<text>            Explain what a command does
  !<command>         Run command directly (bypass AI)

\033[36mExamples:\033[0m
  show all files     -> dir (translated by AI)
  ?dir /s            -> explains the command
  !dir               -> runs dir directly
  !model gpt-5.2     -> switch to GPT-5.2

\033[90mType 'exit' or press Ctrl+C to quit\033[0m
""")

def show_config():
    """Display current configuration"""
    print("\n\033[36mCurrent configuration:\033[0m\n")
    print(json.dumps(config, indent=2))
    print()

def show_welcome():
    """Display welcome message"""
    provider = config.get("provider", "gemini")
    model = config.get("model", {}).get(provider, "default")
    print()
    print(f"\033[1mnatsh\033[0m v{VERSION} - Natural Shell")
    print(f"\033[90mProvider: {provider.upper()} | Model: {model} | Type !help for commands\033[0m")
    print()

# ============== Alias Management ==============

def add_alias(name: str, command: str):
    """Add a new alias"""
    if "aliases" not in config:
        config["aliases"] = {}
    config["aliases"][name] = command
    save_config()
    print(f"\033[32mAlias '{name}' created.\033[0m")

def show_aliases():
    """Display all aliases"""
    aliases = config.get("aliases", {})
    if not aliases:
        print("\033[90mNo aliases defined. Create one with: !alias name=command\033[0m")
        return

    print("\n\033[36mAliases:\033[0m\n")
    for name, cmd in aliases.items():
        print(f"  \033[33m{name}\033[0m = {cmd}")
    print()

def resolve_alias(text: str) -> str:
    """Resolve alias if exists"""
    aliases = config.get("aliases", {})
    parts = text.split()
    if parts and parts[0] in aliases:
        args = " ".join(parts[1:])
        return aliases[parts[0]] + (" " + args if args else "")
    return text

# ============== Command Execution ==============

def run_command(command: str) -> tuple:
    """Execute a shell command and return stdout, stderr"""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout, result.stderr

def get_install_paths():
    """Get installation paths based on OS"""
    if IS_WINDOWS:
        install_dir = HOME / ".natsh"
        bin_paths = [HOME / ".local" / "bin" / "natsh.bat", HOME / ".local" / "bin" / "natsh.ps1"]
    else:
        install_dir = HOME / ".natsh"
        bin_paths = [HOME / ".local" / "bin" / "natsh"]
    return install_dir, bin_paths

# ============== Main Loop ==============

def main():
    global ai_client, config

    # Initialize
    NATSH_DIR.mkdir(parents=True, exist_ok=True)
    load_env()
    config = load_config()
    load_history()

    # Check for API key
    provider = config.get("provider", "gemini")
    key_name = get_provider_key_name(provider)

    if not os.environ.get(key_name):
        show_welcome()
        if not setup_api_key(provider):
            sys.exit(1)

    # Initialize AI client
    ai_client = init_ai_client()
    if ai_client is None:
        print(f"\033[31mFailed to initialize {provider}. Run !api to set key.\033[0m")
    else:
        show_welcome()

    # Main loop
    while True:
        try:
            cwd = os.getcwd()
            folder_name = os.path.basename(cwd) or cwd
            prompt = f"\033[32m{folder_name}\033[0m > "
            user_input = input(prompt).strip()

            if not user_input:
                continue

            # === Handle CD command ===
            if user_input.lower().startswith("cd "):
                path = user_input[3:].strip()
                if IS_WINDOWS:
                    path = os.path.expandvars(path)
                path = os.path.expanduser(path)
                try:
                    os.chdir(path)
                except Exception as e:
                    print(f"cd: {e}")
                continue
            elif user_input.lower() == "cd":
                os.chdir(str(HOME))
                continue

            # === Exit commands ===
            if user_input.lower() in ["exit", "quit", "q"]:
                print("\033[90mGoodbye!\033[0m")
                sys.exit(0)

            # === Special commands ===
            if user_input == "!help":
                show_help()
                continue

            if user_input.startswith("!api"):
                parts = user_input.split()
                prov = parts[1] if len(parts) > 1 else config.get("provider", "gemini")
                if prov not in ["gemini", "openai", "claude"]:
                    print("\033[31mInvalid provider. Use: gemini, openai, claude\033[0m")
                    continue
                if setup_api_key(prov):
                    ai_client = init_ai_client(prov)
                continue

            if user_input.startswith("!provider"):
                parts = user_input.split()
                if len(parts) < 2:
                    print(f"\033[90mCurrent provider: {config.get('provider', 'gemini')}\033[0m")
                    print("Available: gemini, openai, claude")
                    continue
                prov = parts[1].lower()
                if prov not in ["gemini", "openai", "claude"]:
                    print("\033[31mInvalid provider. Use: gemini, openai, claude\033[0m")
                    continue
                config["provider"] = prov
                save_config()
                key_name = get_provider_key_name(prov)
                if not os.environ.get(key_name):
                    print(f"\033[33mNo API key for {prov}. Setting up...\033[0m")
                    setup_api_key(prov)
                ai_client = init_ai_client(prov)
                if ai_client:
                    print(f"\033[32mSwitched to {prov.upper()}\033[0m")
                continue

            if user_input.startswith("!model"):
                parts = user_input.split(maxsplit=1)
                prov = config.get("provider", "gemini")
                current_model = config.get("model", {}).get(prov, "")
                default_model = DEFAULT_CONFIG["model"].get(prov, "")
                if len(parts) < 2:
                    print(f"\033[90mCurrent model ({prov}): {current_model}\033[0m")
                    print(f"\033[90mDefault model ({prov}): {default_model}\033[0m")
                    print("\nUsage: !model <model-name>")
                    print("       !model default        # reset to default")
                    print("\nExamples:")
                    print("  !model gpt-4o              # for OpenAI")
                    print("  !model claude-sonnet-4-20250514  # for Claude")
                    print("  !model gemini-2.0-flash    # for Gemini")
                    continue
                new_model = parts[1].strip()
                # Handle "default" keyword
                if new_model.lower() == "default":
                    new_model = default_model
                if "model" not in config:
                    config["model"] = {}
                config["model"][prov] = new_model
                save_config()
                # Reinitialize client with new model
                ai_client = init_ai_client(prov)
                if ai_client:
                    print(f"\033[32mModel set to: {new_model}\033[0m")
                continue

            if user_input.startswith("!history"):
                parts = user_input.split()
                try:
                    count = int(parts[1]) if len(parts) > 1 else 20
                except ValueError:
                    count = 20
                show_history(count)
                continue

            if user_input == "!config":
                show_config()
                continue

            if user_input.startswith("!alias "):
                alias_def = user_input[7:].strip()
                if "=" in alias_def:
                    name, cmd = alias_def.split("=", 1)
                    add_alias(name.strip(), cmd.strip())
                else:
                    print("\033[31mUsage: !alias name=command\033[0m")
                continue

            if user_input == "!aliases":
                show_aliases()
                continue

            if user_input == "!update":
                print("\033[33m[..] Checking for updates...\033[0m")
                try:
                    import urllib.request
                    import re
                    import base64
                    # Use GitHub API (no cache) instead of raw.githubusercontent.com
                    api_url = "https://api.github.com/repos/pieronoviello/natsh/contents/natsh.py"
                    req = urllib.request.Request(api_url, headers={"Accept": "application/vnd.github.v3+json"})
                    with urllib.request.urlopen(req) as response:
                        data = json.loads(response.read().decode('utf-8'))
                    # Decode base64 content
                    remote_content = base64.b64decode(data['content']).decode('utf-8')
                    # Extract version from remote file
                    match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', remote_content)
                    if not match:
                        print("\033[31m[X] Could not determine remote version\033[0m")
                        continue
                    remote_version = match.group(1)
                    if remote_version == VERSION:
                        print(f"\033[32m[OK] Already up to date (v{VERSION})\033[0m")
                        continue
                    # New version available - save it
                    print(f"\033[33m[..] Updating v{VERSION} -> v{remote_version}...\033[0m")
                    local_path = NATSH_DIR / "natsh.py"
                    with open(local_path, 'w', encoding='utf-8') as f:
                        f.write(remote_content)
                    print(f"\033[32m[OK] Updated to v{remote_version}!\033[0m")
                    print("\033[90mType 'exit' and run 'natsh' again to use the new version.\033[0m")
                except Exception as e:
                    print(f"\033[31m[X] Update failed: {e}\033[0m")
                continue

            if user_input == "!uninstall":
                confirm = input("\033[33mRemove natsh? [y/N]\033[0m ")
                if confirm.lower() == "y":
                    install_dir, bin_paths = get_install_paths()
                    if IS_WINDOWS:
                        # On Windows, create a batch script that runs after we exit
                        import tempfile
                        batch_content = f'''@echo off
timeout /t 2 /nobreak >nul
rmdir /s /q "{install_dir}"
del /f /q "{bin_paths[0]}" 2>nul
del /f /q "{bin_paths[1]}" 2>nul
echo natsh uninstalled successfully
del "%~f0"
'''
                        batch_path = Path(tempfile.gettempdir()) / "natsh_uninstall.bat"
                        with open(batch_path, "w") as f:
                            f.write(batch_content)
                        subprocess.Popen(f'start /min cmd /c "{batch_path}"', shell=True)
                        print("\033[32mUninstalling... (closes in 2 seconds)\033[0m")
                        sys.exit(0)
                    else:
                        import shutil
                        if install_dir.exists():
                            shutil.rmtree(install_dir)
                        for bin_path in bin_paths:
                            if bin_path.exists():
                                bin_path.unlink()
                        print("\033[32mnatsh uninstalled\033[0m")
                        sys.exit(0)
                continue

            # === Explain mode ===
            if user_input.startswith("?"):
                cmd_to_explain = user_input[1:].strip()
                if cmd_to_explain:
                    print(f"\033[90mExplaining: {cmd_to_explain}\033[0m")
                    explanation = explain_command(cmd_to_explain)
                    print(f"\n{explanation}\n")
                continue

            # === Direct command execution ===
            if user_input.startswith("!"):
                cmd = user_input[1:]
                if not cmd:
                    continue
                stdout, stderr = run_command(cmd)
                print(stdout, end="")
                if stderr:
                    print(stderr, end="")
                add_to_history(user_input, cmd, stdout + stderr)
                continue

            # === Check for alias ===
            user_input = resolve_alias(user_input)

            # === Direct shell command ===
            if not is_natural_language(user_input):
                stdout, stderr = run_command(user_input)
                print(stdout, end="")
                if stderr:
                    print(stderr, end="")
                add_to_history(user_input, user_input, stdout + stderr)
                continue

            # === AI Translation ===
            if ai_client is None:
                print("\033[31mAI not initialized. Run !api to set up.\033[0m")
                continue

            command = get_command(user_input, cwd)

            if not command:
                print("\033[31mCould not generate command.\033[0m")
                continue

            # Check for dangerous command
            if is_dangerous_command(command):
                confirm = input(f"\033[31m[!] {command}\033[0m \033[33m(dangerous) [y/N]\033[0m ")
                if confirm.lower() != "y":
                    add_to_history(user_input, command, "", executed=False)
                    continue
            else:
                confirm = input(f"\033[33m-> {command}\033[0m [Enter/n] ")
                if confirm.lower() in ["n", "no"]:
                    add_to_history(user_input, command, "", executed=False)
                    continue

            # Execute command
            if command.lower().startswith("cd "):
                path = command[3:].strip()
                if IS_WINDOWS:
                    path = os.path.expandvars(path)
                path = os.path.expanduser(path)
                try:
                    os.chdir(path)
                    add_to_history(user_input, command, f"Changed to {path}")
                except Exception as e:
                    print(f"cd: {e}")
            else:
                stdout, stderr = run_command(command)
                print(stdout, end="")
                if stderr:
                    print(stderr, end="")
                add_to_history(user_input, command, stdout + stderr)

        except EOFError:
            print("\n\033[90mGoodbye!\033[0m")
            break
        except KeyboardInterrupt:
            print()  # New line after ^C
            continue
        except Exception as e:
            err = str(e)
            if "429" in err or "quota" in err.lower() or "rate" in err.lower():
                print("\033[31mRate limit hit - wait a moment and try again\033[0m")
            elif "API key" in err or "authentication" in err.lower() or "apikey" in err.lower():
                print("\033[31mAPI key error - run !api to set a new key\033[0m")
            elif "InterruptedError" not in err and "KeyboardInterrupt" not in err:
                print(f"\033[31mError: {err[:100]}\033[0m")

if __name__ == "__main__":
    main()
