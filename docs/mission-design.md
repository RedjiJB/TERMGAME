# Mission Design Guide

## Overview

This guide explains how to create missions for TermGame using YAML scenario files.

## Scenario Structure

### Basic Template

```yaml
mission:
  id: "category/subcategory/mission-name"
  title: "Mission Title"
  difficulty: beginner  # beginner, intermediate, advanced, expert
  description: "Brief description of what users will learn"
  estimated_time: "15 minutes"

environment:
  image: "ubuntu:22.04"  # Container image
  setup:
    - "apt-get update && apt-get install -y vim"

steps:
  - id: "step-1"
    title: "Step Title"
    description: "What the user needs to do"
    hint: "Optional hint text"
    validation:
      type: "matcher-type"
      params:
        key: "value"
```

## Validation Types

### command-output
Validates command output:

```yaml
validation:
  type: "command-output"
  command: "ls -la"
  matcher: "contains"
  expected: "README.md"
```

### file-exists
Checks if file exists:

```yaml
validation:
  type: "file-exists"
  path: "/home/user/myfile.txt"
```

### file-content
Validates file contents:

```yaml
validation:
  type: "file-content"
  path: "/home/user/config.txt"
  matcher: "regex"
  pattern: "port=\\d{4}"
```

## Best Practices

1. **Start Simple**: Begin with basic commands
2. **Progressive Difficulty**: Gradually increase complexity
3. **Clear Instructions**: Be specific about expectations
4. **Provide Hints**: Help users without giving answers
5. **Test Thoroughly**: Run scenarios manually before committing

## Example Mission

See `scenarios/linux/basics/navigation.yml` for a complete example.
