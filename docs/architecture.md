# TermGame Architecture

## Overview

TermGame follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────┐
│            User Interface Layer              │
│  ┌──────────────┐      ┌──────────────┐    │
│  │  CLI (Typer) │      │  TUI (Textual)│    │
│  └──────────────┘      └──────────────┘    │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│           Application Layer                  │
│  ┌──────────────┐      ┌──────────────┐    │
│  │ Mission Engine│      │    Coach     │    │
│  └──────────────┘      └──────────────┘    │
└─────────────────────────────────────────────┘
                    │
┌─────────────────────────────────────────────┐
│          Infrastructure Layer                │
│  ┌──────────────┐  ┌──────────┐  ┌───────┐ │
│  │   Runtimes   │  │ Matchers │  │   DB  │ │
│  └──────────────┘  └──────────┘  └───────┘ │
└─────────────────────────────────────────────┘
```

## Components

### User Interface Layer

#### CLI (Typer)
- Command-line interface for quick actions
- Mission management
- Progress tracking

#### TUI (Textual)
- Full-screen terminal interface
- Rich, interactive experience
- Mission navigation and execution

### Application Layer

#### Mission Engine
- Core game logic
- State management
- Mission progression
- Validation orchestration

#### Coach
- AI-powered hints
- Contextual guidance
- Learning path recommendations

### Infrastructure Layer

#### Runtimes
- Container abstraction (Docker/Podman)
- Sandbox lifecycle management
- Command execution

#### Matchers
- Output validation
- Command verification
- File system checks

#### Database
- User progress tracking
- Achievement storage
- Mission history

## Data Flow

1. User initiates mission via CLI/TUI
2. Mission Engine loads scenario YAML
3. Runtime creates isolated container
4. User executes commands
5. Matchers validate outputs
6. Engine updates progress
7. Database persists state
8. Coach provides hints if needed

## Design Principles

- **Modularity**: Clear component boundaries
- **Testability**: Dependency injection, protocols
- **Extensibility**: Plugin architecture for matchers
- **Security**: Isolated sandboxes, input validation
- **Performance**: Async I/O, resource management

## Technology Choices

- **Python 3.12+**: Modern Python features
- **Textual**: Rich TUI framework
- **Typer**: Type-safe CLI
- **Pydantic**: Data validation
- **SQLAlchemy**: Database ORM
- **Docker SDK**: Container management

## Future Enhancements

- [ ] Multi-user support
- [ ] Leaderboards
- [ ] Custom scenario editor
- [ ] Plugin system for custom matchers
- [ ] Web dashboard
