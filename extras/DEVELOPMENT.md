# Development Guide

## Project Overview

This AI Resume Generator uses a sophisticated agentic workflow built with LangGraph to create tailored resumes. The system intelligently extracts information from existing resumes, generates relevant projects and skills based on job descriptions, and produces professional PDF resumes using LaTeX.

## Key Components

### 1. LangGraph Workflow

The core of the application is the LangGraph workflow defined in `backend/main.py`. The workflow consists of 5 sequential nodes:

```python
extract_info → generate_projects → generate_skills → create_metadata → generate_latex
```

Each node is a Python function that receives the current state and returns an updated state.

### 2. State Management

The workflow state is defined using TypedDict:

```python
class AgentState(TypedDict):
    resume_text: str
    job_description: str
    extracted_info: Optional[dict]
    generated_projects: Optional[List[dict]]
    generated_skills: Optional[dict]
    resume_metadata: Optional[ResumeMetadata]
    latex_code: Optional[str]
    messages: Annotated[list, operator.add]
```

### 3. Tool Usage

The `create_resume_metadata` tool is defined using the `@tool` decorator from LangChain. While not directly called by the LLM in the current implementation, it serves as a structured way to define the metadata schema.

### 4. Prompt Engineering

Each node uses carefully crafted prompts:

- **Extract Info**: Asks Claude to extract structured information in JSON format
- **Generate Projects**: Requests 3-4 relevant projects with technologies and achievements
- **Generate Skills**: Asks for categorized technical skills aligned with job description

### 5. LaTeX Template

The LaTeX template uses placeholders that are replaced with actual data:

```latex
{{NAME}} → User's name
{{EMAIL}} → User's email
{{EXPERIENCE}} → Generated experience section
{{PROJECTS}} → Generated projects section
{{TECHNICAL_SKILLS}} → Generated skills
```

## Extending the Application

### Adding New Extraction Fields

1. Update `ResumeMetadata` Pydantic model in `backend/main.py`
2. Modify the extraction prompt in `extract_resume_info()` function
3. Update LaTeX template with new placeholder
4. Add replacement logic in `generate_latex()` function

### Adding New AI Nodes

1. Define new node function with signature: `def my_node(state: AgentState) -> AgentState`
2. Add node to graph: `workflow.add_node("my_node", my_node)`
3. Add edge: `workflow.add_edge("previous_node", "my_node")`

### Customizing Project Generation

Modify the prompt in `generate_projects()` to:
- Request more/fewer projects
- Include specific types of projects
- Emphasize certain technologies

### Customizing Skills Generation

Modify the prompt in `generate_skills()` to:
- Add new skill categories
- Focus on specific domains
- Include proficiency levels

## API Integration

### Using Different LLMs

Replace the LLM initialization:

```python
# For OpenAI
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4")

# For Anthropic (current)
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model="claude-sonnet-4-20250514")
```

### Adding Rate Limiting

Use a rate limiter decorator:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/generate-resume")
@limiter.limit("5/minute")
async def generate_resume(...):
    ...
```

## Frontend Customization

### Changing Colors

Edit `frontend/src/App.jsx`:

```jsx
// Current: from-blue-600 to-purple-600
// Change to: from-green-600 to-teal-600
className="bg-gradient-to-r from-green-600 to-teal-600"
```

### Adding New Features

1. Add new state: `const [newFeature, setNewFeature] = useState(null);`
2. Update UI to collect new data
3. Send to backend in API call
4. Process in backend workflow

## Testing

### Backend Testing

```python
# test_main.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_generate_resume():
    # Add test implementation
    pass
```

### Frontend Testing

```javascript
// App.test.jsx
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders app title', () => {
  render(<App />);
  const titleElement = screen.getByText(/AI Resume Generator/i);
  expect(titleElement).toBeInTheDocument();
});
```

## Deployment

### Railway/Render Deployment

1. Create `Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

2. Set environment variables in platform dashboard

### Docker Deployment

```bash
docker-compose up -d
```

### Kubernetes Deployment

Create deployment files for backend and frontend services.

## Performance Optimization

### Caching

Add Redis caching for common job descriptions:

```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

def generate_resume(...):
    cache_key = f"resume:{hash(job_description)}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    # ... generate resume
    r.setex(cache_key, 3600, json.dumps(result))
```

### Async Processing

Use Celery for background processing:

```python
from celery import Celery

celery = Celery('tasks', broker='redis://localhost:6379')

@celery.task
def generate_resume_async(resume_text, job_description):
    # ... workflow execution
    return result
```

## Security Considerations

1. **Input Validation**: Validate file types and sizes
2. **Rate Limiting**: Prevent API abuse
3. **API Key Protection**: Never expose Anthropic API key
4. **CORS**: Configure properly for production
5. **File Cleanup**: Delete temporary files after processing

## Monitoring

### Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_resume_info(state):
    logger.info(f"Extracting info from resume")
    # ...
```

### Metrics

Track:
- Number of resumes generated
- Average processing time
- API errors
- User satisfaction

## Common Issues

### Issue: LaTeX Compilation Fails

**Solution**: Check LaTeX logs, ensure all required packages are installed

### Issue: API Key Invalid

**Solution**: Verify ANTHROPIC_API_KEY in .env file

### Issue: PDF Preview Not Working

**Solution**: Check browser console, verify base64 encoding

### Issue: Slow Generation

**Solution**: Consider caching, async processing, or using faster Claude model

## Best Practices

1. **Error Handling**: Wrap API calls in try-catch blocks
2. **Logging**: Log all important events and errors
3. **Validation**: Validate all inputs before processing
4. **Testing**: Write tests for critical functionality
5. **Documentation**: Keep code well-documented
6. **Version Control**: Use Git for version control
7. **Code Review**: Review code before merging

## Resources

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details
