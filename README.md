# Z Brands Product Catalog by Adalberto Vazquez

This is a basic catalog system built with the FastAPI framework that is designed to manage products. It allows to **create your own user** and depending on the type of you users, you can perform other actions:
- Admin users:
    - Create other admin users and update/delete existing users.
    - Retrieve/Create/Update/Delete data about products
    - Receive notifications of the changes in the product catalog on a daily basis.
- Non-admin users:
    - Create other non-admin users
- Anonymous users:
    - Retrieve the information about the products

Another cool feature is that you can access some endpoints to get a detailed report of how many times a product was retrieved by an anonymous user, for more info about it please visit the `/docs` endpoint that is auto-generated with FastAPI.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)

## Features

### Products

- **Product Info**: Products have basic details:
  - Name
  - SKU
  - Price
  - Brand

### Users

There are three types of users:

1. **Admin Users**
   - Can create, update, and delete products.
   - Manage (create, update, delete) other admin users.
   - Get notified whenever there's a change in a product with a daily mail.

2. **Non-Admin Users**
   - Create other non-admin users

3. **Anonymous Users**
   -  Don't have an account and don't need to login and get a token
   - Can only view product details.
   - Can't make changes to products or the system.

### Other Features

- **Notifications**: Admin users get notified about product changes with a daily mail, this was done using MailHog just for testing purposes.
- **Analytics**: The system tracks the number of times a product is queried by anonymous users and you can get the data using the `product-views/` endpoints.

## Installation

To run this project, you'll be using Docker for containerization.

### Initial Setup
1. Clone the repository: `git clone [repository_link]`
2. Navigate to the directory: `cd [directory_name]`
4. Create an `.env` file with the shared data. (To make this easier for now, please copy them [here](https://drive.google.com/file/d/1CUElm5JWZ1tcaFhWhtJRyJTdPK2h7iMy/view?usp=sharing) but this should be shared with only a few people ) 
3. Install docker

### To Run the Application
Run the following command: 
```
docker-compose up --build
```

### To run the tests
Run the following command:
```
docker-compose -f docker-compose.tests.yml up --build
```

## Usage

Visit the `/docs` endpoint to have a detailed explanation about each endpoint
