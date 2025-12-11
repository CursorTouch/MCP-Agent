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

- **Logical Threads**: Unlike operating system threads that run in parallel on physical cores, our "Threads" are **logical execution contexts**. They isolate the conversation history and state for specific subtasks. This prevents **Context Pollution**, where an LLM gets confused by too much instruction history from unrelated tasks.
- **Hierarchical Visibility (Virtual Memory)**: The agent implements strict **Scope Restriction**. A Child Thread cannot see its Parent's history or its Siblings' existence. It only operates within its specific subtask. This mirrors **Virtual Memory isolation** in OS processes, ensuring stability and focus.
- **Context Switching**: The Agent acts as a scheduler. When it switches tools or tasks, it performs a "context switch," saving the state of the current thread and loading the new one. This allows it to "pause" a complex high-level plan, dive deep into a specific detail (like searching a file), and then return to the main plan with the answer—just like a CPU handling an interrupt.
- **Strict Manager-Worker Model**: Only the **Parent Thread** (the Manager) can call the `Switch Tool` to multitask between its children. Child Threads (Workers) are "sandboxed" and must simply complete their assigned subtask and `Stop Tool`, preventing them from jumping into unrelated workflows.
- **Resiliency**: If a sub-thread crashes or gets stuck (e.g., a tool failure), the parent thread can catch the error and decide to retry or try a different approach, preventing the entire agent from crashing.

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
