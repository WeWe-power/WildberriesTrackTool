## WILDBERRIES PRODUCT CHANGES TRACKER

#### Briefly about project: 
- Product was created to track changes in wildberries product over time
- User can add an item to track list, information about this item will be collected every hour, then it can be accessed by an api endpoint 

To run app in development:
- First step: build the project with following command
```
docker-compose -f docker-compose.dev.yaml up -d --build
```
- Second step: run the project with following command
```
docker-compose -f docker-compose.dev.yaml up
```
- Or if you want to run app just after it was built, then use first command without -d flag:
```
docker-compose -f docker-compose.dev.yaml up --build
```
URLS:
- localhost:8000/admin : Django admin panel
- localhost:8000/api/docs/swagger : API docs swagger UI
- localhost:5050 : PGadmin
- localhost:8888 : Flower - celery task monitoring tool
- localhost:4444 : Selenium hub

Admin credentials:
 -  email: admin@gmail.com
 -  username: admin
 -  password: admin
