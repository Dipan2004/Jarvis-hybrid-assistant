

import time
import json
from threading import Thread
from pathlib import Path
from taipy.gui import Gui, State, invoke_callback, get_state_id, Markdown

# Initialize variables
conversation = {"Conversation": []}
state_id_list = []
selected_row = [1]
status = "Idle"
is_online = True
total_conversations = 0
offline_commands_count = 0
ml_accuracy = 0.0
conversation_history = []

def on_init(state: State) -> None:
    """Initialize the application state"""
    state_id = get_state_id(state)
    state_id_list.append(state_id)
    
    # Load initial data
    state.is_online = True
    state.total_conversations = 0
    state.offline_commands_count = 0
    state.ml_accuracy = 0.0
    
    # Load conversation history if available
    try:
        with open("data/conversation_history.json", "r") as f:
            state.conversation_history = json.load(f)
            state.total_conversations = len(state.conversation_history)
            state.offline_commands_count = sum(1 for conv in state.conversation_history if conv.get('mode') == 'offline')
    except FileNotFoundError:
        state.conversation_history = []

def client_handler(gui: Gui, state_id_list: list) -> None:
    """Background thread to update the interface"""
    while True:
        time.sleep(0.5)
        if len(state_id_list) > 0:
            invoke_callback(gui, state_id_list[0], update_interface, [])

def update_interface(state: State) -> None:
    """Update the conversation and status"""
    # Update status
    try:
        with open("status.txt", "r") as f:
            new_status = f.read().strip()
        if new_status != state.status:
            state.status = new_status
    except FileNotFoundError:
        pass
    
    # Update conversation
    try:
        with open("conv.txt", "r") as f:
            conv_text = f.read().strip()
        if conv_text:
            conv_lines = conv_text.split("\n")
            conv_data = [line for line in conv_lines if line.strip()]
            
            if conv_data != conversation.get("Conversation", []):
                conversation["Conversation"] = conv_data
                state.conversation = conversation
                state.selected_row = [len(conv_data) - 1] if conv_data else [0]
    except FileNotFoundError:
        pass
    
    # Update statistics
    try:
        with open("data/conversation_history.json", "r") as f:
            history = json.load(f)
            state.total_conversations = len(history)
            state.offline_commands_count = sum(1 for conv in history if conv.get('mode') == 'offline')
            
            # Calculate ML accuracy (mock calculation)
            if state.offline_commands_count > 0:
                state.ml_accuracy = min(95.0, 70.0 + (state.offline_commands_count * 2))
            else:
                state.ml_accuracy = 0.0
    except FileNotFoundError:
        pass

def toggle_mode(state: State) -> None:
    """Toggle between online and offline modes"""
    # Write toggle command to a file that the main assistant can read
    with open("mode_toggle.txt", "w") as f:
        f.write("toggle")
    
    state.is_online = not state.is_online
    mode_text = "Online" if state.is_online else "Offline"
    
    # Add system message to conversation
    with open("conv.txt", "a") as f:
        f.write(f"System: Switched to {mode_text} mode\n")

def clear_conversation(state: State) -> None:
    """Clear the conversation history"""
    try:
        with open("conv.txt", "w") as f:
            f.write("")
        conversation["Conversation"] = []
        state.conversation = conversation
        state.selected_row = [0]
    except Exception as e:
        print(f"Error clearing conversation: {e}")

def export_conversation(state: State) -> None:
    """Export conversation history"""
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_export_{timestamp}.json"
        
        with open(f"exports/{filename}", "w") as f:
            json.dump(state.conversation_history, f, indent=2)
            
        # Add confirmation to conversation
        with open("conv.txt", "a") as f:
            f.write(f"System: Conversation exported to {filename}\n")
    except Exception as e:
        print(f"Error exporting conversation: {e}")

def retrain_model(state: State) -> None:
    """Trigger model retraining"""
    with open("retrain_model.txt", "w") as f:
        f.write("retrain")
    
    # Add system message
    with open("conv.txt", "a") as f:
        f.write("System: Retraining ML model with latest conversations...\n")

def style_conv(state: State, idx: int, row: int) -> str:
    """Style conversation messages"""
    if idx is None:
        return None
    
    # Get the message text
    try:
        message = state.conversation["Conversation"][idx]
        if message.startswith("System:"):
            return "system_message"
        elif idx % 2 == 0:
            return "user_message"
        else:
            return "gpt_message"
    except (IndexError, KeyError):
        return None

# Enhanced page layout with more features
page = """
<|layout|columns=350px 1|
<|part|render=True|class_name=sidebar|

# 🤖 **JARVIS**{: .color-primary} Hybrid # {: .logo-text}

## Mode Control
<|part|render=True|class_name=mode-section|
**Current Mode:** <|{"🌐 Online" if is_online else "💻 Offline"}|text|class_name=mode-indicator|>

<|Toggle Mode|button|class_name=fullwidth mode-toggle|on_action=toggle_mode|>
|>

## Statistics
<|part|render=True|class_name=stats-section|
**Total Conversations:** <|{total_conversations}|text|>
**Offline Commands:** <|{offline_commands_count}|text|>
**ML Accuracy:** <|{f"{ml_accuracy:.1f}%"}|text|>
|>

## Controls
<|part|render=True|class_name=controls-section|
<|New Conversation|button|class_name=fullwidth plain|on_action=clear_conversation|>
<|Export History|button|class_name=fullwidth plain|on_action=export_conversation|>
<|Retrain Model|button|class_name=fullwidth plain|on_action=retrain_model|>
|>

## Status
<|part|render=True|class_name=status-section|
**Status:** <|{status}|text|class_name=status-text|>
|>

|>

<|part|render=True|class_name=chat-area|
<|{conversation}|table|style=style_conv|show_all|width=100%|rebuild|selected={selected_row}|>
|>
|>
"""

# Enhanced CSS for the new interface
enhanced_css = """
body {
    overflow: hidden;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.sidebar {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: white;
    padding: 20px;
    height: 100vh;
    overflow-y: auto;
}

.logo-text {
    text-align: center;
    margin-bottom: 30px;
    border-bottom: 2px solid rgba(255, 255, 255, 0.3);
    padding-bottom: 15px;
}

.mode-section, .stats-section, .controls-section, .status-section {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 20px;
    backdrop-filter: blur(10px);
}

.mode-indicator {
    font-size: 18px;
    font-weight: bold;
    color: #4CAF50;
}

.mode-toggle {
    background: linear-gradient(45deg, #FF6B6B, #4ECDC4) !important;
    color: white !important;
    border: none !important;
    transition: all 0.3s ease !important;
}

.mode-toggle:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 5px 15px rgba(0,0,0,0.3) !important;
}

.stats-section h3 {
    margin-top: 0;
}

.controls-section button {
    margin-bottom: 10px !important;
    background: rgba(255, 255, 255, 0.2) !important;
    color: white !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    transition: all 0.3s ease !important;
}

.controls-section button:hover {
    background: rgba(255, 255, 255, 0.3) !important;
    transform: translateX(5px) !important;
}

.status-text {
    font-weight: bold;
    color: #FFD700;
}

.chat-area {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    height: 100vh;
    overflow-y: auto;
}

.gpt_message td {
    margin-left: 30px;
    margin-bottom: 20px;
    margin-top: 20px;
    position: relative;
    display: inline-block;
    padding: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px 20px 20px 5px;
    max-width: 80%;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    font-size: large;
    color: white;
    animation: slideInLeft 0.5s ease-out;
}

.user_message td {
    margin-right: 30px;
    margin-bottom: 20px;
    margin-top: 20px;
    position: relative;
    display: inline-block;
    padding: 20px;
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    border-radius: 20px 20px 5px 20px;
    max-width: 80%;
    float: right;
    box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(255, 255, 255, 0.18);
    font-size: large;
    color: white;
    animation: slideInRight 0.5s ease-out;
}

.system_message td {
    margin: 10px auto;
    text-align: center;
    padding: 10px 20px;
    background: rgba(255, 193, 7, 0.2);
    border-radius: 15px;
    border: 1px solid rgba(255, 193, 7, 0.5);
    color: #FFC107;
    font-style: italic;
    max-width: 60%;
    animation: fadeIn 0.5s ease-out;
}

@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-50px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(50px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: scale(0.9);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

/* Scrollbar styling */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.5);
}

/* Responsive design */
@media (max-width: 768px) {
    .sidebar {
        width: 100% !important;
        height: auto !important;
        position: relative !important;
    }
    
    .chat-area {
        height: 60vh !important;
    }
}
"""


def save_enhanced_css():
    """Save the enhanced CSS to a file"""
    Path("enhanced_display.css").write_text(enhanced_css)


Path("data").mkdir(exist_ok=True)
Path("exports").mkdir(exist_ok=True)


gui = Gui(page, css_file="enhanced_display.css")


save_enhanced_css()


thread = Thread(target=client_handler, args=(gui, state_id_list))
thread.daemon = True
thread.start()

if __name__ == "__main__":
    gui.run(debug=True, dark_mode=True, port=5000, host="0.0.0.0")
