"""Unit tests for CRUD operations using an isolated in-memory SQLite database."""
import pytest
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src import crud
from src.schemas import ProductCreate, ProductUpdate


@pytest.fixture(name="session")
def session_fixture():
    """Create an isolated, in-memory SQLite database session for fast unit testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_create_product(session: Session):
    """Test successful insertion of a product into the database."""
    product_in = ProductCreate(
        name="Wireless Mouse",
        description="Ergonomic wireless mouse with 2.4GHz USB receiver",
        price=29.99,
        stock=150,
    )
    created = crud.create_product(session=session, product_in=product_in)
    assert created.id is not None
    assert created.name == "Wireless Mouse"
    assert created.description == "Ergonomic wireless mouse with 2.4GHz USB receiver"
    assert created.price == 29.99
    assert created.stock == 150


def test_get_products_empty(session: Session):
    """Test fetching products when catalog is empty."""
    products = crud.get_products(session=session)
    assert len(products) == 0


def test_get_products_pagination(session: Session):
    """Test pagination with skip and limit."""
    for i in range(5):
        crud.create_product(
            session=session,
            product_in=ProductCreate(
                name=f"Product {i}",
                description=f"Description for product {i}",
                price=10.0 + i,
                stock=5 * (i + 1),
            ),
        )

    all_products = crud.get_products(session=session, skip=0, limit=10)
    assert len(all_products) == 5

    subset = crud.get_products(session=session, skip=2, limit=2)
    assert len(subset) == 2
    assert subset[0].name == "Product 2"
    assert subset[1].name == "Product 3"


def test_get_product_by_id(session: Session):
    """Test retrieving product by ID, both existing and non-existent."""
    product_in = ProductCreate(
        name="Mechanical Keyboard",
        description="RGB backlit mechanical gaming keyboard with blue switches",
        price=89.99,
        stock=45,
    )
    created = crud.create_product(session=session, product_in=product_in)
    fetched = crud.get_product_by_id(session=session, product_id=created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "Mechanical Keyboard"

    # Non-existent ID
    assert crud.get_product_by_id(session=session, product_id=9999) is None


def test_update_product(session: Session):
    """Test updating existing product attributes."""
    product_in = ProductCreate(
        name="USB-C Hub",
        description="7-in-1 multi-port adapter",
        price=39.99,
        stock=50,
    )
    created = crud.create_product(session=session, product_in=product_in)

    # Partial update
    update_data = ProductUpdate(price=34.99, stock=40)
    updated = crud.update_product(
        session=session, db_product=created, product_in=update_data
    )
    assert updated.price == 34.99
    assert updated.stock == 40
    assert updated.name == "USB-C Hub"


def test_delete_product(session: Session):
    """Test deleting a product from the database."""
    product_in = ProductCreate(
        name="Laptop Stand",
        description="Adjustable aluminum ergonomic laptop stand",
        price=49.99,
        stock=25,
    )
    created = crud.create_product(session=session, product_in=product_in)
    product_id = created.id

    crud.delete_product(session=session, db_product=created)
    assert crud.get_product_by_id(session=session, product_id=product_id) is None
