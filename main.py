from fastapi import FastAPI
from contextlib import asynccontextmanager
from ariadne import load_schema_from_path, make_executable_schema
from ariadne.asgi import GraphQL
from database import init_db
from resolvers import resolvers

# Lifespan handler menggantikan @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("API siap! Akses GraphiQL di http://localhost:8000/graphql")
    yield

app = FastAPI(title="Star Wars GraphQL API", lifespan=lifespan)

# Inisialisasi GraphQL schema
type_defs = load_schema_from_path("schema.graphql")
schema = make_executable_schema(type_defs, resolvers)
graphql_app = GraphQL(schema, debug=True)

# Mount GraphQL endpoint
app.mount("/graphql", graphql_app)

# Endpoint root
@app.get("/")
async def root():
    return {"message": "Selamat datang di Star Wars GraphQL API! Buka /graphql untuk mulai."}
