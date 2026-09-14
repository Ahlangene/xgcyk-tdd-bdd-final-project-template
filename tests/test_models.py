# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, init_db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should Read of a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        result = Product.find(product.id)
        self.assertEqual(result.id, product.id)
        self.assertEqual(result.name,product.name)
        self.assertEqual(result.description, product.description)
        self.assertEqual(result.price, product.price)

    def test_update_a_product(self):
        """It should Update a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        product.description="This product has been updated to describe the product"
        product.update()
        result = product.find(product.id)
        self.assertEqual(result.description,product.description)

    def test_delete_a_product(self):
        """It should delete a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        self.assertEqual(len(Product.all()),1)
        product.delete()
        self.assertEqual(len(Product.all()),0)

    def test_list_all_products(self):
        """It should List all Products in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        # Create 5 Products
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # See if we get back 5 products
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        name = products[0].name
        count = len([product for product in products if product.name == name])
        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, name)


    def test_find_by_availability(self):
        """It should Find Products by Availability"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        available = products[0].available
        count = len([product for product in products if product.available == available])
        found = Product.find_by_availability(available)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_by_category(self):
        """It should Find Products by Category"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        category = products[0].category
        count = len([product for product in products if product.category == category])
        found = Product.find_by_category(category)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.category, category)

    def test_find_by_price(self):
        """It should Find Products by Price"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        price = products[0].price
        count = len([product for product in products if product.price == price])
        found = Product.find_by_price(price)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.price, price)

    def test_find_by_price_string(self):
        """It should Find Products by Price when price is a string"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        price = str(products[0].price)
        count = len([product for product in products if str(product.price) == price])
        found = Product.find_by_price(price)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(str(product.price), price)

    def test_find_by_price_quoted_string(self):
        """It should Find Products by Price when price is a quoted string"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        price = f'"{products[0].price}"'
        count = len([product for product in products if str(product.price) == products[0].price.__str__()])
        found = Product.find_by_price(price)
        self.assertEqual(found.count(), count)

    def test_find_not_found(self):
        """It should not Find a Product that does not exist"""
        product = Product.find(9999)
        self.assertIsNone(product)

    def test_update_a_product_no_id(self):
        """It should not Update a Product with no ID"""
        product = ProductFactory()
        product.id = None
        with self.assertRaises(DataValidationError):
            product.update()

    def test_serialize_a_product(self):
        """It should Serialize a Product"""
        product = ProductFactory()
        product.create()
        serial_product = product.serialize()
        self.assertIsNotNone(serial_product)
        self.assertEqual(serial_product["id"], product.id)
        self.assertEqual(serial_product["name"], product.name)
        self.assertEqual(serial_product["description"], product.description)
        self.assertEqual(serial_product["price"], str(product.price))
        self.assertEqual(serial_product["available"], product.available)
        self.assertEqual(serial_product["category"], product.category.name)

    def test_deserialize_a_product(self):
        """It should Deserialize a Product"""
        product = ProductFactory()
        product.create()
        serial_product = product.serialize()
        new_product = Product()
        new_product.deserialize(serial_product)
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(new_product.price, product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_deserialize_missing_data(self):
        """It should not Deserialize a Product with missing data"""
        product = ProductFactory()
        serial_product = product.serialize()
        del serial_product["name"]
        new_product = Product()
        with self.assertRaises(DataValidationError):
            new_product.deserialize(serial_product)

    def test_deserialize_bad_data(self):
        """It should not Deserialize bad data"""
        data = "this is not a dictionary"
        product = Product()
        with self.assertRaises(DataValidationError):
            product.deserialize(data)

    def test_deserialize_bad_available(self):
        """It should not Deserialize a bad available value"""
        product = ProductFactory()
        serial_product = product.serialize()
        serial_product["available"] = "not a boolean"
        new_product = Product()
        with self.assertRaises(DataValidationError):
            new_product.deserialize(serial_product)

    def test_deserialize_bad_category(self):
        """It should not Deserialize a bad category value"""
        product = ProductFactory()
        serial_product = product.serialize()
        serial_product["category"] = "NOT_A_CATEGORY"
        new_product = Product()
        with self.assertRaises(DataValidationError):
            new_product.deserialize(serial_product)

    def test_init_db_function(self):
        """It should initialize the database using the module-level init_db"""
        from service.models import init_db
        init_db(app)
        # If no exception was raised, the database was initialized
        self.assertTrue(True)

    def test_bad_category_enum_access(self):
        """It should raise DataValidationError for invalid category enum access"""
        product = ProductFactory()
        serial_product = product.serialize()
        serial_product["category"] = "INVALID_ENUM_VALUE"
        new_product = Product()
        with self.assertRaises(DataValidationError):
            new_product.deserialize(serial_product)
