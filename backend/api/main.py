from fastapi import FastAPI

from api.routes import router
from core.state.database import Base, engine
from core.state.logging import configure_logging

configure_logging()
Base.metadata.create_all(bind=engine)

app = FastAPI(title='AI Marketing Orchestration System', version='1.0.0')
app.include_router(router)


@app.get('/health')
def health_check():
    return {'status': 'ok'}
