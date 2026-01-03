echo ""
echo "✅ Server starting at http://localhost:8001"
echo "📚 API Docs: http://localhost:8001/"
# echo "❤️  Health: http://localhost:8000/api/v2/health/"
echo ""
echo "Press Ctrl+C to stop"
echo ""
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi
# Start server
python3 manage.py runserver 8001