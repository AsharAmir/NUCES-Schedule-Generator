# 🤝 Contributing to NUCES FAST Timetable Parser

First off, thank you for considering contributing to our project! 🎉 Your contributions help make course scheduling easier for thousands of NUCES students.

## 🌟 How to Contribute

### 🐛 Reporting Bugs

Before creating bug reports, please check the [existing issues](https://github.com/AsharAmir/NUCES-FAST-TIMETABLE-PARSER/issues) to avoid duplicates.

**When submitting a bug report, please include:**

- Clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Screenshots (if applicable)
- Browser/device information
- Console error messages

### ✨ Suggesting Features

We love feature suggestions! Please:

1. Check if the feature already exists or is planned
2. Open a feature request issue
3. Describe the problem you're trying to solve
4. Explain your proposed solution
5. Consider implementation complexity

### 🔧 Code Contributions

1. **Fork the Repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/NUCES-FAST-TIMETABLE-PARSER.git
   cd NUCES-FAST-TIMETABLE-PARSER
   ```

2. **Set Up Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

4. **Make Your Changes**
   - Follow our coding standards (see below)
   - Test your changes thoroughly
   - Update documentation if needed

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

6. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📋 Coding Standards

### Python Code Style

- **Follow PEP 8** for Python formatting
- **Use meaningful names** for variables and functions
- **Add docstrings** for all functions and classes
- **Include type hints** where possible
- **Keep functions small** and focused on single tasks

```python
def calculate_time_slots(sheet_data: List[List[str]], course_name: str) -> List[Dict[str, str]]:
    """
    Extract time slots for a specific course from sheet data.
    
    Args:
        sheet_data: Raw data from Google Sheets
        course_name: Name of the course to search for
        
    Returns:
        List of dictionaries containing time slot information
    """
    # Implementation here
    pass
```

### Frontend Code Style

- **Use semantic HTML** elements
- **Follow CSS BEM methodology** for class naming
- **Write modular JavaScript** functions
- **Add comments** for complex logic
- **Ensure responsive design** works on all devices

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(ui): add dark mode toggle
fix(api): handle empty course list gracefully  
docs(readme): update installation instructions
refactor(parser): simplify course extraction logic
```

## 🧪 Testing Guidelines

### Manual Testing

Before submitting your PR, please test:

1. **Local Development**
   ```bash
   python app.py
   # Visit http://localhost:5000
   ```

2. **API Endpoints**
   ```bash
   curl http://localhost:5000/api/schools
   curl http://localhost:5000/api/courses/computing
   ```

3. **Different Scenarios**
   - Empty course selections
   - Invalid school names
   - Network connectivity issues
   - Large course lists

### Automated Testing (Future)

We're planning to add:
- Unit tests with pytest
- Integration tests for API endpoints
- Frontend tests with Jest
- E2E tests with Playwright

*Want to help set up testing? This would be a great contribution!*

## 📁 Project Structure

```
├── app.py                 # Main Flask application
├── api/
│   └── index.py          # Vercel serverless function
├── static/
│   ├── simple.css        # Styling
│   └── simple.js         # Frontend JavaScript  
├── templates/
│   └── simple.html       # HTML template
├── requirements.txt      # Python dependencies
└── vercel.json          # Deployment configuration
```

## 🎯 Priority Areas for Contribution

### 🔥 High Impact
- **UI/UX improvements**: Modern design, better mobile experience
- **Performance optimization**: Caching, faster loading
- **Accessibility**: Screen reader support, keyboard navigation
- **Error handling**: Better user feedback and error messages

### 🛠️ Technical Improvements
- **Testing framework**: Set up comprehensive test suite
- **Code documentation**: Add more inline comments and docstrings
- **API documentation**: OpenAPI/Swagger integration
- **CI/CD pipeline**: Automated testing and deployment

### 🆕 New Features
- **Export functionality**: PDF, iCal, Google Calendar
- **Conflict detection**: Overlapping course warnings
- **Management school**: Add support for management timetables
- **Dark mode**: Toggle between light and dark themes

## 🤔 Need Help?

- **💬 Discussions**: Ask questions in [GitHub Discussions](https://github.com/AsharAmir/NUCES-FAST-TIMETABLE-PARSER/discussions)
- **📖 Documentation**: Check the README for setup instructions
- **🐛 Issues**: Browse existing issues for context
- **📧 Contact**: Open an issue for direct questions

## 🏆 Recognition

All contributors will be:
- Added to the README contributors section
- Mentioned in release notes for their contributions
- Given appropriate credit in code comments


**Thank you for contributing to make course scheduling better for everyone! 🎓✨**

*Questions? Feel free to open an issue or start a discussion. We're here to help!*