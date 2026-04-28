# Voice Assistant Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│               Voice Assistant System                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────┐  │
│  │  Microphone    │  │  Wake Word     │  │  Speech     │  │
│  │   Input        │→ │  Detector      │→ │Recognition  │  │
│  └────────────────┘  └────────────────┘  └─────────────┘  │
│                                              ↓             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          NLP Processor (GPT-4)                      │  │
│  │  Input: User voice text                             │  │
│  │  Output: Structured JSON command                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       Sandbox & Confirmation Gate                   │  │
│  │  • Check action safety                              │  │
│  │  • Request confirmation if risky                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                │
│      ┌────────────────────┬────────────────────┐          │
│      ↓                    ↓                    ↓          │
│  ┌─────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │   Command   │  │   Code           │  │  Other       │ │
│  │  Executor   │  │   Generator      │  │  Operations  │ │
│  └─────────────┘  └──────────────────┘  └──────────────┘ │
│      ↓                    ↓                    ↓          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │    Context Memory & Logging                         │  │
│  │  • Store command history                            │  │
│  │  • Track execution stats                            │  │
│  │  • Persistent session storage                       │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       Text-to-Speech Response                       │  │
│  │  "Command executed successfully"                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Module Descriptions

### 1. Speech Recognition Module
**File:** `modules/speech_recognition.py`

- Captures real-time microphone input
- Uses OpenAI Whisper for speech-to-text
- Supports 90+ languages
- Handles audio file transcription

**Key Classes:**
- `SpeechRecognizer`: Main recognition engine

### 2. NLP Processor Module
**File:** `modules/nlp_processor.py`

- Converts natural language to structured commands
- Uses GPT-4 for intent understanding
- Maintains conversation context
- Parses JSON responses

**Key Classes:**
- `NLPProcessor`: Intent parsing engine

### 3. Command Executor Module
**File:** `modules/command_executor.py`

- Executes system-level operations
- Supported actions:
  - `open_folder`: File explorer operations
  - `create_project`: Project scaffolding
  - `write_code`: Save code to files
  - `run_code`: Execute Python scripts
  - `execute_system`: Shell commands
  - `exit`: Shutdown

**Key Classes:**
- `CommandExecutor`: Command execution engine

### 4. Code Generator Module
**File:** `modules/code_generator.py`

- Generates code using GPT-4
- Supports 6 languages: Python, Java, JavaScript, Bash, C++, C
- Auto-formatting and saving
- Unit test generation

**Key Classes:**
- `CodeGenerator`: Code generation engine

### 5. Text-to-Speech Module
**File:** `modules/text_to_speech.py`

- Converts text to voice using pyttsx3
- Configurable voices and rates
- Async speech support
- Audio file export

**Key Classes:**
- `TextToSpeech`: Voice output engine

### 6. Advanced Features Module
**File:** `modules/advanced_features.py`

#### Wake Word Detection
- Exact and fuzzy matching
- Configurable sensitivity
- Detection statistics tracking

#### Context Memory
- Command history storage (max 10)
- Persistent JSON storage
- Session summaries
- Search capabilities

#### Sandbox Mode
- Action whitelisting
- Risk assessment
- User confirmation
- Execution logging

**Key Classes:**
- `WakeWordDetector`: Wake word recognition
- `ContextMemory`: Session history tracking
- `SandboxExecutor`: Safe command execution

## Data Flow

### Command Processing Pipeline
```
User Voice Input
    ↓
Wake Word Detection (Optional Filter)
    ↓
Speech Recognition (Whisper)
    ↓
NLP Processing (GPT-4)
    ↓
JSON Command Output
    ├─ action: string
    ├─ parameters: dict
    └─ reasoning: string
    ↓
Sandbox Validation
    ├─ Check safety
    ├─ Request confirmation (if risky)
    └─ Log execution
    ↓
Command Execution
    ↓
Context Memory Update
    ↓
Text-to-Speech Response
```

## Configuration

All settings are in `config/config.yaml`:

```yaml
openai:
  api_key: "your-key"
  model: "gpt-4"

audio:
  sample_rate: 16000
  chunk_size: 1024

speech_recognition:
  engine: "whisper"
  model_size: "base"

text_to_speech:
  engine: "pyttsx3"
  rate: 150

wake_word:
  enabled: true
  phrase: "hey assistant"
  sensitivity: 0.5

logging:
  level: "INFO"
  file: "logs/assistant.log"

session:
  context_size: 10
  context_file: "logs/session_context.json"
```

## Error Handling

- Try-catch blocks on all operations
- Automatic retry logic (max 3 attempts)
- Graceful failure recovery
- User-friendly error messages via TTS
- Comprehensive logging

## Logging

- **Console**: Colored output with levels
- **File**: Rotating file handler (10MB max, 5 backups)
- **Format**: JSON and text formats
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Performance

- Speech Recognition: 1-2 seconds
- Intent Understanding: 0.5-1 second
- Command Execution: <100ms
- Memory Usage: ~200MB idle

## Security

- Sandbox mode blocks risky operations
- Command whitelisting
- Path validation
- Dangerous pattern detection
- Confirmation gates for risky actions
- Execution logging
