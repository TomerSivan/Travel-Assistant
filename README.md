# Travel Assistant
An intelligent travel assistant powered by **LangGraph**, **LangChain**, and **Ollama**.  
It helps you plan trips through natural conversation, including checking current weather, 
giving attraction suggestions, and offering personalized packing tips as its main queries.

---

## Powered by Travel APIs

This assistant integrates two public APIs to deliver accurate, real-time travel data:

### 🔶 OpenWeatherMap API
Used to retrieve:
- **Current weather** for any city
- **5-day weather forecasts** to help with trip planning and packing

API Website: https://openweathermap.org/api


### 🔷 OpenTripMap API
Used to retrieve:
- **Top-rated attractions** in any given city

API Website: https://dev.opentripmap.org/product

---

## How to Use
Follow these steps to get the Travel Assistant running on your machine.

### 1. Clone the Repository

```
git clone https://github.com/TomerSivan/Travel-Assistant
```

### 2. Install Dependencies
Ensure you are using Python 3.10+

```
pip install -r requirements.txt
```

### 3. Install Ollama and Pull a Model
Download Ollama from https://ollama.com and install it locally.
Then, in your terminal, pull a model (Recommended - qwen:4b, Has to support Langchain tools):

```
ollama pull qwen:4b
ollama run qwen:4b
```

### 4. Set Up Environment Variables
Create a .env file in the project root directory with your API keys and selected model:

```
CHAT_MODEL=Qwen3:4b
WEATHER_API_KEY=your_openweathermap_key
OPENTRIPMAP_API_KEY=your_opentripmap_key
```

### 5. Run the Assistant
And to finish up and start talking to the assistant chatbot via your terminal
use:

```
python main.py
```

Or directly run the main file.

---

## Supported Queries & Commands

The Travel Assistant supports natural language queries related to:

Query Type|Example Prompt|Details
-|-|-
Weather|`"What's the weather in Paris?"`|Uses the **OpenWeatherMap API** to retrieve either or both the current weather and a 5-day forecast. This data is integrated into the assistant’s natural language response.
Attractions|`"What are some places to visit in Rome?"`|Uses the **OpenTripMap API** to fetch top attractions for a city. Also calls the weather tool to tailor suggestions (e.g., avoid outdoor attractions if it's raining).
Packing Tips|`"What should I pack for a trip to Tokyo?"`|No single tool is used directly. Instead, the assistant internally calls both **weather** and **attractions** tools to suggest appropriate clothing, gear, and essentials.
Mixed Intent|`"I'm flying to London—what should I see and pack?"`|The assistant chains multiple tools (weather + attractions) and uses them together to provide detailed activity suggestions and overviews as well as a tailored packing list.

The assistant interprets user intent dynamically and will request needed information for tools.

The Travel Assistant supports user commands:

Command|Effect
-|-
"/exit"|Quit the assistant
"/debug"|Toggle debug output
"/think"|Toggle thought display
"/history"|Show full conversation
"/clear"|Clears up the history of the conversation
"/cmds"|List available commands

---

## LangGraph Workflow

The Travel Assistant uses a dynamic, tool-aware conversation loop built with **LangGraph**.

The graph consists of two main nodes and a simple routing condition:

**Nodes:**
- `assistant` – the core LLM node responsible for interpreting the user's message, reasoning, and generating tool calls (if needed).
- `tools` – executes any tools requested by the LLM (e.g. current weather, attractions, etc.) and updates the conversation state.

**Control Flow:**
1. ➤ Start at the `assistant` node.
2. ➤ The LLM interprets the user's message:
   - If tool calls are needed go to `tools`
   - If not end the conversation
3. ➤ The `tools` node executes tool calls and updates the state.
4. ➤ After tools are run, control returns to `assistant`.
5. ➤ This loop continues until no further tools are required.

Below is a simplified diagram of the Travel Assistant's LangGraph structure:
![LangGraph UML Diagram](Examples/langgraph_diagram.JPG)

### Why This Structure?

This setup ensures:
- There is a natural back and forth between reasoning and tools
- LLM re-evaluates its output with tool results
- Tools are only called when needed
- The loop exits cleanly once all goals are fulfilled