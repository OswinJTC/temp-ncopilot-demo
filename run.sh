export GOOGLE_APPLICATION_CREDENTIALS="$HOME/Desktop/Jubo 智齡科技/key/sa-oswinchen1.json"
echo $GOOGLE_APPLICATION_CREDENTIALS
uvicorn app.main:app --host 0.0.0.0 --port 8000 