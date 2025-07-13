# NeuroCP AI – Command Line Interface Demo (MVP)
## 🚀 Welcome to the NeuroCP CLI Demo!

This command-line application is a Minimum Viable Product (MVP) showcasing foundational concepts behind the **NeuroCP AI** platform in a simplified, local environment.

**NeuroCP’s Vision**
Empowering AI agents that reason intelligently and operate with meaningful, dynamic context. Built on a modular, privacy-first, and user-controlled architecture, NeuroCP puts intelligence in your hands.

This CLI simulates how NeuroCP orchestrates three core architectural layers:

1. 🧠 **AI Intelligence Layer** – The cognitive engine of the agent.
2. 🎯 **Intent Recognition Layer** – Interpreting user goals.
3. 🔗 **Context Integration Layer** – Delivering relevant and secure data access.

Our goal is to offer a hands-on demonstration of how these elements interact, and how developers can work within the NeuroCP framework of decentralization, modularity, and trustless AI interaction.

## Core Concepts in This MVP

- Context-Aware AI Agents
Spin up unique agents that pull from isolated local datasets to personalize their responses.
- Modular Execution
Use independent commands to handle agents, manipulate contextual data, and run natural language queries.
- Privacy by Design
All context is drawn from your local files. Nothing is sent externally except user-approved queries to the OpenAI API (if an API key is set). No file uploads or hidden data transfers.
- Simulated Intelligence
When configured, OpenAI’s API is used to generate responses. However, the NeuroCP architectural blueprint is preserved and demonstrated through how this CLI manages data and workflow.

# 📋 Prerequisites
Python 3.7 or higher

OpenAI Python SDK → `pip install openai`

An OpenAI API Key (`OPENAI_API_KEY`)

# ⚙️ Quick Start Guide
### 1. Save the script:
Place the neurocp.py CLI file into your project directory (e.g., neurocp-cli-mvp).

### 2. Move into your directory:

<pre>cd path/to/neurocp-cli-mvp</pre>
### 3. (Optional but recommended) Create a virtual environment:

<pre>python -m venv venv
source venv/bin/activate  
# macOS/Linux  
# venv\Scripts\activate   
# Windows</pre>

### 4. Install dependencies:

<pre>pip install openai</pre>
### 5. Set your OpenAI API key:

- #### macOS/Linux:
<pre>export OPENAI_API_KEY='your_key_here'</pre>
- #### Windows CMD  $env: 
<pre>set OPENAI_API_KEY=your_key_here</pre> 
- #### PowerShell
<pre>OPENAI_API_KEY="your_key_here"</pre>     

# 🛠️ Simulated NeuroCP Architecture
## 1. 🔗 Context Integration Layer (Simulated)
- In a full NeuroCP deployment, agents securely pull data from decentralized storage. Here, that’s emulated with local files:
context add --file <path> lets you assign a file to an agent.
- Named contexts help agents organize different data sets.
- You retain 100% control. Only selected context content is included with your OpenAI query – nothing else is shared or stored externally.

CLI Commands:

- `python neurocp.py context add <name> --file <path>`
- `python neurocp.py context use <name>`
- `python neurocp.py context show`
## 2. 🎯 Intent Recognition Layer (Simulated)
- This layer processes your input and identifies user intent. This is modeled via:
The ask "<query>" command
- Optional use of the OpenAI API to interpret and answer queries
- Lightweight prompt engineering to ensure relevance and context usage

CLI Command:

`python neurocp.py` ask "Your question here"

## 3. 🧠 AI Intelligence Layer (Simulated)
### The "thinking" engine. For now, this CLI uses gpt-3.5-turbo via OpenAI.

- All agent responses depend on the selected context
- The variable DEFAULT_AGENT_MODEL in the script serves as a placeholder
- Future NeuroCP agents will support fine-tuned and multi-model configurations

## 🤖 Agents in NeuroCP CLI
### An agent is a named configuration containing its own context space and behavior.

Agents are created using:
`python neurocp.py` agent create <name>
Switch between agents:

<pre>python neurocp.py agent use <name></pre>
Each agent has its own isolated contexts

All agent data is stored locally in neurocp_data.json

## ⌨️ CLI Command Overview
🧩 Agent Management:

- `python neurocp.py` agent create <agent_name>
- `python neurocp.py` agent use <agent_name>
- `python neurocp.py` agent list
- `python neurocp.py` agent delete <agent_name>

## 📂 Context Management (per agent):

- `python neurocp.py` context add <context_name> --file <path>
- `python neurocp.py` context use <context_name>
- `python neurocp.py` context show [--all]
- `python neurocp.py` context remove <context_name>

## 🧠 Ask a Question:
- `python neurocp.py` ask "Your question"

## 📊 Example Walkthrough
### Step 1: Create an Agent

- `python neurocp.py` agent create researcher

### Step 2: Add Context
Create a file called quantum_notes.txt with some content like:

Quantum entanglement describes the non-local correlation between particles. Einstein called it "spooky action at a distance."
Then run:

`python neurocp.py` context add entanglement --file ./quantum_notes.txt
### Step 3: Ask a Question

`python neurocp.py` ask "What did Einstein call quantum entanglement?"
You'll receive a contextualized answer, powered by your local file and OpenAI.

## 💡 Future Vision for NeuroCP
**This CLI is just the beginning. The long-term roadmap includes:**

- Decentralized and encrypted context storage
- Advanced, programmable intent engines
- Multi-model, self-hosted AI support
- Rich developer tools and SDKs
- Verifiable agent transparency and performance auditing
- This MVP is a glimpse into how NeuroCP will redefine agent-driven AI for decentralized, privacy-conscious applications.
