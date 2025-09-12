# 🎙️ MultiModal AI-Concierge

A **multimodal AI assistant** with a **human-like AI avatar**, built on [LiveKit](https://livekit.io/) for **real-time audio/video interaction**.  
It combines **LLMs, speech processing, memory, and tool integrations** to provide a **proactive, conversational, and task-oriented experience**.

## 🚀 Quick Start

```bash
# Clone the repository
git clone  https://github.com/OmkarGurav12/Multimodal-AI-Concierge.git
cd livekit-voice
```

---

## 🚀 Project Overview

The **LiveKit Voice Agent** is designed to act as a **personal AI concierge**. It doesn't just listen and respond — it can **see, hear, remember, search the web, manage your calendar, and even send emails on your behalf**.

The agent combines:
- 🎤 **Voice interaction** (STT + TTS)
- 🧑‍💻 **AI reasoning via LLMs**
- 🧠 **Persistent memory**
- 🌐 **Web search + productivity tools**
- 🧑‍🎤 **AI avatar for human-like presence**

This makes it a powerful foundation for **virtual assistants, customer support, and AI-driven productivity agents**.

---

## ✨ Key Features

- 🎙️ **Real-time audio/video** → Powered by **LiveKit** for low-latency communication
- 🧑‍💻 **AI brain (LLM)** → Backed by **OpenRouter** (multi-model API)
- 🎤 **Speech processing** → **Deepgram** for Speech-to-Text, **Cartesia** for Text-to-Speech
- 🧠 **Memory system** → **Mem0** for persistent conversational memory
- 🌐 **Web & Productivity Tools (MCP)** → via **Composio**:
  - Web search
  - Gmail (read, send, manage emails)
  - Google Calendar (create, update, delete events)
- 🧑‍🎤 **AI Avatar** → **Tavus.ai** for a human-like, talking AI presence
- ⚡ **Frontend UI** → Built with **Next.js** and **@livekit/components-react**

---

## 🛠️ Services & Integrations

| Category            | Service / Library | Purpose |
|---------------------|------------------|---------|
| **Real-time Infra** | [LiveKit](https://livekit.io/) | Audio/video communication |
| **LLM Backbone**    | [OpenRouter](https://openrouter.ai/) | Access to multiple large language models |
| **Speech-to-Text**  | [Deepgram](https://deepgram.com/) | Convert voice input to text |
| **Text-to-Speech**  | [Cartesia](https://cartesia.ai/) | Convert AI responses to natural voice |
| **Memory**          | [Mem0](https://mem0.ai/) | Persistent conversational memory |
| **MCP Integrations**| [Composio](https://composio.dev/) | Web search, Gmail, Calendar tools |
| **Avatar**          | [Tavus.ai](https://tavus.io/) | Human-like AI avatar for interactions |
| **Frontend**        | Next.js + @livekit/components-react | Modern UI for agent interaction |


---

## 📂 Project Structure

```
livekit-voice/                    # Root project directory
├── .env                         # Environment variables
├── .env.example                 # Example environment file
├── .gitignore                   # Git ignore rules
├── pyproject.toml               # Python dependencies & settings
├── uv.lock                      # Lockfile (for uv / pip-tools)
├── README.md                    # Project documentation
├── exp.py                       # Experimental scripts / testing
├── single_demo.py               # Standalone demo script
├── agent-starter-react/         # Next.js frontend (UI for AI assistant)
│   ├── app/                     # Application pages & logic
│   └── components/              # React UI components
└── backend/                     # FastAPI backend
    ├── __init__.py              # Marks backend as a package
    ├── agent.py                 # AI agent logic
    ├── config.py                # Configurations & environment loading
    ├── main.py                  # Entry point (backend server)
    ├── mcp_handler.py           # Handles MCP tools & connections
    └── memory_handler.py        # Memory storage & retrieval
```

---

## ✅ Prerequisites

Before starting, ensure you have the following installed:

- **Python** → `3.10+`
- **Node.js** → `18+`
- **npm** → (comes with Node.js)
- **uv** → Python package/dependency manager ([install guide](https://github.com/astral-sh/uv))
- **LiveKit CLI** → Required for local/cloud LiveKit setup ([docs](https://docs.livekit.io/))
- **Git** → For cloning the repository

---

## ⚙️ Setup & Implementation Guide

Follow these steps to set up and run the **LiveKit Voice Agent**:

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-repo/livekit-voice.git
cd livekit-voice
```

### 2️⃣ Backend Setup

🔹 **Create Virtual Environment (using uv)**

```bash
uv venv .venv
source .venv/bin/activate   # Linux / macOS
# OR
.venv\Scripts\activate      # Windows
```

🔹 **Install Dependencies**

```bash
uv sync
```

🔹 **Configure Environment Variables**

```bash
# Copy example file
cp .env.example .env
```

Add all necessary API keys to `.env`:

```bash
# LiveKit Configuration
LIVEKIT_URL=wss://your-livekit-url
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret

# OpenRouter (LLM)
OPENROUTER_API_KEY=your-openrouter-api-key

# Speech Services
DEEPGRAM_API_KEY=your-deepgram-api-key
CARTESIA_API_KEY=your-cartesia-api-key

# Memory & Tools
MEM0_API_KEY=your-mem0-api-key
COMPOSIO_API_KEY=your-composio-api-key

# Avatar
TAVUS_API_KEY=your-tavus-api-key
TAVUS_PERSONA_ID=your-persona-id
TAVUS_REPLICA_ID=your-replica-id
```

🔹 **Tavus.ai Avatar Setup**

1. Create your avatar on [Tavus.ai](https://tavus.io/)
2. Copy the generated `persona_id` and `replica_id`
3. Add them to your `.env` file or `backend/config.py`

🔹 **Install LiveKit CLI**

Follow the [LiveKit CLI installation guide](https://docs.livekit.io/)

🔹 **Run Backend (Dev Mode)**

```bash
python -m backend.main dev
```

### 3️⃣ Frontend Setup

```bash
cd agent-starter-react
```

🔹 **Configure Environment Variables**

```bash
# Copy example file
cp .env.example .env.local
```

Add **LiveKit credentials** to `.env.local`:

```bash
NEXT_PUBLIC_LIVEKIT_URL=wss://your-livekit-url
LIVEKIT_API_KEY=your-livekit-api-key
LIVEKIT_API_SECRET=your-livekit-api-secret
```

🔹 **Install Dependencies**

```bash
npm install
```

🔹 **Run Frontend**

```bash
npm run dev
```

### 4️⃣ Final Step

- Ensure **both backend & frontend servers** are running
- Open the app in your browser: 👉 **http://localhost:3000**

You are now ready to interact with your **AI-powered LiveKit Voice Agent** 🎙️🤖

---

## 🚀 Usage

1. **Start a conversation** by clicking the microphone button
2. **Speak naturally** - the agent will listen and respond with voice
3. **Ask for help** with tasks like:
   - "Search the web for latest AI news"
   - "Schedule a meeting for tomorrow at 2 PM"
   - "Send an email to john@example.com about the project update"
   - "What did we discuss last week?"

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-repo/multimodal-ai-concierge/issues) page
2. Create a new issue with detailed description


---

## 🔥 Why MCP (Model Context Protocol)?

**MCP is revolutionizing how AI agents interact with tools!** 🚀

- **🌐 Universal Standard** → One protocol to rule all AI tool integrations
- **🔧 Modular Architecture** → Plug-and-play tool ecosystem
- **⚡ Real-time Communication** → Direct, efficient tool access
- **🛡️ Secure & Sandboxed** → Safe execution environment
- **📈 Future-Proof** → The industry is moving towards MCP as the standard

Our custom MCP implementation showcases the **next generation of AI tooling** - making your concierge truly intelligent and capable!