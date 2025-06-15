"""
Enhanced Taipy display with sleek black background, white text, and red buttons
"""

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

# Enhanced page layout with black theme
page = """
<|layout|columns=350px 1|
<|part|render=True|class_name=sidebar|

# 🤖 **JARVIS**{: .color-primary} Assistant # {: .logo-text}

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
<|New Conversation|button|class_name=fullwidth control-btn|on_action=clear_conversation|>
<|Export History|button|class_name=fullwidth control-btn|on_action=export_conversation|>
<|Retrain Model|button|class_name=fullwidth control-btn|on_action=retrain_model|>
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

# Sleek black theme CSS
enhanced_css = """
/* Global Dark Theme */
* {
    box-sizing: border-box;
}

body {
    background-color: #000000 !important;
    color: #ffffff !important;
    font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    margin: 0;
    padding: 0;
    overflow: hidden;
}

/* Sidebar Styling */
.sidebar {
    background: linear-gradient(145deg, #1a1a1a, #0d0d0d) !important;
    color: #ffffff !important;
    padding: 25px;
    height: 100vh;
    overflow-y: auto;
    border-right: 2px solid #333333;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.5);
}

.logo-text {
    text-align: center;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 2px solid #dc3545;
    color: #ffffff !important;
    font-size: 1.3em;
    font-weight: bold;
}

.logo-text .color-primary {
    color: #dc3545 !important;
}

/* Section Styling */
.mode-section, .stats-section, .controls-section, .status-section {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid #333333;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 25px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.mode-section:hover, .stats-section:hover, .controls-section:hover, .status-section:hover {
    background: rgba(255, 255, 255, 0.08) !important;
    border-color: #dc3545;
}

/* Mode Indicator */
.mode-indicator {
    font-size: 18px !important;
    font-weight: bold !important;
    color: #00ff41 !important;
    text-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
}

/* Toggle Mode Button */
.mode-toggle {
    background: linear-gradient(135deg, #dc3545, #b02a37) !important;
    color: #ffffff !important;
    font-weight: bold !important;
    font-size: 16px !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 12px 20px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3) !important;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.mode-toggle:hover {
    background: linear-gradient(135deg, #e74c3c, #c0392b) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(220, 53, 69, 0.4) !important;
}

.mode-toggle:active {
    transform: translateY(0) !important;
    box-shadow: 0 2px 10px rgba(220, 53, 69, 0.3) !important;
}

/* Control Buttons */
.control-btn {
    background: linear-gradient(135deg, #dc3545, #b02a37) !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 16px !important;
    margin-bottom: 12px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 3px 10px rgba(220, 53, 69, 0.2) !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.control-btn:hover {
    background: linear-gradient(135deg, #e74c3c, #c0392b) !important;
    transform: translateX(5px) !important;
    box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3) !important;
}

.control-btn:active {
    transform: translateX(2px) !important;
    box-shadow: 0 2px 8px rgba(220, 53, 69, 0.2) !important;
}

/* Status Text */
.status-text {
    font-weight: bold !important;
    color: #00ff41 !important;
    font-size: 16px !important;
    text-shadow: 0 0 10px rgba(0, 255, 65, 0.3);
}

/* Chat Area */
.chat-area {
    background: #000000 !important;
    padding: 25px;
    height: 100vh;
    overflow-y: auto;
    border-left: 1px solid #333333;
}

/* Message Styling */
.gpt_message td {
    margin-left: 20px;
    margin-bottom: 15px;
    margin-top: 15px;
    position: relative;
    display: inline-block;
    padding: 18px 22px;
    background: linear-gradient(135deg, #2c2c2c, #1a1a1a) !important;
    border: 1px solid #404040;
    border-radius: 18px 18px 18px 4px;
    max-width: 80%;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    font-size: 15px !important;
    color: #ffffff !important;
    animation: slideInLeft 0.4s ease-out;
    line-height: 1.5;
}

.user_message td {
    margin-right: 20px;
    margin-bottom: 15px;
    margin-top: 15px;
    position: relative;
    display: inline-block;
    padding: 18px 22px;
    background: linear-gradient(135deg, #dc3545, #b02a37) !important;
    border-radius: 18px 18px 4px 18px;
    max-width: 80%;
    float: right;
    box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);
    font-size: 15px !important;
    color: #ffffff !important;
    animation: slideInRight 0.4s ease-out;
    line-height: 1.5;
}

.system_message td {
    margin: 15px auto;
    text-align: center;
    padding: 12px 24px;
    background: rgba(255, 193, 7, 0.15) !important;
    border: 1px solid rgba(255, 193, 7, 0.4);
    border-radius: 20px;
    color: #ffc107 !important;
    font-style: italic;
    font-weight: 500;
    max-width: 70%;
    animation: fadeIn 0.4s ease-out;
    box-shadow: 0 2px 10px rgba(255, 193, 7, 0.2);
}

/* Animations */
@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-40px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(40px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: scale(0.95);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

/* Scrollbar Styling */
::-webkit-scrollbar {
    width: 10px;
}

::-webkit-scrollbar-track {
    background: #1a1a1a;
    border-radius: 5px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #dc3545, #b02a37);
    border-radius: 5px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #e74c3c, #c0392b);
}

/* Table Styling */
table {
    background: transparent !important;
    border: none !important;
}

table td, table th {
    background: transparent !important;
    border: none !important;
    color: #ffffff !important;
}

/* Input and Select Styling */
input, select, textarea {
    background: #2c2c2c !important;
    color: #ffffff !important;
    border: 1px solid #404040 !important;
    border-radius: 6px !important;
    padding: 8px 12px !important;
}

input:focus, select:focus, textarea:focus {
    border-color: #dc3545 !important;
    box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.2) !important;
    outline: none !important;
}

/* Responsive Design */
@media (max-width: 768px) {
    .sidebar {
        width: 100% !important;
        height: auto !important;
        position: relative !important;
        border-right: none;
        border-bottom: 2px solid #333333;
    }
    
    .chat-area {
        height: 60vh !important;
        border-left: none;
        border-top: 1px solid #333333;
    }
    
    .user_message td, .gpt_message td {
        max-width: 90% !important;
    }
}

/* Additional Enhancements */
h1, h2, h3, h4, h5, h6 {
    color: #ffffff !important;
}

.fullwidth {
    width: 100% !important;
}

/* Loading Animation */
@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.4);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(220, 53, 69, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(220, 53, 69, 0);
    }
}

.mode-toggle.active {
    animation: pulse 2s infinite;
}
"""


def save_enhanced_css():
    """Save the enhanced CSS to a file"""
    Path("enhanced_display.css").write_text(enhanced_css)


# Ensure directories exist
Path("data").mkdir(exist_ok=True)
Path("exports").mkdir(exist_ok=True)

# Create GUI instance
gui = Gui(page, css_file="enhanced_display.css")

# Save CSS file
save_enhanced_css()

# Start background thread for updates
thread = Thread(target=client_handler, args=(gui, state_id_list))
thread.daemon = True
thread.start()

if __name__ == "__main__":
    gui.run(debug=True, dark_mode=True, port=5000, host="0.0.0.0")
