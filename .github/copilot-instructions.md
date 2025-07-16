<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# Roblox Garden Parser - Copilot Instructions

This is a Python project for parsing Roblox Garden WebSocket data with Telegram bot integration.

## Project Context

- **Language**: Python 3.11+
- **Architecture**: Asynchronous, event-driven
- **Main Libraries**: asyncio, websockets, python-telegram-bot, pydantic
- **Purpose**: Monitor Roblox Garden shop and send filtered updates to Telegram channels

## Code Style Guidelines

- Use **async/await** patterns for all I/O operations
- Implement **type hints** for all functions and classes
- Use **Pydantic models** for data validation
- Follow **PEP 8** naming conventions
- Use **dependency injection** for better testability

## Key Components

1. **WebSocket Client** - Connects to Roblox Garden API
2. **Telegram Bot** - Sends messages to channels
3. **Item Filters** - Filters items by rarity and type
4. **Message Formatters** - Creates structured Telegram messages
5. **Configuration Management** - Handles environment variables

## Filtering Rules

### Seeds & Gears
- **Include**: Divine rarity and higher
- **Exclude**: "Harvest Tool", "Favorite Tool", "Cleaning Spray"

### Eggs
- **Include only**: "Bee Egg", "Paradise Egg", "Bug Egg", "Mythical Egg"

## Message Formats

- Use emojis: 🌱 for seeds, ⚙️ for gears, 🥚 for eggs
- Include rarity in brackets: [Divine], [Mythical]
- Add status indicators: ✅ В наличии, ❌ Отсутствует

## Error Handling

- Implement graceful WebSocket reconnection
- Add retry logic for Telegram API calls
- Log all errors with context
- Never crash on single item processing failure

## Testing

- Write unit tests for all filters
- Mock external API calls
- Test message formatting
- Verify configuration loading
