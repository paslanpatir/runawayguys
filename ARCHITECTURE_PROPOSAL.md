# Proposed Architecture Structure

## Current Structure (Flat)
```
src/
├── *.py (all files mixed together)
```

## Proposed Structure (Clean Architecture)

```
src/
├── ports/                    # Interfaces (contracts)
│   ├── __init__.py
│   ├── database_port.py      # Database interface
│   └── email_port.py         # Email interface
│
├── adapters/                 # External service implementations
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── dynamodb_adapter.py
│   │   ├── csv_adapter.py
│   │   └── database_handler.py  # Factory
│   └── email/
│       ├── __init__.py
│       └── email_adapter.py
│
├── infrastructure/           # Connection management, config
│   ├── __init__.py
│   ├── connection_manager.py      # AWS/DynamoDB
│   └── email_connection_manager.py
│
├── services/                 # Business logic (optional for now)
│   └── __init__.py
│
├── application/            # Application layer (main app components)
│   ├── __init__.py
│   ├── steps/               # All survey steps
│   │   ├── __init__.py
│   │   ├── base_step.py
│   │   ├── ask_language.py
│   │   ├── ask_user_details.py
│   │   ├── ask_boyfriend_name.py
│   │   ├── welcome.py
│   │   ├── filter_questions_step.py
│   │   ├── redflag_questions_step.py
│   │   ├── gtk_questions_step.py
│   │   ├── toxicity_opinion_step.py
│   │   ├── results_step.py
│   │   ├── feedback_step.py
│   │   ├── report_step.py
│   │   └── goodbye_step.py
│   ├── survey_controller.py
│   ├── progress_manager.py
│   ├── session_manager.py
│   └── messages.py
│
├── utils/                   # Utility functions
│   ├── __init__.py
│   └── utils.py
│
└── main.py                  # Entry point
```

## Benefits

1. **Separation of Concerns**: Clear boundaries between layers
2. **Testability**: Easy to mock ports for testing
3. **Maintainability**: Easy to find and modify code
4. **Scalability**: Easy to add new adapters (e.g., PostgreSQL, SendGrid)
5. **Dependency Inversion**: High-level code depends on abstractions (ports), not implementations

## Migration Plan

1. ✅ Create folder structure
2. ✅ Create ports (interfaces)
3. ✅ Move database adapters
4. ✅ Move email adapters
5. ✅ Move infrastructure
6. ✅ Move application layer (steps, controller, etc.)
7. ✅ Move utils
8. ✅ Update all imports
9. ⏳ Test (ready for testing)

