#!/bin/bash
# QuizTime dev server control
# Usage: ./dev.sh [start|stop|status|restart]

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

start() {
  echo "Starting backend (dev)..."
  cd "$BACKEND_DIR"
  nohup ./venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > /tmp/quiztime-backend.log 2>&1 &
  echo "  PID: $!  →  http://localhost:8000/docs"

  echo "Starting frontend (dev)..."
  cd "$FRONTEND_DIR"
  nohup npm run dev > /tmp/quiztime-frontend.log 2>&1 &
  echo "  PID: $!  →  http://localhost:5173"

  sleep 2
  echo ""
  echo "Dev servers started. Run '$0 stop' to shut down."
}

stop() {
  echo "Stopping servers..."
  killed=0
  for port in 8000 5173; do
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
  for port in 8000 5173; do
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
