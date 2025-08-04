# Live Testing Overlay - Usage Instructions

## 🎮 How to Use the Live Testing Overlay

The verbose logging and OQE testing system is now active in the game! Here's how to use it:

### 🔧 Controls
- **F12**: Toggle the testing overlay on/off
- **F9**: Advance to next test step (mark current step complete)
- **F8**: Mark current test as failed
- **ESC**: Exit game (normal)

### 📋 What You'll See

When you press **F12** in the game, you'll see a testing overlay appear in the top-left corner showing:

```
🧪 Issue #34: Game State Logging
✅ Game State Logger Initialization  
⏳ Performance Impact Measurement
⚪ Scene Integration Test

[F12] Toggle | [F9] Next Step
```

### 🎯 Active Test Procedures (Issue #34)

The system automatically loads 7 test procedures for Issue #34:

1. **Game State Logger Initialization**
   - Initialize logger system
   - Verify session ID generation
   - Check log file creation

2. **Performance Impact Measurement**
   - Measure baseline FPS
   - Enable logging
   - Verify <2% impact

3. **Scene Integration Test**
   - Navigate between scenes
   - Verify transition logging
   - Check event capture

4. **Input Event Logging**
   - Press various keys
   - Verify input capture
   - Check response times

5. **Audio Event Logging**
   - Start/stop music
   - Change volume
   - Verify audio events

6. **Memory Usage Tracking**
   - Monitor memory delta
   - Check for leaks
   - Verify cleanup

7. **Log File Validation**
   - Check JSON format
   - Verify completeness
   - Test searchability

### 🧪 Testing Process

1. **Start the game** - Test procedures automatically load
2. **Press F12** to show/hide the testing overlay
3. **Follow test instructions** displayed in overlay
4. **Press F9** to mark steps complete as you verify them
5. **All events are automatically logged** for evidence

### 📊 What's Happening Behind the Scenes

While you play, the system automatically logs:
- Every keypress and mouse click
- Scene transitions with timing data
- FPS and memory metrics every second
- Audio events (music start/stop)
- System events and errors

### 📁 Log Files

Check the `logs/` directory for JSON log files:
- `game_session_XXXXXX_XXXXXXXX.jsonl` - Current session logs
- Each line is a complete JSON event record
- Search and analyze with any JSON tool

### 🎯 Success Indicators

The system is working correctly if you see:
- **Overlay appears/disappears** with F12
- **Test procedures listed** (3 visible at once)
- **Log files growing** in size during gameplay
- **Performance remains smooth** during logging
- **Events captured** for all actions

---

## 💡 Try This Now:

1. **Run the game**: `python -m src.main`
2. **Press F12** once you're in the game
3. **See the testing overlay** in the top-left
4. **Navigate to different scenes** (Title → Hub → Drive)
5. **Press F9** to mark test steps complete
6. **Check logs folder** to see the generated evidence

The system provides comprehensive debugging and testing capabilities while maintaining smooth gameplay performance!