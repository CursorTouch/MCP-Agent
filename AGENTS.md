# MCP Agent: Cognitive Process Architecture

## 🧠 Core Philosophy
This project reimagines an AI Agent not as a chatbot, but as an **Intelligent Cognitive Process** running on a Virtual Kernel. This architecture strictly mirrors Modern Operating System concepts, treating "Thinking" as CPU cycles and "Context" as Memory.

## 🏗️ Architecture Stack

### 1. The Kernel (Main Process)
- **Role**: Scheduler & Orchestrator.
- **Responsibility**: Holds the Main Goal. Spawns threads. Manages resources.
- **Analogy**: The OS Kernel (Ring 0).

### 2. The Threads (Workers)
- **Role**: Execution Contexts.
- **Responsibility**: Perform atomic subtasks (e.g., "Search Web", "Read File").
- **Analogy**: User Mode Processes (Ring 3).
- **Isolation**: Strictly sandboxed. A thread cannot see its parent's plan or its sibling's data.

### 3. IPC (Inter-Process Communication)
- **Mechanism**: Data passed via strict `Start Tool` (arguments) and `Stop Tool` (results).
- **Protocol**: No shared global variables. Pure message passing.

---

## 🧵 Threading Strategy (The "Scheduler")

The Agent implements a **Recursive Hierarchical Task Scheduler**:

1.  **Atomic Decomposition**
    - Complex tasks are broken down into single-purpose threads.
    - *Example*: "Research and Write Report" -> Spawns `Thread-A` (Research) -> Waits -> Spawns `Thread-B` (Write).

2.  **Context Switching (Virtual Memory)**
    - When switching threads, the system performs a "Context Switch."
    - **Scope Restriction**: The LLM prompt is dynamically rebuilt to show ONLY the active thread's history.
    - **Prevention**: This prevents **Context Pollution** (Hallucinations caused by irrelevant history).

3.  **Resource Management (Smart Connect)**
    - Threads attach to **MCP Servers** (Model Context Protocol).
    - **Optimization**: The Scheduler automatically reuses TCP connections if the next thread uses the same server (e.g., FileSystem to FileSystem).

---

## 🛡️ Security & Constraints

1.  **Hierarchical Visibility (Virtual Memory)**
    - Child Threads CANNOT see Parent Threads.
    - Sibling Threads CANNOT see each other.
    - This creates a **Trust Boundary**. A "Worker" cannot manipulate the "Manager's" plan.

2.  **Strict Lifecycle (Zombie Prevention)**
    - Every started thread MUST be stopped.
    - Unhandled errors in children bubble up to the parent as `Stop Tool(error="...")`.

---

## 🔮 Future Roadmap: Multi-Process Swarm

While the current implementation is Single-Process / Multi-Thread, the design is "Fractal"—ready to scale to **Multi-Process**.

| Component | Current (Threaded) | Future (Multi-Process) |
| :--- | :--- | :--- |
| **Unit** | Python `Thread` Object | Docker Container / Separate Process |
| **Memory** | Shared Heap (Filtered) | Physical Isolation (Network) |
| **Communication** | Function Calls | HTTP / MCP Protocol |
| **Orchestration** | `process/service.py` | Supervisor Agent (Kubernetes-style) |

---

## 🧩 Key Terminologies

- **Process (PID: Main)**: The Agent instance.
- **Thread**: A specific subtask context.
- **Work Item**: A message/instruction.
- **Syscall**: Using a Tool (Start/Switch/Stop).
- **Context Switch**: Changing the active prompt history.
- **MCP Server**: An external peripheral (like a mounted drive).
