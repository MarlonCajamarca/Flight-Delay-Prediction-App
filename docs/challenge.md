
# Workflow
1. Install make in the server/local machine
2. Install git in the server/local machine
3. Clone the repository
4. Push all project files into `main` branch
5. Create `dev` branch from `main` branch
6. Git fetch and checkout `dev` branch
7. Execute `make venv` to create a virtual environment
8. activate the virtual environment
9. Execute `make install` to install all dependencies
10. Test all imports in `exploration.ipynb` file
11. Start documenting insights and approaches for decision-taking in `challenge.md` file
12. Git add, commit and push all changes to `dev` branch
13. Implement and past test for challenge Part 1 and push to `dev` branch
14. Implement and past test for challenge Part 2 and push to `dev` branch
15. Implement and past test for challenge Part 3 and push to `dev` branch
16. Make a PR from `dev` branch to `main` branch
17. Implement Ci/CD pipeline for `main` branch

# Challenge Part 1
## Data Preprocessing Pipeline
* Using shuffled data for crafting the training features
  * The data used for model beanchmarking and feature importance detection in the `exploration.ipynb` file was not shuffled. This could lead to a biased model. To fix this, the data was shuffled before crafting the training features.
  * By shuffling the data, the feature importance set of the model changed (Check cell #59 of the aforementioned notebook). As a result, the list of `top_10_features` was updated in the training and testing functions to:
    ```
    "OPERA_Latin American Wings", 
    "MES_7",
    "OPERA_Grupo LATAM",
    "OPERA_Sky Airline",
    "MES_10",
    "MES_8",
    "MES_12",
    "TIPOVUELO_I",
    "OPERA_JetSmart SPA",
    "MES_4"
    ```

## Model Fitting Pipeline
* For improving the model recall and passing the `test_model_fit` test, a basic hyperparameter tuning approach (using Grid Search) was taken instead of the approach sugested by the DS (using just class weights throug manual calculation of scaling ratio and no hyperparamter tuning). A cross validation scheam was also added for a better model training schema. The hyperparameter searched and tuned were:
```
# Inverse of regularization strength
'C': [0.001, 0.01, 0.1, 1, 10, 100],
# Algorithm to use in the optimization problem
'solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],
# Weights associated with classes in the form {class_label: weight}
'class_weight': ['balanced'] 
```
* The trained model was stored in a newly created `models` folder. The model was saved using the `pickle` library and was called `model.pkl`. This would be the model to be served for serving predictions. Even thoug it is not a good practice to upload ML models to repository, the fitted model was only 1.0K in size. Additionally, in the name of transparency the model has been uploaded for the evaluators to track all artifacts geenrated during the model operationalization challenge. Therefore, the trained model was pushed to the repository.

## Model Selection Pipeline
* `XGBCclassifier` VS `LogisticRegression`
  * Based on the results from the DS and the nature of the problem, given that the primary focus on predicting delayed flights (class label "1") as accurately as possible, the Logistic Regression model seems slightly better because it has a marginally higher __recall__. This means it can detect a slightly higher proportion of actual delayed flights.
  * However, it's essential to note that the differences between the two models are minimal. It may be worth considering other factors like the training time, ease of deployment, interpretability, and any business costs associated with false positives (incorrectly predicting a flight as delayed) for a real-world application.

# Challenge Part 2
* A FastAPI API was created in the `challenge/api.py` file. The API has two endpoints:
  * `/predict` endpoint: This endpoint accepts a POST request with a JSON payload containing the features of a flight. The API then returns a JSON response containing the predicted class label for the flight (0 for non-delay flight & 1 for delayed flight).
  * `/health` endpoint: This endpoint accepts a GET request and returns a JSON response containing the status of the API.
  * The API was tested using the `api-test` test. The test passed.
  
# Challenge Part 3

## Approach 1: Zipped Deployment Package
### API Packaging
Deploying FastAPI API in AWS Lambda using zipped deployment package.
* Create a requirements-prod.txt listing the production dependencies only
```
fastapi~=0.103.1
pydantic~=2.3.0
scikit-learn~=1.3.0
pandas~=2.1.0
mangum~=0.17.0
```
* Create a deployment package by running the following commands in the terminal:
```
# Creating lib folder and installing all production dependencies. 
# Do not forget to add lib folder into gitignore file
pip install -t lib -r requirements-prod.txt

# Create the zip file that is going to be uploaded to AWS Lambda as deployment package. Starting from the lib folder.
# Do not forget to add lambda_function.zip file into gitignore file
(cd lib; zip ../lambda_function.zip -r .)

# Add api.py file to the root of the zip file
zip -u lambda_function.zip challenge/api.py -j

# Add model.joblib file to the root of the zip file
zip -u lambda_function.zip model/model.pkl -j
```
### API Deployment
* Create a new Lambda function in AWS console (python 3.10 runtime)
* Upload zip file to S3 bucket and use zipped file as deployment package to Lambda Code Source

### Conclusion
* The zipped deployment package approach is not recommended for deploying FastAPI APIs in AWS Lambda. The unzipped deployment package size is 310.5 MB, which is way above the 250 MB limit for AWS Lambda. The deployment package size can be reduced by removing the `scikit-learn` library from the requirements-prod.txt file. However, this would mean that the model cannot be loaded in the API. Therefore, this approach is not recommended.

## Appraoch 2: Container Image
### FastAPI Docker Image
* Create a containerized FastAPI API using the following Dockerfile
  * Build the Docker image for dev environment
```
docker build -f Dockerfile-dev -t flight-delay-pred-app-lambda .
```
  * Build the Docker image for prod environment
```
docker build -f Dockerfile-prod -t flight-delay-pred-app-lambda .
```
* Run the Docker container for development environment
```
docker run -d --name flight-delay-app-container -p 8080:8080 flight-delay-pred-app-lambda
```
* Test the API: All api-stress tests passed using dev containerized FastAPI API

### Push Dockerized API to AWS ECR
* Create a new repository in AWS ECR
```
flight-delay-pred-app-lambda
```
* Authenticate Docker client to AWS ECR
```
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 245582572290.dkr.ecr.us-east-1.amazonaws.com
```
* Tag the Docker image
```
docker tag flight-delay-pred-app-lambda:latest 245582572290.dkr.ecr.us-east-1.amazonaws.com/flight-delay-pred-app-lambda:latest
```
* Push the Docker image to AWS ECR
```
docker push 245582572290.dkr.ecr.us-east-1.amazonaws.com/flight-delay-pred-app-lambda:latest
```
### Deploy API in AWS Lambda from ECR
* Create a new Lambda function in AWS console from ECR container image flight-delay-pred-app-lambda:latest
* configure, test and get the Lambda Function URL working properly
* Test the Deployed API: All api-stress tests passed using AWs Lambda API (Lambda Function URL used for stress-test available in makefile)
* The results from the stress test are available in the `reports` folder.
### Conclusion
* The container image approach is recommended for deploying FastAPI APIs in AWS Lambda. The unzipped deployment package size is 310.5 MB, which is way above the 250 MB limit for AWS Lambda. However, the container image size is only 0.5 GB, which is well below the 10 GB limit for AWS Lambda. Therefore, this approach is recommended for majority of ML-based APIs

# Challenge Part 4
## CI/CD Pipeline
* A CI/CD pipeline was created using GitHub Actions. The pipeline is triggered when a new commit is pushed to the `main` branch. The pipeline consists of the following steps:
  * Checkout the repository
  * Setup Python 3.10
  * Install dependencies
  * Run tests
  * Build Docker image
  * Push Docker image to AWS ECR
  * Deploy Docker image to AWS Lambda

