# Contributing to Agentic Trip Planner

Thank you for your interest in contributing to the Agentic Trip Planner! This document provides guidelines and information for contributors.

## 🌟 Getting Started

### Prerequisites
- Python 3.10+
- Git
- Basic understanding of multi-agent systems and APIs

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/mini-task-planner.git
   cd mini-task-planner
   ```

2. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Add your API keys for testing
   ```

4. **Run tests to verify setup**
   ```bash
   python -m pytest
   ```

## 📋 Development Rules

Please follow the established development rules in `docs/development_rules.md`:

### Core Principles
- **Docs-first**: Update documentation before making code changes
- **Modular design**: Agents and tools should be small, testable units
- **Free-first**: Prefer free/public APIs over paid services
- **Privacy-by-default**: No PII storage unless explicitly opted in
- **Graceful degradation**: Always provide useful information even with limited data

### Git Workflow
- Use meaningful commit messages
- Follow the project timeline structure (see development_rules.md)
- Keep commits small and focused
- Include tests for new functionality

## 🏗️ Architecture Overview

### Adding New Agents
When creating new specialized agents:

1. **Create agent file** in `src/agents/`
2. **Follow the agent pattern**:
   ```python
   class NewAgent:
       def execute_task(self, request: TripRequest, context: Dict[str, Any]) -> Dict[str, Any]:
           # Agent logic here
           pass
   ```
3. **Add to central coordination** in `central_planning_agent.py`
4. **Write comprehensive tests** in `test/`
5. **Update documentation**

### Adding New APIs
When integrating new external APIs:

1. **Create tool file** in `src/tools/`
2. **Follow the tool pattern** with proper error handling
3. **Add fallback mechanisms** for when API is unavailable
4. **Update API client manager** in `src/utils/api_client.py`
5. **Add environment variables** to `.env.example`
6. **Document in** `docs/free_apis.md`

## 🧪 Testing Guidelines

### Test Categories
- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test agent coordination and API integration
- **Contract tests**: Verify external API responses
- **End-to-end tests**: Test complete trip planning workflows

### Writing Tests
```python
def test_flight_agent_search():
    """Test flight search with mock data."""
    agent = FlightAgent()
    request = create_test_request()
    result = agent.search_flights(request, {})
    
    assert result["status"] == "success"
    assert len(result["flights"]) > 0
```

### Running Tests
```bash
# All tests
python -m pytest

# Specific categories
python -m pytest test/test_agents/ -v
python -m pytest test/test_tools/ -v

# With coverage
python -m pytest --cov=src
```

## 📝 Documentation Standards

### Code Documentation
- Use clear docstrings for all classes and methods
- Include type hints
- Add inline comments for complex logic
- Update README.md for user-facing changes

### API Documentation
- Document new API integrations in `docs/free_apis.md`
- Include setup instructions and usage limits
- Provide fallback strategies

## 🐛 Reporting Issues

### Bug Reports
When reporting bugs, please include:
- **Description**: Clear description of the issue
- **Steps to reproduce**: Detailed steps to recreate the bug
- **Expected behavior**: What should have happened
- **Actual behavior**: What actually happened
- **Environment**: Python version, OS, API keys used
- **Logs**: Relevant error messages or log output

### Feature Requests
For new features, please describe:
- **Problem**: What problem does this solve?
- **Solution**: Proposed solution approach
- **Alternatives**: Any alternative solutions considered
- **Impact**: Who would benefit from this feature?

## 🚀 Submission Guidelines

### Pull Request Process

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes following development rules**
   - Update documentation first
   - Write tests
   - Implement feature
   - Ensure all tests pass

3. **Commit with clear messages**
   ```bash
   git commit -m "feat: add weather integration for packing recommendations"
   ```

4. **Push and create pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Documentation
- [ ] README updated if needed
- [ ] Code comments added
- [ ] API documentation updated
```

## 🏷️ Code Style

### Python Style Guidelines
- Follow PEP 8
- Use meaningful variable names
- Keep functions small and focused
- Use type hints consistently

### Example:
```python
from typing import Dict, List, Optional

def search_flights(
    origin: str, 
    destination: str, 
    dates: List[str]
) -> Optional[Dict[str, Any]]:
    """
    Search for flights between origin and destination.
    
    Args:
        origin: Origin city/airport code
        destination: Destination city/airport code
        dates: List of travel dates in YYYY-MM-DD format
        
    Returns:
        Flight search results or None if no flights found
    """
    # Implementation here
    pass
```

## 🔧 Tools and Utilities

### Useful Development Commands
```bash
# Format code
black src/ test/

# Lint code
flake8 src/ test/

# Type checking
mypy src/

# Security check
bandit -r src/
```

## 🙋‍♀️ Getting Help

- **Documentation**: Check `docs/` directory
- **Issues**: Browse existing [GitHub Issues](https://github.com/yourusername/mini-task-planner/issues)
- **Examples**: Look at `output/` for sample itineraries
- **Tests**: Review `test/` directory for usage examples

## 🎯 Good First Issues

Look for issues labeled with:
- `good first issue`: Perfect for newcomers
- `documentation`: Improve docs and examples
- `enhancement`: Add new features
- `bug`: Fix existing problems

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/mini-task-planner/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/mini-task-planner/discussions)

---

Thank you for contributing to making travel planning more intelligent and accessible! 🌍✈️
