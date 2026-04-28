# Advanced Features Documentation

## 1. Comprehensive Logging

### Multi-Format Output

```python
from utils.enhanced_logger import ColoredFormatter, JSONFormatter

# Console with colors
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter('%(asctime)s - %(levelname)s - %(message)s'))

# File with JSON
file_handler = logging.FileHandler('logs/assistant.log')
file_handler.setFormatter(JSONFormatter())
```

### Configuration

```yaml
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  file: "logs/assistant.log"
  max_file_size: 10485760  # 10 MB
  backup_count: 5
  console_output: true
```

### Output Example

```
[INFO] 2024-01-15 10:30:45 - VoiceAssistant - Voice Assistant Starting
[DEBUG] 2024-01-15 10:30:46 - SpeechRecognizer - Listening for audio...
[INFO] 2024-01-15 10:30:48 - NLPProcessor - Processing: Open Downloads folder
[INFO] 2024-01-15 10:30:49 - CommandExecutor - Executing: open_folder
[INFO] 2024-01-15 10:30:49 - ContextMemory - Command added to history
```

---

## 2. Error Handling

### Try-Catch Pattern

```python
try:
    result = speech_recognizer.listen()
except Exception as e:
    logger.error(f"Speech recognition error: {e}")
    text_to_speech.speak("I didn't hear that. Please try again.")
```

### Retry Logic

```yaml
api:
  max_retries: 3
  retry_delay: 2  # seconds
```

### Error Recovery

- Automatic retry on failures
- Graceful degradation
- User-friendly feedback via TTS
- Session continuation after errors

---

## 3. Configuration-Driven

### No Hardcoding

```python
# ✓ GOOD: Configuration-driven
api_key = config.get('openai', {}).get('api_key')
model = config.get('openai', {}).get('model', 'gpt-4')

# ✗ BAD: Hardcoded
api_key = "sk-1234..."
model = "gpt-4"
```

### Runtime Configuration

```python
# Load config
config = self._load_config("config/config.yaml")

# Access nested values
temperature = self.config.get('openai', {}).get('temperature', 0.3)
```

---

## 4. OS Compatibility

### Automatic Detection

```python
def _detect_os(self) -> str:
    """Detect operating system."""
    system = platform.system()
    if system == "Darwin":
        return "macos"
    elif system == "Linux":
        return "linux"
    elif system == "Windows":
        return "windows"
```

### OS-Specific Commands

```python
if self.os_type == "macos":
    subprocess.run(["open", str(path)], check=True)
elif self.os_type == "linux":
    subprocess.run(["xdg-open", str(path)], check=True)
elif self.os_type == "windows":
    os.startfile(str(path))
```

---

## 5. Modular Design

### Independent Modules

Each module is self-contained and testable:

```python
# SpeechRecognizer can be used independently
recognizer = SpeechRecognizer()
text = recognizer.listen()

# NLPProcessor can be used independently
processor = NLPProcessor(api_key)
command = processor.process(text)

# No interdependencies
```

### Clear Separation

```
speech_recognition.py  → Audio input only
nlp_processor.py       → Intent parsing only
command_executor.py    → Command execution only
code_generator.py      → Code generation only
text_to_speech.py      → Audio output only
advanced_features.py   → Optional features
```

---

## 6. Wake Word Detection ⭐

### Usage

```python
from modules.advanced_features import WakeWordDetector

# Initialize
detector = WakeWordDetector(
    wake_word="hey assistant",
    sensitivity=0.5  # 0.0-1.0
)

# Detect
if detector.detect("Hey Assistant, open Downloads"):
    print("Command activated!")
    # Process command
```

### Features

- **Exact Matching**: "hey assistant" → matches exactly
- **Fuzzy Matching**: "hey assist" → matches if sensitivity > 0.3
- **Statistics**: Track detection patterns
- **Configurable**: Adjust sensitivity per use case

### Example Output

```python
stats = detector.get_detection_stats()
# {
#   'total_detections': 42,
#   'exact_matches': 38,
#   'fuzzy_matches': 4,
#   'last_detection': '2024-01-15T10:30:49'
# }
```

---

## 7. Context Memory ⭐

### Usage

```python
from modules.advanced_features import ContextMemory

# Initialize
memory = ContextMemory(
    max_size=10,
    persist_file="logs/session_context.json"
)

# Add command
memory.add(
    command="Create a Python project",
    result={'success': True, 'path': '/path/to/project'},
    duration=2.5,
    metadata={'language': 'python'}
)

# Retrieve
recent = memory.get_recent(5)
summary = memory.get_summary()
```

### Features

- **History Tracking**: Store last N commands
- **Persistent Storage**: JSON file backup
- **Search**: Find commands by pattern
- **Statistics**: Session summaries
- **Follow-ups**: Understand context of new commands

### Example Summary

```python
summary = memory.get_summary()
# {
#   'total_commands': 10,
#   'total_duration': 25.3,
#   'average_duration': 2.53,
#   'first_command': '2024-01-15T10:30:00',
#   'last_command': '2024-01-15T10:35:00'
# }
```

---

## 8. Sandbox Mode ⭐

### Usage

```python
from modules.advanced_features import SandboxExecutor

# Initialize
sandbox = SandboxExecutor(
    confirmation_required=True,
    max_execution_time=30
)

# Check if action is safe
if sandbox.can_execute("execute_system"):
    # Request confirmation for risky actions
    if sandbox.request_confirmation("rm -rf /tmp/data"):
        execute_command()
else:
    print("Action blocked")

# Log execution
sandbox.log_execution(
    action="create_project",
    success=True,
    duration=2.5,
    details="Created Python project"
)

# View execution log
log = sandbox.get_execution_log()
```

### Features

- **Safe Actions**: Pre-approved commands (open_folder, create_project)
- **Risky Actions**: Blocked unless confirmed (execute_system, delete_file)
- **Confirmation Gate**: User prompt for dangerous operations
- **Execution Logging**: Track all operations
- **Whitelisting**: Only run approved actions

### Risky vs Safe

```python
SAFE_ACTIONS = {
    "open_folder",
    "create_project",
    "write_code",
    "run_code",
}

RISKY_ACTIONS = {
    "execute_system",
    "delete_file",
    "modify_system",
    "install_package",
}
```

---

## Integration Example

```python
from modules import (
    SpeechRecognizer,
    NLPProcessor,
    CommandExecutor,
    TextToSpeech,
    WakeWordDetector,
    ContextMemory,
    SandboxExecutor,
)

# Initialize all modules
recognizer = SpeechRecognizer()
processor = NLPProcessor(api_key)
executor = CommandExecutor()
tts = TextToSpeech()
detector = WakeWordDetector()
memory = ContextMemory()
sandbox = SandboxExecutor()

# Main loop
while True:
    # 1. Listen
    text = recognizer.listen()
    
    # 2. Wake word check
    if not detector.detect(text):
        continue
    
    # 3. Parse command
    command = processor.process(text)
    
    # 4. Safety check
    if not sandbox.can_execute(command['action']):
        if not sandbox.request_confirmation(command['action']):
            continue
    
    # 5. Execute
    start = time.time()
    result = executor.execute(command)
    duration = time.time() - start
    
    # 6. Log execution
    sandbox.log_execution(
        command['action'],
        result.get('success'),
        duration
    )
    
    # 7. Store in memory
    memory.add(text, result, duration)
    
    # 8. Respond
    if result.get('success'):
        tts.speak(result.get('message'))
    else:
        tts.speak(f"Error: {result.get('error')}")
    
    # 9. Show summary
    print(memory.get_summary())
```

---

## Performance Tips

1. **Reduce Model Size**: Use `base` or `small` for faster responses
2. **Enable Wake Word**: Skip processing until activation
3. **Batch Operations**: Process multiple commands together
4. **Cache Context**: Reuse conversation history
5. **Async Operations**: Use non-blocking TTS

---

## Troubleshooting

### Wake Word Not Detected
- Lower sensitivity threshold
- Check microphone input levels
- Verify audio quality

### Memory Not Persisting
- Check file path exists
- Verify write permissions
- Check JSON format

### Sandbox Blocking Commands
- Add to whitelist if safe
- Lower confirmation requirement
- Check action name matches
