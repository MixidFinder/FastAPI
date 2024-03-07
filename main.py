from datetime import datetime

import databases
import uvicorn
import sqlalchemy

from fastapi import FastAPI
from pydantic import BaseModel, Field
from werkzeug.security import generate_password_hash, check_password_hash

app = FastAPI()

DATABASE_URL = "sqlite:///mydatabase.db"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String(32), nullable=False),
    sqlalchemy.Column('surname', sqlalchemy.String(32), nullable=False),
    sqlalchemy.Column('email', sqlalchemy.String(64), nullable=False),
    sqlalchemy.Column('password', sqlalchemy.String(512), nullable=False)
)

products = sqlalchemy.Table(
    'products',
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('product_name', sqlalchemy.String(32), nullable=False),
    sqlalchemy.Column('description', sqlalchemy.String(1000)),
    sqlalchemy.Column('price', sqlalchemy.Float, nullable=False)
)

orders = sqlalchemy.Table(
    'orders',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('user_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('product_id', sqlalchemy.Integer, sqlalchemy.ForeignKey('products.id')),
    sqlalchemy.Column('order_date', sqlalchemy.DateTime, default=datetime.utcnow()),
    sqlalchemy.Column('order_status', sqlalchemy.String, default='In progress')
)

engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
metadata.create_all(engine)


class User(BaseModel):
    id: int = Field(primary_key=True)
    name: str = Field(max_length=32, nullable=False)
    surname: str = Field(max_length=64, nullable=False)
    email: str = Field(max_length=128, nullable=False, unique=True)
    password: str = Field(nullable=False)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Product(BaseModel):
    id: int = Field(primary_key=True)
    product_name: str = Field(max_length=32, nullable=False)
    description: str = Field(max_length=1000)
    price: float = Field(gt=0, default=100000, nullable=False)


class Order(BaseModel):
    id: int = Field(primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    order_date: datetime = Field(default=datetime.utcnow)
    order_status: str = Field(max_length=64, default="In progress")


@app.get("/fake_users/{count}")
async def create_f_users(count: int):
    for i in range(count):
        query = users.insert().values(name=f'user{i}',
                                      surname=f'user{i}',
                                      email=f'mail{i}@mail.ru',
                                      password=generate_password_hash('pass' + str(i))
                                      )

        await database.execute(query)
    return {'message': f'{count} fake users create'}


@app.get("/fake_products/{count}")
async def create_f_products(count: int):
    for i in range(count):
        query = products.insert().values(product_name=f'product{i}',
                                         description=f'desc{i}',
                                         price=100.00 + i
                                         )
        await database.execute(query)
    return {'message': f'{count} fake products create'}


@app.get("/fake_orders/{count}")
async def create_f_orders(count: int):
    for i in range(count):
        query = orders.insert().values(user_id=i,
                                       product_id=i,
                                       )
        await database.execute(query)
    return {'message': f'{count} fake orders create'}


if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
