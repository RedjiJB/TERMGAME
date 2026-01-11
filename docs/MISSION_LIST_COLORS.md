# Mission List Color Guide

The `list` command displays all available missions with color coding to help you quickly identify mission types and difficulty levels.

## Color Coding Reference

### Platform Colors

| Platform | Color | Example |
|----------|-------|---------|
| **Linux** | Green | <span style="color:green">Linux</span> |
| **PowerShell** | Blue | <span style="color:blue">PowerShell</span> |

### Mission ID Colors

| Platform | Color | Example |
|----------|-------|---------|
| **Linux** | Bright Green | `linux/basics/navigation` |
| **PowerShell** | Bright Blue | `powershell/basics/hello-powershell` |

### Title Colors

| Platform | Color | Visibility |
|----------|-------|-----------|
| **Linux** | White | High contrast |
| **PowerShell** | Cyan | Distinct from Linux |

### Difficulty Colors

| Difficulty | Color | Example |
|-----------|-------|---------|
| **beginner** | Green | <span style="color:green">beginner</span> |
| **intermediate** | Yellow | <span style="color:yellow">intermediate</span> |
| **advanced** | Red | <span style="color:red">advanced</span> |

## Table Layout

```
┌───┬────────────┬──────────────────────────────────────────┬────────────────────────────────────┬──────────────┬────────┐
│ ✓ │ Platform   │ ID                                       │ Title                              │ Difficulty   │ Time   │
├───┼────────────┼──────────────────────────────────────────┼────────────────────────────────────┼──────────────┼────────┤
│   │ Linux      │ linux/basics/navigation                  │ Directory Navigation Basics        │ beginner     │ 15 min │
│ ✓ │ Linux      │ linux/basics/file-operations             │ File Operations Fundamentals       │ beginner     │ 20 min │
│   │ PowerShell │ powershell/basics/hello-powershell       │ Your First PowerShell Command      │ beginner     │ 10 min │
│   │ PowerShell │ powershell/scripting/functions           │ Creating PowerShell Functions      │ intermediate │ 25 min │
└───┴────────────┴──────────────────────────────────────────┴────────────────────────────────────┴──────────────┴────────┘

Found 126 mission(s) - 2 completed
```

## Column Descriptions

| Column | Description |
|--------|-------------|
| **✓** | Green checkmark (✓) if mission is completed |
| **Platform** | Linux or PowerShell - shows which type of container needed |
| **ID** | Full mission identifier (use this with `start` command) |
| **Title** | Human-readable mission name |
| **Difficulty** | Mission complexity level (beginner/intermediate/advanced) |
| **Time** | Estimated completion time in minutes |

## Sorting Order

Missions are sorted by:
1. **Platform** (Linux first, then PowerShell)
2. **Difficulty** (beginner → intermediate → advanced)
3. **ID** (alphabetical)

This groups similar missions together for easier navigation.

## Quick Examples

### Linux Missions
- **Platform:** <span style="color:green">■ Linux</span>
- **ID:** <span style="color:limegreen">linux/networking/test-connection</span>
- **Title:** Network Connectivity Testing

### PowerShell Missions
- **Platform:** <span style="color:blue">■ PowerShell</span>
- **ID:** <span style="color:dodgerblue">powershell/cloud/azure-intro</span>
- **Title:** Introduction to Azure PowerShell

## Understanding the Visual Hierarchy

1. **Platform color** (left column) - First thing you notice
2. **Difficulty color** - Shows challenge level at a glance
3. **Completion checkmark** - Track your progress
4. **Mission ID** - Unique identifier for `start` command

## Tips for Using the List

### Filter by Color
- Scan for **green** = Linux missions
- Scan for **blue** = PowerShell missions

### Track Progress
- Look for **green ✓** in first column = completed
- Empty first column = not yet completed

### Plan Your Learning Path
- **Green difficulty** = Good for beginners
- **Yellow difficulty** = Requires some experience
- **Red difficulty** = Challenging, requires solid foundation

## Common Patterns

### Mission ID Structure

**Linux missions:**
```
linux/<topic>/<specific-mission>
      └─────┴────────────────────  Topic area (basics, networking, scripting, etc.)
```

**PowerShell missions:**
```
powershell/<topic>/<specific-mission>
           └─────┴────────────────  Topic area (basics, cloud, security, etc.)
```

### Time Estimates
- **10-15 min** - Quick introductory missions
- **20-30 min** - Standard learning missions
- **35-50 min** - Comprehensive or advanced missions

## Starting a Mission

After viewing the list, copy the full ID:

```bash
# Example: Start a Linux mission
> start linux/basics/navigation

# Example: Start a PowerShell mission
> start powershell/basics/hello-powershell
```

## Accessibility

The color scheme is designed to be:
- **Distinguishable** - Even in monochrome, layout remains clear
- **Consistent** - Same colors always mean the same thing
- **Functional** - Colors enhance usability without being required

## Terminal Compatibility

Works best with:
- Windows Terminal
- iTerm2 (macOS)
- GNOME Terminal (Linux)
- VS Code integrated terminal
- Any terminal supporting 256-color or true color

May have limited colors in:
- Classic Windows Command Prompt (cmd.exe)
- Basic SSH terminals
- Minimal terminal emulators
