## WILDBERRIES PRODUCT CHANGES TRACKER

#### Briefly about project: 
- Allows users to track changaes is wildberries products selected by them over time

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