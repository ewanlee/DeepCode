# PDF Support in Paper2Sim

Paper2Sim now supports direct PDF input for Phase 1 analysis, enabling accurate extraction of mathematical formulas and notation from OR/OM/MS papers.

## 🎯 Why PDF Support?

Many Operations Research, Operations Management, and Management Science papers:
- Are only available as PDF files (no LaTeX source)
- Contain extensive mathematical notation that loses information when converted to plain text
- Include complex formulas, Greek letters, subscripts, superscripts, and special symbols

By using LLM models with native PDF support (like Gemini), we can:
- ✅ Preserve mathematical notation exactly as it appears
- ✅ Extract formulas with full fidelity
- ✅ Capture equation numbers and references
- ✅ Maintain layout and structure information

## 📋 Requirements

### 1. OpenRouter API Key

PDF processing uses OpenRouter as the unified gateway to access models with PDF support.

Get your API key from: https://openrouter.ai/keys

### 2. Configuration

Add to `mcp_agent.secrets.yaml`:
```yaml
openrouter:
  api_key: "your-openrouter-api-key-here"
```

Or set environment variable:
```bash
export OPENROUTER_API_KEY="your-key-here"
```

### 3. Model Configuration

In `mcp_agent.config.yaml`, configure models with PDF support:

```yaml
# Set OpenRouter as your LLM provider
llm_provider: "openrouter"

openrouter:
  base_url: "https://openrouter.ai/api/v1"
  
  # Models for different phases
  # Recommended: Gemini models have excellent PDF support
  planning_model: "google/gemini-2.0-flash-exp"
  implementation_model: "google/gemini-2.0-flash-exp"
  
  # Or use other PDF-capable models:
  # planning_model: "anthropic/claude-3-5-sonnet"
  # planning_model: "openai/gpt-4o"
```

## 🚀 Usage

### Basic Usage

Simply provide a PDF file path instead of markdown:

```python
from paper2sim.workflows.paper2sim_workflow import Paper2SimWorkflow
from utils.llm_utils import get_preferred_llm_class

# Initialize workflow
llm_factory = get_preferred_llm_class()
workflow = Paper2SimWorkflow(llm_factory)

# Run pipeline with PDF input
results = await workflow.run_full_pipeline(
    paper_path="papers/my_paper.pdf",  # PDF instead of .md
    project_name="my_simulation"
)
```

### Command-Line Interface

```bash
# Run paper2sim with PDF
python -m paper2sim.main --paper papers/my_paper.pdf --output ./output

# The system will automatically detect PDF format and use appropriate models
```

### Phase 1 Only (Extract Game Model)

```python
from paper2sim.agents.theorist import TheTheoristAgent

theorist = TheTheoristAgent(llm_factory)

# Extract from PDF
game_model = await theorist.extract_game_model("papers/signaling_game.pdf")

# The PDF is sent directly to the LLM, preserving all mathematical notation
```

## 📊 Supported Models

Models with native PDF support available via OpenRouter:

| Model | Provider | PDF Support | Best For |
|-------|----------|-------------|----------|
| `google/gemini-2.0-flash-exp` | Google | ✅ Excellent | General use, fast |
| `google/gemini-2.5-pro` | Google | ✅ Excellent | Complex papers |
| `google/gemini-3-pro` | Google | ✅ Excellent | Latest model |
| `anthropic/claude-3-5-sonnet` | Anthropic | ✅ Good | Reasoning-heavy |
| `openai/gpt-4o` | OpenAI | ✅ Good | Vision-based |

The system automatically selects a PDF-capable model based on your configuration.

## ⚙️ Advanced Configuration

### Force Specific Model

```python
# Force a specific model for PDF processing
game_model = await theorist.extract_game_model(
    paper_path="paper.pdf",
    force_pdf_model="google/gemini-3-pro"
)
```

### File Size Limits

Default limit: 20 MB per PDF

To handle larger files, modify in your code:

```python
from tools.pdf_processor import PDFProcessor

# Prepare with custom size limit
pdf_data = PDFProcessor.prepare_pdf_for_llm(
    "large_paper.pdf",
    max_size_mb=30.0  # 30 MB limit
)
```

## 🔍 How It Works

### Architecture

```
PDF File
   │
   ├─> PDFProcessor.encode_pdf_to_base64()
   │   └─> Base64 encoded data
   │
   ├─> TheTheoristAgent._extract_from_pdf()
   │   ├─> Builds prompt with extraction instructions
   │   ├─> Packages PDF as inline_data
   │   └─> Sends to OpenRouter API
   │
   └─> OpenRouter → Gemini/Claude/GPT-4o
       └─> Returns structured game model JSON
```

### Automatic Detection

The system automatically detects PDF files:

```python
# In theorist.py
if PDFProcessor.is_pdf(paper_path):
    return await self._extract_from_pdf(...)  # Use PDF-capable model
else:
    return await self._extract_from_markdown(...)  # Use MCP filesystem
```

### API Format

For Gemini models via OpenRouter:

```json
{
  "model": "google/gemini-2.0-flash-exp",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Extract the game model from this paper..."
        },
        {
          "type": "inline_data",
          "inline_data": {
            "mime_type": "application/pdf",
            "data": "<base64_encoded_pdf>"
          }
        }
      ]
    }
  ]
}
```

## 💡 Best Practices

### 1. Use PDF for Math-Heavy Papers

If your paper contains:
- Complex equations (Bayesian updating, equilibrium conditions)
- Greek letters and special symbols
- Matrix notation or optimization problems

→ **Use PDF input** for best results

### 2. Use Markdown for Text-Heavy Papers

If your paper is mostly text with simple formulas:
- Conceptual papers
- Survey papers
- Papers with simple linear models

→ **Markdown may be sufficient** and faster

### 3. Check Model Costs

Different models have different pricing:
- Gemini Flash: ~$0.10-0.30 per paper
- Claude Sonnet: ~$0.50-1.00 per paper
- GPT-4o: ~$0.30-0.80 per paper

Check current pricing at: https://openrouter.ai/models

### 4. Optimize Token Usage

For very long papers (>50 pages):
- Consider splitting into sections
- Or use the highest-context model (Gemini 2.5 Pro)

## 🧪 Testing

Test your PDF setup:

```bash
# Test PDF processor
python tools/pdf_processor.py papers/test.pdf

# Test OpenRouter configuration
python test_openrouter.py
```

## 🐛 Troubleshooting

### "OpenRouter API key not found"

Solution:
```bash
export OPENROUTER_API_KEY="your-key"
# or add to mcp_agent.secrets.yaml
```

### "PDF file too large"

Solution:
- Compress PDF using online tools
- Or increase `max_size_mb` parameter
- Or split paper into multiple PDFs

### "Model does not support PDF"

Solution:
- Check model name includes a PDF-capable model
- Update `openrouter.planning_model` in config
- Or use `force_pdf_model` parameter

### API Rate Limits

If you hit rate limits:
- Add delays between requests
- Or upgrade to paid OpenRouter tier
- Or use a different provider's model

## 📚 Examples

### Example 1: Physician Testing Game (Signaling)

```python
# PDF with Bayesian updating formulas
results = await workflow.run_full_pipeline(
    paper_path="papers/physician_testing_bayesian.pdf",
    project_name="physician_sim"
)
# ✅ Preserves posterior = (prior × likelihood) / evidence
```

### Example 2: Supply Chain Coordination

```python
# PDF with complex optimization problems
game_model = await theorist.extract_game_model(
    paper_path="papers/supply_chain_contracting.pdf"
)
# ✅ Preserves max E[π] = ∫ (p·q - c·q) f(θ) dθ
```

### Example 3: Auction Mechanism Design

```python
# PDF with extensive game trees and equilibrium characterizations
results = await workflow.run_full_pipeline(
    paper_path="papers/auction_mechanism.pdf",
    force_pdf_model="google/gemini-3-pro"  # Use latest model
)
```

## 📖 Additional Resources

- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Gemini PDF Support](https://ai.google.dev/gemini-api/docs/document-processing)
- [Paper2Sim PRD](./paper2sim/README.md)
- [OpenRouter Setup Guide](../OPENROUTER_SETUP.md)

## 🔄 Migration Guide

### From Markdown to PDF

If you've been using markdown files:

**Before:**
```python
workflow.run_full_pipeline(paper_path="paper.md")
```

**After:**
```python
# Just change the file extension - everything else stays the same!
workflow.run_full_pipeline(paper_path="paper.pdf")
```

No other code changes needed! The system auto-detects the format.

## 🎓 Technical Details

### PDF Encoding

PDFs are encoded as base64 for API transmission:
- Adds ~33% to file size
- But preserves binary data exactly
- Models decode and render internally

### Model Context Windows

| Model | Context Window | Recommended PDF Size |
|-------|----------------|---------------------|
| Gemini 2.0 Flash | 1M tokens | Up to 100 pages |
| Gemini 2.5 Pro | 2M tokens | Up to 200 pages |
| Claude 3.5 Sonnet | 200K tokens | Up to 50 pages |

### Performance

- **PDF Processing Time**: 30-60 seconds for typical paper
- **Cost**: $0.10-1.00 per paper depending on model
- **Accuracy**: Higher for formulas vs. text conversion

## 🚦 Status

- ✅ PDF detection and encoding
- ✅ OpenRouter integration
- ✅ Gemini model support
- ✅ Theorist agent PDF support
- ✅ Critic agent PDF support
- ⏳ Batch processing multiple PDFs
- ⏳ PDF page range selection
- ⏳ Direct Gemini API (without OpenRouter)

---

**Ready to process your first PDF paper?** 

Run: `python -m paper2sim.main --paper your_paper.pdf`
