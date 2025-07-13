import argparse
import json
import os
import sys
import re  # For regular expression matching
from openai import OpenAI  # Added for OpenAI API

# --- Constants ---
DATA_FILE = "neurocp_data.json"
DEFAULT_AGENT_MODEL = "default_mock_v1"  # Placeholder for agent model type
OPENAI_MODEL = "gpt-4o"  # Default OpenAI model

# --- Data Management Functions ---
def load_data():
    default_structure = {"agents": {}, "active_agent": None}
    if not os.path.exists(DATA_FILE):
        return default_structure
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            if not content:
                return default_structure
            return json.loads(content)
    except json.JSONDecodeError:
        print(f"Error: {DATA_FILE} is corrupted or not valid JSON. ", end="")
        print("A new empty data structure will be used. Previous data might be lost if not backed up.")
        return default_structure
    except FileNotFoundError:
        return default_structure

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"Error: Could not write to data file {DATA_FILE}: {e}")

# --- Helper Functions ---
def get_active_agent_name_or_exit(data):
    active_agent_name = data.get("active_agent")
    if not active_agent_name:
        print("Error: No active agent set. Use 'python neurocp.py agent use <agent_name>' to set one.")
        sys.exit(1)
    if active_agent_name not in data.get("agents", {}):
        print(f"Error: Active agent '{active_agent_name}' is configured but not found.")
        print("The data file may be corrupted. Try setting an existing agent as active again.")
        sys.exit(1)
    return active_agent_name

def get_agent_or_exit(data, agent_name):
    agents_data = data.get("agents", {})
    if agent_name not in agents_data:
        print(f"Error: Agent '{agent_name}' not found.")
        sys.exit(1)
    return agents_data[agent_name]

# --- Agent Command Functions ---
def agent_create(args):
    data = load_data()
    agent_name = args.agent_name
    if "agents" not in data:
        data["agents"] = {}
    if agent_name in data["agents"]:
        print(f"Error: Agent '{agent_name}' already exists.")
        return
    data["agents"][agent_name] = {"model": DEFAULT_AGENT_MODEL, "current_context_name": None, "contexts": {}}
    if not data.get("active_agent") or not data["agents"]:
        data["active_agent"] = agent_name
        print(f"Agent '{agent_name}' created and set as active.")
    else:
        print(f"Agent '{agent_name}' created.")
    save_data(data)

def agent_list(args):
    data = load_data()
    active_agent_name = data.get("active_agent")
    agents = data.get("agents", {})
    if not agents:
        print("No agents created yet. Use 'python neurocp.py agent create <agent_name>'.")
        return
    print("Available Agents:")
    for name in sorted(agents.keys()):
        marker = " (*)" if name == active_agent_name else ""
        print(f"- {name}{marker}")
    if active_agent_name:
        print("\n(*) indicates the active agent.")
    elif agents:
        print("\nNo agent is currently active. Use 'python neurocp.py agent use <agent_name>' to activate one.")

def agent_use(args):
    data = load_data()
    agent_name = args.agent_name
    if agent_name not in data.get("agents", {}):
        print(f"Error: Agent '{agent_name}' not found.")
        return
    data["active_agent"] = agent_name
    save_data(data)
    print(f"Agent '{agent_name}' is now active.")

def agent_delete(args):
    data = load_data()
    agent_name = args.agent_name
    if agent_name not in data.get("agents", {}):
        print(f"Error: Agent '{agent_name}' not found.")
        return
    del data["agents"][agent_name]
    print(f"Agent '{agent_name}' deleted.")
    if data.get("active_agent") == agent_name:
        data["active_agent"] = None
        print("The deleted agent was active. No agent is active now.")
        if data["agents"]:
            new_active = next(iter(data["agents"]))
            data["active_agent"] = new_active
            print(f"Agent '{new_active}' has been automatically set as active.")
    save_data(data)

# --- Context Command Functions ---
def context_add(args):
    data = load_data()
    active_agent = get_active_agent_name_or_exit(data)
    agent = data["agents"][active_agent]
    context_name, file_path = args.context_name, args.file
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return
    if not os.path.isfile(file_path):
        print(f"Error: '{file_path}' is not a valid file.")
        return
    abs_path = os.path.abspath(file_path)
    agent["contexts"][context_name] = abs_path
    agent["current_context_name"] = context_name
    save_data(data)
    print(f"Context '{context_name}' from '{abs_path}' added and activated for agent '{active_agent}'.")

def context_use(args):
    data = load_data()
    active_agent = get_active_agent_name_or_exit(data)
    agent = data["agents"][active_agent]
    context_name = args.context_name
    if context_name not in agent.get("contexts", {}):
        print(f"Error: Context '{context_name}' not found for agent '{active_agent}'.")
        available = list(agent.get("contexts", {}).keys())
        if available:
            print("Available contexts:", ", ".join(available))
        else:
            print("This agent has no contexts yet. Use 'python neurocp.py context add ...'.")
        return
    agent["current_context_name"] = context_name
    save_data(data)
    print(f"Context '{context_name}' is now active for agent '{active_agent}'.")

def context_show(args):
    data = load_data()
    active_agent = get_active_agent_name_or_exit(data)
    agent = data["agents"][active_agent]
    if args.all:
        contexts = agent.get("contexts", {})
        if not contexts:
            print(f"No contexts defined for agent '{active_agent}'.")
            return
        print(f"Contexts for agent '{active_agent}':")
        for name, path in sorted(contexts.items()):
            marker = " (*)" if name == agent.get("current_context_name") else ""
            print(f"- {name} (Path: {path}){marker}")
        if agent.get("current_context_name"):
            print("\n(*) indicates the active context.")
    else:
        current = agent.get("current_context_name")
        if not current:
            print(f"No active context for agent '{active_agent}'. Use '--all' to see all.")
            return
        path = agent["contexts"].get(current)
        if not path:
            print(f"Error: Path for active context '{current}' not found.")
            return
        print(f"Active context for agent '{active_agent}':\n  Name: {current}\n  Path: {path}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                snippet = f.read(200)
                print(f"  Snippet: \"{snippet}{'...' if len(snippet) == 200 else ''}\"")
        except Exception as e:
            print(f"Warning: Could not read context file '{path}': {e}")

def context_remove(args):
    data = load_data()
    active_agent = get_active_agent_name_or_exit(data)
    agent = data["agents"][active_agent]
    name = args.context_name
    if name not in agent.get("contexts", {}):
        print(f"Error: Context '{name}' not found.")
        return
    del agent["contexts"][name]
    print(f"Context '{name}' removed from agent '{active_agent}'.")
    if agent.get("current_context_name") == name:
        agent["current_context_name"] = None
        print("The removed context was active. No active context now.")
    save_data(data)

# --- Ask Command (OpenAI Integration) ---
def ask(args):
    data = load_data()
    active_agent = get_active_agent_name_or_exit(data)
    query = args.query

    context = None
    context_label = "no active context"
    context_name = data["agents"][active_agent].get("current_context_name")

    if context_name:
        context_path = data["agents"][active_agent]["contexts"].get(context_name)
        if context_path and os.path.exists(context_path):
            try:
                with open(context_path, "r", encoding="utf-8") as f:
                    context = f.read(10000)
                context_label = f"context '{context_name}'"
                if len(context) == 10000:
                    print("Warning: Context too large, truncated to first 10000 characters.")
            except Exception as e:
                print(f"Warning: Could not read context file '{context_path}': {e}")
                context = None
        elif context_path:
            print(f"Warning: File '{context_path}' not found. Skipping context.")
            context = None

    # OpenAI API interaction
    response = "Could not retrieve an answer."
    system_msg = "You are a helpful assistant. Answer the user's question."
    prompt = f"Question: {query}"

    if context:
        system_msg = "You are a helpful assistant. Answer based only on the provided context. If unavailable, say so."
        prompt = f"Context:\n---\n{context}\n---\n\nQuestion: {query}"

    print(f"\nQuerying OpenAI ({OPENAI_MODEL})...")

    try:
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OPENAI_API_KEY environment variable not set.")

        client = OpenAI()

        completion = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ]
        )
        if completion.choices and completion.choices[0].message:
            response = completion.choices[0].message.content
        else:
            response = "OpenAI API returned an empty response."
    except Exception as e:
        response = f"OpenAI API Error: {e}"
        if "OPENAI_API_KEY" not in os.environ:
            response += "\nMake sure OPENAI_API_KEY is set in your environment."

    print(f"Agent '{active_agent}' (using {context_label} via OpenAI):\n  Query: \"{query}\"\n  Answer: {response}")

# --- Main Parser ---
def main():
    parser = argparse.ArgumentParser(prog="neurocp", description="NeuroCP AI CLI", epilog="Example: python neurocp.py agent create my_agent")
    subparsers = parser.add_subparsers(dest="command_group", title="Command groups", required=True)

    agent_parser = subparsers.add_parser("agent", help="Agent management")
    agent_subparsers = agent_parser.add_subparsers(dest="agent_action", title="Agent actions", required=True)
    agent_subparsers.add_parser("list", help="List agents").set_defaults(func=agent_list)
    agent_create = agent_subparsers.add_parser("create", help="Create agent")
    agent_create.add_argument("agent_name")
    agent_create.set_defaults(func=agent_create)
    agent_use = agent_subparsers.add_parser("use", help="Set active agent")
    agent_use.add_argument("agent_name")
    agent_use.set_defaults(func=agent_use)
    agent_delete = agent_subparsers.add_parser("delete", help="Delete agent")
    agent_delete.add_argument("agent_name")
    agent_delete.set_defaults(func=agent_delete)

    context_parser = subparsers.add_parser("context", help="Context management")
    context_subparsers = context_parser.add_subparsers(dest="context_action", title="Context actions", required=True)
    context_add = context_subparsers.add_parser("add", help="Add context")
    context_add.add_argument("context_name")
    context_add.add_argument("--file", required=True)
    context_add.set_defaults(func=context_add)
    context_use = context_subparsers.add_parser("use", help="Use context")
    context_use.add_argument("context_name")
    context_use.set_defaults(func=context_use)
    context_show = context_subparsers.add_parser("show", help="Show context(s)")
    context_show.add_argument("--all", action="store_true")
    context_show.set_defaults(func=context_show)
    context_remove = context_subparsers.add_parser("remove", help="Remove context")
    context_remove.add_argument("context_name")
    context_remove.set_defaults(func=context_remove)

    ask = subparsers.add_parser("ask", help="Ask OpenAI")
    ask.add_argument("query")
    ask.set_defaults(func=ask)

    args = parser.parse_args()
    if hasattr(args, "func") and callable(args.func):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
