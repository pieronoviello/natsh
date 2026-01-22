# natsh - Natural Shell

> Talk to your terminal in plain English

**natsh** translates natural language into shell commands using AI. Supports multiple AI providers: Gemini (free), OpenAI, and Claude.

## Demo

```
Downloads > show me all files
-> dir [Enter]
 Volume in drive C is Windows
 Directory of C:\Users\piero\Downloads
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
- **Safe Mode**: Asks confirmation for dangerous commands (del, rmdir, etc.)
- **Command History**: Persistent history across sessions
- **Explain Mode**: Use `?command` to understand what a command does
- **Aliases**: Create shortcuts for frequent commands
- **Windows Native**: Built for Windows CMD, uses proper Windows commands

## Installation

### Quick Install (PowerShell)

```powershell
irm https://raw.githubusercontent.com/pieronoviello/natsh/main/install.ps1 | iex
```

### Manual Install

```powershell
# Clone repository
git clone https://github.com/pieronoviello/natsh.git
cd natsh

# Run installer
.\install.ps1
```

### Requirements

- Windows 10/11
- Python 3.8+
- API key from one of: [Gemini](https://aistudio.google.com/apikey) (free), [OpenAI](https://platform.openai.com/api-keys), or [Claude](https://console.anthropic.com/settings/keys)

## Usage

After installation, open a **new terminal** and run:

```
natsh
```

### Commands

| Command | Description |
|---------|-------------|
| `!help` | Show help |
| `!api [provider]` | Set API key for provider |
| `!provider <name>` | Switch AI provider (gemini/openai/claude) |
| `!history [n]` | Show last n commands |
| `!config` | Show configuration |
| `!alias name=cmd` | Create alias |
| `!aliases` | List aliases |
| `?<command>` | Explain a command |
| `!<command>` | Run command directly (bypass AI) |
| `!uninstall` | Remove natsh |

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

| Provider | Model | Cost | Get API Key |
|----------|-------|------|-------------|
| **Gemini** (default) | gemini-2.5-flash | Free (with limits) | [aistudio.google.com](https://aistudio.google.com/apikey) |
| **OpenAI** | gpt-4o-mini | ~$0.15/1M tokens | [platform.openai.com](https://platform.openai.com/api-keys) |
| **Claude** | claude-3-haiku | ~$0.25/1M tokens | [console.anthropic.com](https://console.anthropic.com/settings/keys) |

### Switching Providers

```bash
# Switch to OpenAI
!provider openai

# Switch to Claude
!provider claude

# Set API key for specific provider
!api openai
```

## Configuration

Configuration is stored in `~/.natsh/config.json`:

```json
{
  "provider": "gemini",
  "safe_mode": true,
  "max_history": 100,
  "aliases": {
    "ll": "dir /w",
    "cls": "cls"
  }
}
```

## File Structure

```
~/.natsh/
├── natsh.py          # Main script
├── config.json      # Configuration
├── history.json     # Command history
├── .env             # API keys (never committed)
└── venv/            # Python virtual environment

~/.local/bin/
└── natsh.bat         # Command wrapper
```

## Uninstall

### Quick Uninstall (PowerShell)

```powershell
irm https://raw.githubusercontent.com/pieronoviello/natsh/main/uninstall.ps1 | iex
```

### From within natsh

```bash
!uninstall
```

### Manual Uninstall

```bash
rmdir /s /q %USERPROFILE%\.natsh
del %USERPROFILE%\.local\bin\natsh.bat
del %USERPROFILE%\.local\bin\natsh.ps1
```

This removes:
- `~/.natsh/` - Configuration, history, API keys, virtual environment
- `~/.local/bin/natsh.bat` - Command wrapper (CMD)
- `~/.local/bin/natsh.ps1` - Command wrapper (PowerShell)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file.
