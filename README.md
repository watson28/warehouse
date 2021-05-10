# Warehouse example application
This small application manages the inventory and products of a warehouse.

## Getting started
The easiest way of running the application is using docker-compose.

```shell
docker-compose up
```

Docker-compose will instance a Postgres DB and a Django web API.

## How to use it
The Django project provides the following Web API endpoints to manage the warehouse:

| URL                             | HTTP method | description |
| ------------------------------- | ----------- | ----------- |
| `inventory/articles/upload`     | POST        | Upload a JSON file with articles and stocks. |
| `inventory/products/upload`     | POST        | Upload a JSON file with products and articles need it to make a single unit of a product. |
| `inventory/products/availability` | GET       | get the existing products and its availaible quantity based on the current existing articles. |
| `products/<int:product_id>/sell`| POST        | sell one unit of a product and update the inventory. |

You can use the [Postman collection](https://www.postman.com/collection/) `warehouse.postman_collection.json` to easily interact with the Web API.

## Application structure

The Application uses the [Django](https://www.djangoproject.com/) web framework. There are two modules: 'warehouse` and 'inventory'.

'warehouse' module is the default module created by Django for the project's configuration.

'inventory' module is where the actual functionality lives. Several components compose the module:
- *urls.py*: is where the API endpoint configuration happens. It maps URLs / HTTP methods to controllers (Django views).
- *views.py*: These are controllers that handle requests to the application. Their responsibility is to manage the HTTP-related communication work and to call business logic objects.
- *business_logic.py*: This where the requirements of a business operation implemented with the repository layer's help. They Provide high-level API for business operations. They persist information, validate data based on business rules, and return business data objects.
- *upload_parsers.py*: Objects used to transform serialized JSON objects to business data objects.
- *business_data_objects.py*: It contains data objects used for transporting information between different layers in a business operation.
- *repositories.py*: It abstracts the complexity of complex queries to the DB and, more importantly, sets a boundary to using ORM objects to avoid unresponsible uses of their methods.
- *models.py*: This is where the domain models live. They use Django ORM to implement constraints and persist the information in the DB.

## Future improvements
- Add testing
- ~~Configure static typing check~~
- Add pipeline
- Add simple frontend
