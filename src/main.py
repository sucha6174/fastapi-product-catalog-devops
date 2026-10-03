"""FastAPI Product Catalog Application Main Entrypoint."""
import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from src import crud
from src.database import create_db_and_tables, get_session
from src.schemas import ProductCreate, ProductResponse, ProductUpdate

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager with fail-fast database initialization."""
    logger.info("Starting up Product Catalog API...")
    try:
        create_db_and_tables()
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.critical("Fatal error during database initialization: %s", e)
        raise e
    yield
    logger.info("Shutting down Product Catalog API...")


# Initialize FastAPI application
app = FastAPI(
    title="Product Catalog API",
    description="A scalable, production-grade REST API for managing product catalogs built with FastAPI, PostgreSQL, and Docker.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    tags=["Root"],
    summary="API Root Information",
    description="Returns basic information and documentation links for the Product Catalog API.",
)
def read_root():
    """Root endpoint returning service status and docs URL."""
    return {
        "service": "Product Catalog API",
        "version": "1.0.0",
        "status": "online",
        "documentation": "/docs",
    }


@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Liveness and readiness health check probe for container orchestrators and load balancers.",
    status_code=status.HTTP_200_OK,
)
def health_check():
    """Health check endpoint for ECS and Docker probes."""
    return {"status": "healthy", "service": "product-catalog-api"}


@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Products"],
    summary="Create a New Product",
    description="Creates a new product record in the catalog and returns the stored entity with its generated ID.",
)
def create_new_product(
    product: ProductCreate,
    session: Session = Depends(get_session),
):
    """Create a new product in the database."""
    return crud.create_product(session=session, product_in=product)


@app.get(
    "/products",
    response_model=List[ProductResponse],
    status_code=status.HTTP_200_OK,
    tags=["Products"],
    summary="List All Products",
    description="Fetches a list of product catalog items with optional pagination parameters.",
)
def list_products(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
):
    """Retrieve all products from the catalog."""
    return crud.get_products(session=session, skip=skip, limit=limit)


@app.get(
    "/products/{id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    tags=["Products"],
    summary="Get Product by ID",
    description="Fetches details of a single product using its unique database ID.",
)
def get_product(
    id: int,
    session: Session = Depends(get_session),
):
    """Retrieve a single product by ID or return 404."""
    product = crud.get_product_by_id(session=session, product_id=id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {id} not found",
        )
    return product


@app.put(
    "/products/{id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    tags=["Products"],
    summary="Update an Existing Product",
    description="Updates specified attributes of an existing product. Returns the updated product or 404.",
)
def update_existing_product(
    id: int,
    product_update: ProductUpdate,
    session: Session = Depends(get_session),
):
    """Update fields on an existing product or return 404."""
    db_product = crud.get_product_by_id(session=session, product_id=id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {id} not found",
        )
    return crud.update_product(
        session=session, db_product=db_product, product_in=product_update
    )


@app.delete(
    "/products/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Products"],
    summary="Delete a Product",
    description="Removes a product from the database by ID. Returns HTTP 204 on success or 404 if not found.",
)
def delete_existing_product(
    id: int,
    session: Session = Depends(get_session),
):
    """Delete a product by ID or return 404."""
    db_product = crud.get_product_by_id(session=session, product_id=id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {id} not found",
        )
    crud.delete_product(session=session, db_product=db_product)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
