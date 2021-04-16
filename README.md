# Warehouse example application
This small application manages the inventory and products of a warehouse.

## Getting started
The easiest way of running the application is using docker-compose.

```shell
docker-compose up
```

This will instance a Postgres DB and a Django web api.

## How to use it
The django project provides the following Web API endpoints to manage the warehouse:

| URL                             | HTTP method | description |
| ------------------------------- | ----------- | ----------- |
| `inventory/articles/upload`     | POST        | Upload a JSON file with articles and stocks. |
| `inventory/products/upload`     | POST        | Upload a JSON file with products and articles need it to make a single unit of a product. |
| `inventory/products/availability` | GET       | get the existing products and its availaible quantity based on the current existing articles. |
| `products/<int:product_id>/sell`| POST        | sell one unit of a product and update the inventory. |

You can use the [Postman collection](https://www.postman.com/collection/) `warehouse.postman_collection.json` to easily interact with the Web API.

## Application structure

The Application uses [Django](https://www.djangoproject.com/) web framework. There are two modules: 'warehouse` and 'inventory'.

'warehouse' module is the default module created by Django for the project's configuration.

'inventory' module is where the actual functioanlity lives. The module is composed by several components:
- *urls.py*: is where the API endpoint configuration happens. It maps URLs / HTTP methods to controllers (Django views).
- *views.py*: These are controllers that handle requests to the application. Their responsability is to handle the HTTP related communication work and to call business logic objects.
- *business_logic.py*: This where the requirements of a business operation are implemented with the help of the repository layer. Provides high level API for business operations. They persist information, validate data based on business rules and return business data objects.
- *upload_parsers.py*: objects used to transform serialized JSON objects to business data objects.
- *business_data_objects.py*: Data objects used to tranport information between different layers in a business operation.
- *repositories.py*: Abstract the complexy of complex queries to the DB and more importanly set a boundary to the use of ORM objects in order to avoid unresponsable uses of their methods.
- *models.py*: This is where the domain models live. They use Django ORM to implement constraints and persist the information in the DB.

## Future improvements
- Add testing
- Configure static typing check
- Add simple frontend