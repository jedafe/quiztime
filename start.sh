#!/bin/bash
# QuizTime production server control
# Usage: ./start.sh [start|stop|status|restart]

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

start() {
  echo "Starting backend (prod)..."
  cd "$BACKEND_DIR"
  nohup ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 > /tmp/quiztime-backend.log 2>&1 &
  echo "  PID: $!  →  http://localhost:8000/docs"

  echo "Building frontend..."
  cd "$FRONTEND_DIR"
  npm run build 2>&1 | tail -5

  echo "Starting frontend (prod)..."
  nohup npm run preview > /tmp/quiztime-frontend.log 2>&1 &
  echo "  PID: $!  →  http://localhost:4173"

  sleep 2
  echo ""
  echo "Prod servers started. Run '$0 stop' to shut down."
}

stop() {
  echo "Stopping servers..."
  killed=0
  for port in 8000 4173; do
    pid=$(lsof -t -i:$port 2>/dev/null)
    if [ -n "$pid" ]; then
      kill $pid 2>/dev/null
      echo "  Killed process on port $port (PID $pid)"
      killed=1
    fi
  done
  if [ $killed -eq 0 ]; then
    echo "  No servers running."
  else
    echo "Done."
  fi
}

status() {
  for port in 8000 4173; do
    pid=$(lsof -t -i:$port 2>/dev/null)
    if [ -n "$pid" ]; then
      echo "Port $port: running (PID $pid)"
    else
      echo "Port $port: stopped"
    fi
  done
}

case "${1:-start}" in
  start)    start ;;
  stop)     stop ;;
  status)   status ;;
  restart)  stop; sleep 1; start ;;
  *) echo "Usage: $0 {start|stop|status|restart}" ;;
esac
