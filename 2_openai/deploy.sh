#!/bin/bash
# Deploy Research Assistant to Hugging Face Spaces

echo "🚀 Deploying Research Assistant to Hugging Face Spaces"
echo ""
echo "⚠️  IMPORTANT: When prompted for Space name, use a valid format:"
echo "   ✅ Use: research-assistant"
echo "   ✅ Use: ai-research-tool"
echo "   ❌ DON'T use: Research Assistant (no spaces!)"
echo ""
echo "Starting deployment..."
echo ""

cd "$(dirname "$0")"
uv run --python 3.12 gradio deploy --app-file research_assistant.py

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "1. Go to your Space on Hugging Face"
echo "2. Click Settings → Repository secrets"
echo "3. Add: OPENAI_API_KEY = your-api-key"
echo "4. Wait for Space to rebuild (30 seconds)"
echo "5. Test your app!"

