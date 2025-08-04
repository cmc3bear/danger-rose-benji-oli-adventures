# 📜 Commit Message Confessional Guidelines

## Strategy #2 from the Twenty Sacred Strategies

As proclaimed by **Agent_LeadDev_002**: *"Our commits read like the ramblings of madmen! 'Fix stuff', 'asdf' - these are SINS!"*

## The Sacred Format

```
type(component): what I did | why I did it | evidence: reference
```

### Examples of Righteous Commits

```bash
# Good Examples ✅
feat(player): Add double-jump ability | Requested by design team | evidence: issue-#42
fix(skiing): Correct collision with trees | Players getting stuck in geometry | evidence: bug-report-2025-08-03
docs(readme): Update installation steps | New pygame version requires different setup | evidence: pr-#15
refactor(sound): Extract audio loading logic | Reduce code duplication across scenes | evidence: design-doc-audio-refactor
test(hub): Add door navigation tests | Ensure doors work after refactoring | evidence: user-story-12

# Sinful Examples ❌
fix stuff
asdf
more changes
update
working on things
```

## The Three Sacred Questions

Every commit must answer:

1. **WHAT** did I change? *(type and brief description)*
2. **WHY** did I change it? *(business/technical reason)*  
3. **WHERE** is the evidence? *(traceable reference)*

## Commit Types

| Type | Purpose | Example |
|------|---------|---------|
| `feat` | New feature | `feat(pool): Add splash effects` |
| `fix` | Bug fix | `fix(player): Prevent falling through floor` |
| `docs` | Documentation | `docs(api): Add function docstrings` |
| `style` | Formatting | `style(ui): Fix button alignment` |
| `refactor` | Code restructure | `refactor(scenes): Extract common base class` |
| `perf` | Performance | `perf(rendering): Optimize sprite batching` |
| `test` | Testing | `test(physics): Add collision detection tests` |
| `chore` | Build/tools | `chore(deps): Update pygame to 2.5.0` |

## Components

Use these component names:
- `player` - Player character logic
- `skiing` - Ski minigame
- `pool` - Pool minigame  
- `vegas` - Vegas minigame
- `hub` - Hub world navigation
- `audio` - Sound and music
- `ui` - User interface
- `assets` - Game assets
- `tests` - Test code
- `build` - Build system
- `docs` - Documentation

## Evidence References

Link every commit to traceable evidence:

- `issue-#42` - GitHub issue number
- `pr-#15` - Pull request number
- `bug-report-2025-08-03` - Bug report by date
- `design-doc-audio-refactor` - Design document name
- `user-story-12` - User story number
- `review-feedback-john` - Code review feedback
- `performance-test-results` - Performance analysis

## Setting Up Git Template

Enable the commit message template:

```bash
git config commit.template .gitmessage
```

Now when you run `git commit`, you'll see the template with reminders!

## Enforcement

The Screenshot Salvation System will capture evidence of commit message sins. Repeated violations may result in:

- Paired Programming Penance
- Code Review Confession
- Daily Standup Shame

## Commit Message Blessing

Before committing, recite:

> *"May this commit tell a story of purpose,*  
> *May its evidence be clear and true,*  
> *May future developers understand my intent,*  
> *And may the build remain green."*

## Examples in Practice

### Before (Sinful)
```bash
git commit -m "fix bug"
git commit -m "updates"  
git commit -m "working on pool game"
```

### After (Righteous)  
```bash
git commit -m "fix(pool): Correct ball physics after paddle hit | Balls were bouncing incorrectly | evidence: issue-#28"
git commit -m "feat(hub): Add door hover effects | Improve user feedback for interactive elements | evidence: user-story-8"
git commit -m "test(skiing): Add slope collision tests | Ensure player can't ski through mountains | evidence: bug-report-2025-08-02"
```

## Measuring Success

Track your commitment to the Confessional:

- **Compliance Rate**: % of commits following format
- **Evidence Linking**: % of commits with valid references  
- **Clarity Score**: Team vote on commit message usefulness
- **Future Proof Test**: Can you understand your own commits after 3 months?

---

*"The git history shall tell the story of our project's divine transformation!"*

**✝️ In ClaudeEthos' name, commit with purpose. Amen.**