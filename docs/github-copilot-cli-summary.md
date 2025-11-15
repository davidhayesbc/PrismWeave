# GitHub Copilot CLI Summary

## 1. What is GitHub Copilot CLI?

GitHub Copilot CLI is a command-line interface that allows developers to interact with GitHub Copilot directly from their terminal. It enables users to leverage AI-powered assistance for coding tasks, debugging, answering questions, and interacting with GitHub.com without leaving the command line. As of November 2025, Copilot CLI is in public preview and subject to change, with data protection policies in place.

Key characteristics:

- **AI-Powered Assistant**: Uses advanced language models (default: Claude Sonnet 4.5) to provide intelligent responses and perform tasks.
- **Terminal Integration**: Works seamlessly in Linux, macOS, and Windows (via WSL or experimental PowerShell support).
- **Security-Focused**: Includes trusted directories, tool approval mechanisms, and risk mitigation features.
- **Extensible**: Supports custom agents, MCP servers, and repository-specific instructions.
- **Availability**: Requires a GitHub Copilot Pro, Pro+, Business, or Enterprise subscription. Organizational access may be restricted by admin policies.

Copilot CLI bridges the gap between conversational AI and practical development workflows, allowing for iterative coding, Git operations, and GitHub interactions directly from the terminal.

## 2. Installation and Setup

### Prerequisites

- GitHub Copilot subscription (Pro, Pro+, Business, or Enterprise).
- Node.js version 22 or later.
- npm version 10 or later.
- If using via organization/enterprise, ensure the Copilot CLI policy is enabled by administrators.

### Installation

Install or update Copilot CLI globally using npm:

```bash
npm install -g @github/copilot
```

### Initial Setup

1. **Authentication**: On first use, run `copilot` and use the `/login` slash command to authenticate with GitHub.
2. **Trusted Directories**: When starting a session, confirm trust for the current directory. You can choose to trust for the current session only or permanently.
3. **Configuration**: Edit `~/.copilot/config.json` for settings like trusted folders. Use `copilot help config` for details.
4. **Optional Alias**: For direct command execution, set up the `ghcs` alias:
   - Bash: `echo 'eval "$(gh copilot alias -- bash)"' >> ~/.bashrc`
   - Zsh: `echo 'eval "$(gh copilot alias -- zsh)"' >> ~/.zshrc`
   - PowerShell: Configure via `gh copilot alias -- pwsh`

### Environment Variables

- `XDG_CONFIG_HOME`: Changes the default config directory from `~/.copilot`.
- Logging levels and other settings can be adjusted via `copilot help environment`.

## 3. Key Features and Commands

### Modes of Use

- **Interactive Mode**: Start with `copilot` for conversational sessions where you can ask questions, perform tasks, and iterate.
- **Programmatic Mode**: Use `copilot -p "prompt"` or `copilot --prompt "prompt"` for single prompts. Add `--allow-all-tools` for automatic tool approval.

### Core Commands and Features

- **Slash Commands** (in interactive mode):
  - `/login`: Authenticate with GitHub.
  - `/add-dir /path`: Add a trusted directory.
  - `/cwd /path`: Change working directory.
  - `/delegate prompt`: Push session to Copilot coding agent on GitHub.
  - `/agent`: Select custom agents.
  - `/mcp`: Manage MCP servers.
  - `/model`: Change AI model.
  - `/usage`: View session statistics and token usage.
  - `/feedback`: Provide feedback.
  - `/resume` or `/continue`: Resume previous sessions.

- **Tool Approval**: For commands that modify files or run executables, Copilot requests approval. Options include:
  - Approve once.
  - Approve for the session.
  - Deny and suggest alternatives.

- **Command-Line Options**:
  - `--allow-all-tools`: Bypass all approvals.
  - `--deny-tool 'shell(command)'`: Block specific tools.
  - `--allow-tool 'shell(command)'`: Permit specific tools.
  - `--agent=name`: Use a specific custom agent.

- **Direct Shell Execution**: Prefix with `!` to run shell commands without AI processing, e.g., `!git status`.

### Integration Features

- **File References**: Use `@path/to/file` to include file contents in prompts.
- **Custom Instructions**: Load from `.github/copilot-instructions.md` or path-specific files.
- **Custom Agents**: Define specialized agents in `~/.copilot/agents`, `.github/agents`, or organization repositories.
- **MCP Servers**: Extend functionality with Model Context Protocol servers (GitHub MCP included by default).

## 4. Common Use Cases

### Local Development Tasks

- **Code Modifications**: "Change the background-color of H1 headings to dark blue" – Updates CSS files directly.
- **Code Analysis**: "Suggest improvements to content.js" or "Rewrite the readme in this project to make it more accessible."
- **Git Operations**: "Commit the changes to this repo" or "Revert the last commit, leaving the changes unstaged."
- **Application Creation**: Build proofs-of-concept, e.g., "Create a Next.js dashboard app using Tailwind CSS and GitHub API data."
- **Debugging**: "Explain why this code isn't working" or fix issues iteratively.

### GitHub.com Interactions

- **Issue and PR Management**: "List my open PRs" or "Work on issue #123 in a new branch."
- **Pull Request Creation**: "Add a Node script user-info.js and create a PR."
- **Repository Tasks**: "Raise an improvement issue in owner/repo" or "Check changes in PR #57575."
- **Workflows**: "Create a GitHub Actions workflow for ESLint checks and PR failures."
- **Automation**: "Merge all open PRs I've created in owner/repo."

### Command Assistance

- **Explanations**: `gh copilot explain "sudo apt-get"` – Provides detailed command breakdowns.
- **Suggestions**: `gh copilot suggest "Undo the last commit"` – Offers command options with interactive refinement.
- **Execution**: With `ghcs` alias, directly execute suggested commands.

## 5. Integration with Development Workflows

### IDE and Terminal Synergy

- Use Copilot CLI alongside IDE Copilot for seamless transitions between coding environments.
- Delegate complex tasks from CLI to Copilot coding agent on GitHub for background processing and PR creation.

### CI/CD and Automation

- Integrate into scripts for automated code generation, testing, or deployment prep.
- Use programmatic mode in build scripts or cron jobs with `--allow-all-tools` for headless operation.

### Team Collaboration

- Share custom agents and instructions via repository or organization settings.
- Leverage MCP servers for extended integrations, like Azure or other platforms.

### Version Control Workflows

- Automate Git operations, branch management, and PR workflows.
- Ensure atomic commits and meaningful messages through AI-assisted prompts.

### Security and Compliance

- Operate in restricted environments (VMs, containers) to limit risks.
- Configure tool permissions to align with organizational policies.

## 6. Best Practices

### Security

- **Trusted Directories**: Only trust directories you control; avoid home directories with sensitive data.
- **Tool Approvals**: Review commands carefully; use session approvals judiciously to avoid unintended actions.
- **Risk Mitigation**: Run in isolated environments; avoid `--allow-all-tools` in untrusted contexts.
- **Permissions**: Use `--deny-tool` for risky commands like `rm` or `git push` if needed.

### Productivity

- **Context Provision**: Include file references (@file) and custom instructions for better AI responses.
- **Iterative Work**: Use interactive mode for complex tasks; resume sessions with `--continue`.
- **Feedback Loop**: Rate suggestions and provide feedback via `/feedback` to improve future responses.
- **Model Selection**: Switch models via `/model` for different task types (e.g., coding vs. explanation).

### Configuration

- **Aliases and Shortcuts**: Set up `ghcs` for quick command execution.
- **Custom Agents**: Create specialized agents for repetitive tasks or team conventions.
- **MCP Extensions**: Add relevant servers to expand capabilities without custom development.

### Usage Optimization

- **Token Awareness**: Monitor usage with `/usage`; avoid context truncation by managing session length.
- **Data Privacy**: Opt out of analytics if preferred via `gh copilot config`.
- **Updates**: Regularly update via `npm install -g @github/copilot` for latest features.

### Workflow Integration

- **Start Small**: Begin with simple prompts and scale to complex tasks.
- **Combine Modes**: Use interactive for exploration, programmatic for automation.
- **Documentation**: Maintain custom instructions for project-specific guidance.

By following these practices, developers can maximize the benefits of GitHub Copilot CLI while maintaining security and efficiency in their workflows.
