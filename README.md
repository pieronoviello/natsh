# natsh - Natural Shell

> Talk to your terminal in plain words

**natsh** translates natural language into shell commands using AI. Supports multiple AI providers: Gemini (free), OpenAI, and Claude.

## Demo

```
Downloads > show me all files
-> dir [Enter]
 Volume in drive C is Windows
 Directory of C:\Users\dev\Downloads
...

Downloads > create a folder called projects
-> mkdir projects [Enter]

Downloads > delete the folder I just created
[!] rmdir /s /q projects (dangerous) [y/N] y

Downloads > open notepad
-> start notepad [Enter]
```

## Features

- **Natural Language to Commands**: Just describe what you want to do
- **Multi-AI Provider**: Switch between Gemini (free), OpenAI, or Claude
- **Model Selection**: Use any model (gpt-5.2, claude-sonnet-4, gemini-2.0-flash, etc.)
- **Safe Mode**: Asks confirmation for dangerous commands (del, rmdir, etc.)
- **Command History**: Persistent history across sessions (100 commands)
- **Explain Mode**: Use `?command` to understand what a command does
- **Aliases**: Create shortcuts for frequent commands
- **Auto-Update**: Update to latest version with `!update`
- **Windows Native**: Built for Windows CMD, uses proper Windows commands

## Installation

### Quick Install (PowerShell)

```powershell
irm https://raw.githubusercontent.com/pieronoviello/natsh/main/install.ps1 | iex
```

Then run `natsh` (works immediately, no need to open a new terminal).

### Manual Install

```powershell
git clone https://github.com/pieronoviello/natsh.git
cd natsh
.\install.ps1
```

### Requirements

- Windows 10/11
- Python 3.8+
- API key from one of: [Gemini](https://aistudio.google.com/apikey) (free), [OpenAI](https://platform.openai.com/api-keys), or [Claude](https://console.anthropic.com/settings/keys)

## Usage

```
natsh
```

### Commands

| Command | Description |
|---------|-------------|
| `!help` | Show help |
| `!api [provider]` | Set API key for provider |
| `!provider <name>` | Switch AI provider (gemini/openai/claude) |
| `!model <name>` | Switch AI model (e.g., gpt-4o, gpt-5.2, claude-sonnet-4-20250514) |
| `!history [n]` | Show last n commands (default: 20) |
| `!config` | Show configuration |
| `!alias name=cmd` | Create alias |
| `!aliases` | List aliases |
| `!update` | Update to latest version |
| `!uninstall` | Remove natsh |
| `?<command>` | Explain a command |
| `!<command>` | Run command directly (bypass AI) |
| `exit` / `quit` | Exit natsh |

### Examples

```bash
# Natural language (translated by AI)
show all files              # -> dir
list python files           # -> dir *.py
go to downloads             # -> cd %USERPROFILE%\Downloads
open chrome                 # -> start chrome
delete temp folder          # -> rmdir /s /q temp

# Explain mode
?dir /s /b                  # Explains the command

# Direct execution (bypass AI)
!dir                        # Runs dir directly
!git status                 # Runs git status directly

# Aliases
!alias ll=dir /w            # Create alias
ll                          # Uses alias -> dir /w
```

## AI Providers

| Provider | Default Model | Cost | Get API Key |
|----------|---------------|------|-------------|
| **Gemini** (default) | gemini-2.5-flash | Free (with limits) | [aistudio.google.com](https://aistudio.google.com/apikey) |
| **OpenAI** | gpt-4o-mini | ~$0.15/1M tokens | [platform.openai.com](https://platform.openai.com/api-keys) |
| **Claude** | claude-3-haiku | ~$0.25/1M tokens | [console.anthropic.com](https://console.anthropic.com/settings/keys) |

### Switching Providers & Models

```bash
!provider openai            # Switch to OpenAI
!provider claude            # Switch to Claude
!api openai                 # Set API key for specific provider

# Change model (use any valid model name for your provider)
!model gpt-5.2              # Use GPT-5.2 instead of gpt-4o-mini
!model gpt-4o               # Use GPT-4o
!model claude-sonnet-4-20250514  # Use Claude Sonnet 4
!model gemini-2.0-flash     # Use Gemini 2.0 Flash
```

## Configuration

Configuration is stored in `~/.natsh/config.json`:

```json
{
  "provider": "gemini",
  "model": {
    "gemini": "gemini-2.5-flash",
    "openai": "gpt-4o-mini",
    "claude": "claude-3-haiku-20240307"
  },
  "safe_mode": true,
  "max_history": 100,
  "aliases": {
    "ll": "dir /w"
  }
}
```

## File Structure

```
~/.natsh/
├── natsh.py         # Main script
├── config.json      # Configuration
├── history.json     # Command history
├── .env             # API keys (never committed)
└── venv/            # Python virtual environment

~/.local/bin/
├── natsh.bat        # Command wrapper (CMD)
└── natsh.ps1        # Command wrapper (PowerShell)
```

## Update

```bash
!update              # Check and install updates from within natsh
```

## Uninstall

From within natsh:
```bash
!uninstall
```

Or manually:
```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.natsh"
Remove-Item -Force "$env:USERPROFILE\.local\bin\natsh.*"
```

## License

MIT License - see [LICENSE](LICENSE) file.
