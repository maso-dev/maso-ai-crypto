# Development Workflow & CI/CD Safety Guidelines

## 🎯 Overview
This document establishes a structured, CI/CD-safe development workflow that ensures:
- **Plan adherence**: Each development step follows the established roadmap
- **Branch safety**: Isolated development with proper validation
- **Quality gates**: Automated testing and validation at each step
- **Rollback capability**: Safe merging with ability to revert if needed

## 🌿 Branching Strategy

### Main Branches
- **`main`**: Production-ready code, always deployable
- **`develop`**: Integration branch for completed features

### Feature Branches
- **`feature/step-{X}-{description}`**: Individual development steps
- **`hotfix/urgent-fix`**: Critical production fixes
- **`release/v{major}.{minor}.{patch}`**: Release preparation

## 📋 Development Workflow

### 1. Step Planning & Branch Creation
```bash
# 1. Create feature branch for current step
git checkout develop
git pull origin develop
git checkout -b feature/step-{X}-{description}

# 2. Update step status in plan documents
# 3. Create step-specific test plan
```

### 2. Development Phase
```bash
# 1. Implement step requirements
# 2. Follow coding standards (see repo rules)
# 3. Add/update tests for new functionality
# 4. Update documentation
```

### 3. Pre-Merge Validation
```bash
# 1. Run local tests
python -m pytest tests/ -v
python -m pytest test_*.py -v

# 2. Check linting
python -m flake8 . --max-line-length=120
python -m black . --check

# 3. Validate API endpoints
curl -s http://localhost:8000/health | python -m json.tool
curl -s http://localhost:8000/admin_conf | python -m json.tool

# 4. Test core functionality
python test_enhanced_pipeline.py
python test_livecoinwatch.py
python test_tavily.py
```

### 4. Pull Request & Review
```bash
# 1. Push branch and create PR
git push origin feature/step-{X}-{description}

# 2. PR Requirements:
#    - Clear description of changes
#    - Link to step in plan document
#    - Test results summary
#    - Screenshots for UI changes
#    - API endpoint validation results
```

### 5. CI/CD Pipeline Validation
```yaml
# Automated checks (GitHub Actions or similar):
- Code linting (flake8, black)
- Unit tests (pytest)
- Integration tests (API endpoints)
- Security scan (bandit)
- Dependency check (safety)
- Build validation (uvicorn startup)
```

### 6. Merge & Integration
```bash
# 1. Merge to develop after approval
git checkout develop
git merge feature/step-{X}-{description}
git push origin develop

# 2. Update step status in plan documents
# 3. Create next step branch
git checkout -b feature/step-{X+1}-{description}
```

## 🔄 Step Validation Checklist

### Before Creating PR
- [ ] All tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Plan documents updated
- [ ] No hardcoded secrets
- [ ] Environment variables properly configured
- [ ] API endpoints tested
- [ ] Error handling implemented
- [ ] Logging added for debugging

### Before Merging
- [ ] CI/CD pipeline passes
- [ ] Code review approved
- [ ] Integration tests pass
- [ ] Performance impact assessed
- [ ] Rollback plan documented
- [ ] Step completion documented

## 📊 Current Development Status

### Completed Steps
- ✅ Step 1: LiveCoinWatch Integration
- ✅ Step 2: Data Quality Filtering
- ✅ Step 3: Refresh Process Engine
- ✅ Step 4: Tavily Integration
- ✅ Step 5: Frontend Integration

### Current Step
- 🔄 Step 6: CI/CD Workflow Implementation

### Next Steps
- ⏳ Step 7: Vercel Integration (cron jobs)
- ⏳ Step 8: Lightweight AI Engine
- ⏳ Step 9: A/B Testing Engine
- ⏳ Step 10: LangSmith Evaluators

## 🛡️ Safety Measures

### Plan Protection
- **No direct main branch commits**
- **Plan documents are read-only in main**
- **Step changes require plan updates**
- **Breaking changes require plan review**

### Rollback Strategy
```bash
# Quick rollback to previous step
git checkout develop
git revert HEAD
git push origin develop

# Full rollback to specific step
git checkout develop
git reset --hard step-{X}-commit-hash
git push --force origin develop
```

### Emergency Procedures
```bash
# Hotfix for production issues
git checkout main
git checkout -b hotfix/critical-issue
# Fix and test
git checkout main
git merge hotfix/critical-issue
git tag v{major}.{minor}.{patch}
```

## 📝 Step Documentation Template

### Step {X}: {Description}

**Branch**: `feature/step-{X}-{description}`

**Objectives**:
- [ ] Objective 1
- [ ] Objective 2
- [ ] Objective 3

**Implementation**:
- Files modified: `list of files`
- New files: `list of new files`
- API changes: `endpoint modifications`

**Testing**:
- Unit tests: `test files`
- Integration tests: `API endpoints`
- Manual tests: `user scenarios`

**Validation Results**:
- Linting: ✅/❌
- Unit tests: ✅/❌
- Integration tests: ✅/❌
- Performance: ✅/❌

**Dependencies**:
- Environment variables: `list`
- External APIs: `list`
- Database changes: `list`

**Rollback Plan**:
- Files to revert: `list`
- Database rollback: `commands`
- Configuration changes: `list`

## 🚀 Getting Started

### For New Developers
```bash
# 1. Clone repository
git clone https://github.com/your-org/maso-ai-crypto.git
cd maso-ai-crypto

# 2. Setup environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# 3. Configure environment variables
cp env.example .env
# Edit .env with your API keys

# 4. Run initial tests
python -m pytest tests/ -v

# 5. Start development server
python -m uvicorn main:app --reload --port 8000
```

### For Current Step Development
```bash
# 1. Check current step status
git checkout develop
git pull origin develop

# 2. Create step branch
git checkout -b feature/step-{X}-{description}

# 3. Follow step validation checklist
# 4. Create PR when ready
```

## 📚 Resources

- **Plan Documents**: 
  - `OPTIMIZED_BRAIN_ARCHITECTURE_PLAN.md`
  - `FRONTEND_INTEGRATION_PLAN.md`
  - `CURRENT_IMPLEMENTATION_STATUS.md`
- **Testing**: `tests/` directory
- **API Documentation**: `http://localhost:8000/docs`
- **Admin Dashboard**: `http://localhost:8000/admin`

## 🔧 Tools & Commands

### Development Commands
```bash
# Start development server
python -m uvicorn main:app --reload --port 8000

# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest test_enhanced_pipeline.py -v

# Check code style
python -m flake8 . --max-line-length=120

# Format code
python -m black .

# Security check
python -m bandit -r .

# Dependency check
python -m safety check
```

### Git Workflow Commands
```bash
# Create step branch
git checkout -b feature/step-{X}-{description}

# Commit with conventional message
git commit -m "feat: implement step {X} - {description}"

# Push and create PR
git push origin feature/step-{X}-{description}

# Update develop
git checkout develop
git pull origin develop
```

---

**Remember**: Always follow the plan, validate thoroughly, and maintain the safety of the main branch. Each step should be atomic and independently testable. 
