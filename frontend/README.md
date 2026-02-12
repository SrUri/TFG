# Erasmus Comparator

- Frontend: React + Vite
- Backend: FastAPI (Python)

### Requisitos:
- Homebrew
- Node.js + npm
- Python 3.9+

# Pasos:

```bash
brew install node python

# FRONTEND
cd frontend
npm install
npm run dev

# BACKEND
cd ../backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload

```

## Uso

1. Introduce las URLs de dos guías docentes (en PDF).
2. Introduce el nombre de una asignatura contenida en la primera.
3. Obtendrás una lista ordenada de asignaturas similares en la segunda guía.