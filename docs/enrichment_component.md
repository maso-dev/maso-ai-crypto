# LangChain Enrichment Component

## Overview

The `utils/enrichment.py` module provides a modular LangChain-based component for enriching crypto news articles with AI-generated metadata. This component extracts sentiment, trust scores, categories, and summaries from news content using OpenAI's GPT-4-turbo model.

## Features

- **Structured Output**: Uses Pydantic models for type-safe, validated output
- **Modern LangChain**: Built with the latest LangChain patterns (pipe syntax, JsonOutputParser)
- **Robust Error Handling**: Graceful handling of API failures and malformed inputs
- **Testable Interface**: Clean, modular design for easy testing and integration

## Input Schema

The enrichment component expects a dictionary with the following fields:

```python
{
    "title": str,        # Article title
    "content": str,      # Article content/text
    "source_name": str   # Source publication name
}
```

## Output Schema

Returns a `NewsEnrichment` Pydantic object with:

```python
class NewsEnrichment(BaseModel):
    sentiment: float        # Sentiment score (0.01-1.0)
    trust: float           # Trust score (0.01-1.0)
    categories: List[str]  # Relevant categories
    macro_category: str    # Primary macro category
    summary: str          # Brief summary
```

## Usage Example

```python
from utils.enrichment import get_enrichment_chain

# Get the enrichment chain
chain = get_enrichment_chain()

# Prepare article data
article = {
    "title": "Bitcoin ETF inflows reach $1.2B as institutional adoption accelerates",
    "content": "The cryptocurrency market saw significant institutional inflows...",
    "source_name": "CoinDesk"
}

# Run enrichment
result = chain.invoke(article)

# Access structured results
print(f"Sentiment: {result.sentiment}")
print(f"Trust: {result.trust}")
print(f"Categories: {result.categories}")
print(f"Macro Category: {result.macro_category}")
print(f"Summary: {result.summary}")
```

## Example Output

```python
{
    'sentiment': 0.85,
    'trust': 0.75,
    'categories': ['Bitcoin', 'ETF', 'Institutional Investment', 'Market Trends'],
    'macro_category': 'Cryptocurrency',
    'summary': 'Bitcoin ETFs experienced a surge in institutional investments...'
}
```

## Testing

Run the test suite to validate the component:

```bash
python3 test_enrichment.py
```

The test script validates:
- ✅ Output schema compliance
- ✅ Data type validation
- ✅ Value range checks (sentiment/trust 0-1)
- ✅ Error handling with minimal inputs

## Integration Notes

### Environment Variables

Ensure `OPENAI_API_KEY` is set in your environment:

```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### Dependencies

Required packages:
```bash
pip install langchain-openai langchain-core pydantic
```

### Performance Considerations

- **Temperature**: Set to 0.4 for consistent, structured output
- **Max Tokens**: Limited to 300 for concise summaries
- **Caching**: Consider implementing caching for repeated articles
- **Rate Limiting**: Monitor OpenAI API rate limits in production

## Error Handling

The component handles various error scenarios:

1. **Missing API Key**: Returns empty results gracefully
2. **API Failures**: Logs errors and continues processing
3. **Malformed Input**: Validates required fields before processing
4. **JSON Parsing**: Uses JsonOutputParser for reliable structured output

## Future Enhancements

- [ ] Add caching layer for repeated articles
- [ ] Implement batch processing for multiple articles
- [ ] Add more granular category classification
- [ ] Support for different languages
- [ ] Integration with sentiment analysis models

## Related Components

This enrichment component is part of the larger LangChain pipeline:

1. **News Ingestion** → **Chunking** → **Enrichment** → **Vector Storage**
2. **Query Processing** → **RAG Retrieval** → **Market Summary Generation**

See the main pipeline documentation for integration details. 
