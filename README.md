# InfoFlow MCP Server

**Combat Information Overload and Decision Fatigue with AI-Powered Intelligence**

InfoFlow is a Model Context Protocol (MCP) server that helps users overcome information overload and decision fatigue through intelligent filtering, synthesis, and decision support. Built to integrate seamlessly with ChatGPT Custom GPTs and other AI assistants.

## 🎯 Problem Statement

In today's information-saturated world, people face:

- **Massive content volume** from articles, videos, forums, news making it difficult to filter and prioritize
- **Conflicting or low-quality sources** that complicate decision-making
- **Generic content** lacking personalized context or actionable next steps
- **Decision fatigue** from constant evaluation of options

### Why Traditional Solutions Fall Short

- Search engines and Q&A sites present large uncurated result sets
- Users must still filter and interpret everything themselves
- Most content lacks personalization or translation to actionable steps
- No adaptive learning from past decisions

## 🚀 How InfoFlow Solves This

InfoFlow acts as an **intelligent filter + synthesizer + decision assistant**:

1. **Smart Filtering**: Automatically filters content based on your interests and preferences
2. **Multi-Source Synthesis**: Combines information from multiple sources into coherent summaries
3. **Priority Ranking**: Assigns urgency levels to help you focus on what matters
4. **Decision Support**: Generates pros/cons analysis and recommendations
5. **Adaptive Learning**: Learns from your decisions to improve over time
6. **Proactive Monitoring**: Tracks topics and alerts you to relevant updates

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         Custom GPT / AI Assistant        │
│                                          │
│  "Help me decide which CRM to buy..."   │
└──────────────┬───────────────────────────┘
               │ MCP Protocol (JSON-RPC)
               │
┌──────────────▼───────────────────────────┐
│         InfoFlow MCP Server              │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  User Profile Manager              │ │
│  │  - Interests & Preferences         │ │
│  │  - Risk Tolerance                  │ │
│  │  - Decision Style                  │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Content Synthesizer               │ │
│  │  - Relevance Scoring               │ │
│  │  - Priority Determination          │ │
│  │  - Multi-Source Synthesis          │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Decision Engine                   │ │
│  │  - Pros/Cons Analysis              │ │
│  │  - Recommendations                 │ │
│  │  - Decision Tracking               │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Database (SQLite)                 │ │
│  │  - User Profiles                   │ │
│  │  - Decisions History               │ │
│  │  - Monitored Topics                │ │
│  └────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

## 🛠️ Features

### 1. User Profile Management
- Create personalized profiles with interests and preferences
- Set risk tolerance (low, medium, high)
- Define decision-making style (analytical, intuitive, collaborative)
- Customize notification thresholds

### 2. Intelligent Content Filtering
- Automatic relevance scoring based on your interests
- Priority levels: Critical, High, Medium, Low, Minimal
- Filter out noise and focus on what matters

### 3. Multi-Source Synthesis
- Combine information from multiple sources
- Generate coherent summaries
- Identify common themes and patterns
- Highlight conflicting information

### 4. Decision Support System
- Create structured decision frameworks
- Automatic pros/cons analysis
- Context-aware recommendations
- Track decision outcomes
- Learn from feedback

### 5. Proactive Monitoring
- Monitor specific topics for updates
- Keyword-based tracking
- Priority-based alerts
- Stay informed without being overwhelmed

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- ChatGPT Plus account (for Custom GPT integration)

## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

```bash
# Clone the repository
git clone https://github.com/vikkysarswat/infoflow-mcp-server.git
cd infoflow-mcp-server

# Run setup script
./setup.sh  # Linux/Mac
# OR
setup.bat   # Windows

# Start the server
python server.py
```

## 📖 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 5 minutes
- **[Custom GPT Instructions](custom_gpt_instructions.md)** - Set up your Custom GPT
- **[Usage Examples](examples/usage_examples.md)** - Real-world scenarios
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Changelog](CHANGELOG.md)** - Version history

## 🎮 Usage Examples

### Filter Information
```
User: I found 10 articles about AI trends but don't have time to read them all.

AI: [Filters by relevance to your interests]
- Article 1: HIGH PRIORITY (95% relevance)
- Article 2: MEDIUM PRIORITY (60% relevance)
- Articles 3-10: Below your threshold
```

### Make Decisions
```
User: Help me decide between Option A ($100, fast) and Option B ($200, better quality).

AI: [Creates structured analysis]
Pros/Cons analysis + Recommendation based on your risk tolerance
```

### Synthesize Research
```
User: Synthesize these 5 sources about remote work trends.

AI: [Combines sources]
Key themes, consensus points, contradictions, and actionable insights
```

See [Usage Examples](examples/usage_examples.md) for more!

## 🔧 Available Tools

- `create_user_profile` - Create/update user profile
- `filter_information` - Filter content by relevance
- `synthesize_information` - Combine multiple sources
- `create_decision` - Create structured decisions
- `update_decision` - Update decision status
- `get_decision_recommendation` - Get AI recommendations
- `monitor_topic` - Track topics for updates
- And more...

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

## 👥 Author

**Nilesh Vikky** - [vikkysarswat](https://github.com/vikkysarswat)

## 🙏 Acknowledgments

- Anthropic for the Model Context Protocol
- OpenAI for Custom GPT platform
- The open-source community

## 📧 Support

- 🐛 [Report Issues](https://github.com/vikkysarswat/infoflow-mcp-server/issues)
- 📧 Email: vikky.sarswat@gmail.com

---

**Built with ❤️ to help you make better decisions faster**

⭐ Star this repo if you find it useful!