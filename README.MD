<div align="center">

  <h1>🎮 MCP Agent</h1>

  <a href="https://github.com/Jeomon/MCP-Agent/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  </a>
  <img src="https://img.shields.io/badge/python-3.13%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/platform-Cross%20Platform-blue" alt="Platform">
  <img src="https://img.shields.io/github/last-commit/Jeomon/MCP-Agent" alt="Last Commit">
  <br>
  <a href="https://x.com/CursorTouch">
    <img src="https://img.shields.io/badge/follow-%40CursorTouch-1DA1F2?logo=twitter&style=flat" alt="Follow on Twitter">
  </a>
  <a href="https://discord.com/invite/Aue9Yj2VzS">
    <img src="https://img.shields.io/badge/Join%20on-Discord-5865F2?logo=discord&logoColor=white&style=flat" alt="Join us on Discord">
  </a>

</div>

<br>

**MCP Agent** is an advanced AI agentic framework designed to interact with **Model Context Protocol (MCP)** servers. It employs a multi-threaded architecture to decompose complex tasks into subtasks, dynamically connecting to configured MCP servers to utilize their tools and resources.

## ✨ Key Capabilities

- **🧠 Multi-Threaded Task Execution**  
  Decomposes complex requests into manageable subtasks, spawning separate threads to handle specific aspects of a problem using appropriate resources.

- **🔌 Universal MCP Integration**  
  Connects to any MCP server defined in your configuration, allowing the agent to dynamically discover and use tools for filesystem access, web search, database interaction, and more.

- **🤖 Multi-LLM Support**  
  Built-in support for a wide range of LLMs including **Google Gemini**, **OpenAI**, **Anthropic**, **Mistral**, **Ollama**, **Groq**, **Cerebras**, and **OpenRouter**.

- **🛠️ Extensible Tool System**  
  The agent automatically assimilates tools from connected MCP servers, making them available for use within its reasoning loop.

## 🧩 Architecture Deep Dive

The **MCP Agent** implements a unique **"Virtual CPU"** architecture for cognitive tasks.

- **Logical Threads (Process States)**: Unlike OS threads that run in parallel, our "Threads" are logical execution contexts. They map to **Process States** in an OS. Each thread has its own isolated memory (conversation history) and state (ready, running, blocked). This prevents **Context Pollution**, ensuring the LLM focuses only on the immediate subtask without being distracted by global history.

- **Hierarchical Visibility (Virtual Memory)**: The agent implements strict **Scope Restriction** similar to **Virtual Memory Isolation**.
  - A **Child Thread** cannot access the Parent's memory (history) or see Independent Sibling threads. It operates in a sandboxed environment.
  - This acts as a **Memory Management Unit (MMU)** for the LLM, enforcing that a "worker" process only sees the data it needs to do its job, preventing hallucinated cross-thread communication.

- **Context Switching (The Scheduler)**: The `Agent` class acts as the **OS Kernel/Scheduler**.
  - **Syscall (Start Tool)**: When a thread needs to perform a subtask, it invokes a "syscall" to create a new process (Start Tool). The Kernel saves the Parent's state (Push to Stack) and loads the Child's empty state.
  - **Interrupt (Stop Tool)**: When a child finishes, it triggers an interrupt. The Kernel terminates the child, pops the stack, and restores the Parent's context with the result in the "return register."

- **Strict User/Kernel Mode (Ring Protection)**:
  - **Parent Thread (Ring 0)**: Acts as the Manager/Kernel. It has full visibility of its children and can use the `Switch Tool` to multitask between them.
  - **Child Thread (Ring 3)**: Acts as User Mode. It is restricted. It cannot arbitrarily jump to other threads or modify the global plan. It must simply complete its task and exit (`Stop Tool`), ensuring stability and preventing "runaway processes."

- **Resiliency (Fault Tolerance)**: Just as an OS doesn't crash if a user application segfaults, a failure in a Child Thread doesn't kill the Agent. The Parent Thread catches the "exception" (error message) from the dead child and can decide to spawn a new thread (retry) or change strategies.

## 🚀 Getting Started

### Prerequisites

- **Python 3.13+**
- **uv** (Recommended for dependency management)

### 1. Clone the Repository

```bash
git clone https://github.com/Jeomon/MCP-Agent.git
cd MCP-Agent
```

### 2. Install Dependencies

Using `uv` (Recommended):
```bash
uv sync
```

Or using `pip`:
```bash
pip install .
```

### 3. Configure Environment

Create a `.env` file in the project root and add your LLM API keys:

```env
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
# Add other keys as needed (MISTRAL_API_KEY, ANTHROPIC_API_KEY, etc.)
```

### 4. Configure MCP Servers

Create a `config.json` file in the project root to define available MCP servers. You can use `config-example.json` as a template:

```json
{
  "mcpServers": {
    "filesystem": {
      "description": "Access to local files",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "D:/Projects"]
    },
    "brave-search": {
      "description": "Web search capability",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your_brave_api_key"
      }
    }
  }
}
```

### 5. Run the Agent

```bash
# If using uv
uv run main.py

# If using standard python
python main.py
```

## ⚙️ Customization

### Changing the LLM
The agent is configured to use **Google Gemini** by default. To change the LLM, modify `main.py`:

```python
# main.py

# Uncomment the LLM you want to use:
# llm=ChatMistral(model='mistral-large-latest', api_key=os.getenv('MISTRAL_API_KEY'))
# llm=ChatOllama(model='llama3')
# llm=ChatOpenRouter(model='...', api_key=os.getenv('OPENROUTER_API_KEY'))

# Default:
llm=ChatGoogle(api_key=os.getenv('GOOGLE_API_KEY'), model='gemini-2.5-flash')
```

## 🪪 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions, ideas, and pull requests are welcome! Check out the [CONTRIBUTING](CONTRIBUTING.md) guide for more info.
