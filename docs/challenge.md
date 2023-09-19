
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
## CI/CD Pipelines using Github Actions
### Continuous Integration Pipeline
A continuous integration pipeline has been implemented using GitHub Actions workflow using the file named `ci.yml`. This workflow is triggered by push events to the `main` branch, pull request events targeting the `main` branch, and manual workflow dispatch events.

The workflow has a single job named `build` that runs on an Ubuntu latest runner. The `build` job consists of several steps that are executed in sequence:

1. The `actions/checkout` action is used to check out the source code from the repository.

2. The `actions/setup-python` action is used to set up a Python environment with version 3.10.

3. The `make venv` command is used to create a virtual environment for the project.

4. The `source .venv/bin/activate` command is used to activate the virtual environment.

5. The `make install` command is used to install the project dependencies.

6. The `make model-test` command is used to run the model tests.

7. The `make api-test` command is used to run the API tests.

By using GitHub Actions, this workflow can be automated and run on every push or pull request, ensuring that the project is always tested and up-to-date.

### Continuous Deployment Pipeline
A continuous deployment pipeline has been implemented using GitHub Actions workflow file named `cd.yml`. This workflow is triggered by push events to the `main` branch, pull request events targeting the `main` branch, and manual workflow dispatch events.

The workflow has two jobs: `deploy` and `test_api`. The `deploy` job runs on an Ubuntu latest runner and consists of several steps that are executed in sequence:

1. The `actions/checkout` action is used to check out the source code from the repository.

2. The `docker build` command is used to build a Docker image for the development environment using the `Dockerfile-dev` file. The image is tagged with the name `flight-delay-pred-app-lambda-dev`.

3. The `docker run` command is used to run the Docker image for the development environment. The container is named `flight-delay-app-container` and is mapped to port `8080` on the host machine.

4. The `docker build` command is used to build a Docker image for the production environment using the `Dockerfile-prod` file. The image is tagged with the name `flight-delay-pred-app-lambda-prod`.
5. __CAVIATS!__
   1. Given that I am using my enterprise/private AWS Credentials, the AWS authorization, tagging and deployment of the Docker image to AWS ECR is not part of this CD pipeline. For evaluating the steps for deploying the Docker image to AWS ECR, please refer to the `Push Dockerized API to AWS ECR`
   2. The AWS Lambda deployment is not part of this CD pipeline. For evaluating the steps for deploying the Docker image to AWS Lambda, please refer to the `Deploy API in AWS Lambda from ECR`.

The `test_api` job runs on an Ubuntu latest runner and depends on the `deploy` job. This job consists of several steps that are executed in sequence:

1. The `actions/checkout` action is used to check out the source code from the repository.

2. The `actions/setup-python` action is used to set up a Python environment with version 3.10.

3. The `make venv` command is used to create a virtual environment for the project.

4. The `source .venv/bin/activate` command is used to activate the virtual environment.

5. The `make install` command is used to install the project dependencies.

6. The `make stress-test` command is used to run stress tests on the API.

# Evaluation Report
## Challenge Part 1
The `model-test` test passed. The model was trained using a basic hyperparameter tuning approach (using Grid Search) instead of the approach sugested by the DS (using just class weights throug manual calculation of scaling ratio and no hyperparamter tuning). A cross validation scheam was also added for a better model training schema. 
## Challenge Part 2
A FastAPI API  was created in the `challenge/api.py` file. The API has two endpoints: `/predict` and `/health`.

The `/predict` endpoint accepts a POST request with a JSON payload containing the features of a flight. The API then returns a JSON response containing the predicted class label for the flight. The predicted class label is either 0 for non-delayed flights or 1 for delayed flights. This endpoint is used to predict whether a flight will be delayed or not based on the input features.

The `/health` endpoint accepts a GET request and returns a JSON response containing the status of the API. This endpoint is used to check the health of the API and ensure that it is running correctly.

The API was tested using the `api-test` test, which passed. This test ensures that the API is functioning correctly and returning the expected results.
## Challenge Part 3
Two different approaches for deploying a FastAPI API in AWS Lambda were tested. The first approach involves creating a zipped deployment package, while the second approach involves creating a container image.

The first approach involves creating a `requirements-prod.txt` file that lists the production dependencies for the API. The dependencies are then installed in a `lib` folder using the `pip install` command. The `lib` folder is then zipped along with the `api.py` and `model.pkl` files to create the deployment package. However, this approach is not recommended for FastAPI APIs in AWS Lambda because the unzipped deployment package size is 310.5 MB, which is above the 250 MB limit for AWS Lambda. Removing the `scikit-learn` library from the `requirements-prod.txt` file can reduce the deployment package size, but this would mean that the model cannot be loaded in the API.

The second approach involves creating a containerized FastAPI API using a Dockerfile. The Dockerfile is used to build a Docker image for the development (`Dockerfile-dev`)and production (`Dockerfile-prod`)environments. 
The Docker container for the development environment is then run using the `docker run` command described in the correponding section. The API is tested on local machine URL using the `api-stress` tests, which passed using the dev containerized FastAPI API. 
Then a production docker image is built using the `Dockerfile-prod` image, which is beaing created following AWS guidelines for building Docker images targeted to AWS Lambda functions. The image is then pushed to AWS ECR and a new Lambda function is (manually) created in AWS console and API is deployed from the ECR container image. The deployed API is then tested using the `api-stress` tests, which passed using the AWS Lambda API. The results from the stress test are available in the `reports` folder.

The second approach is recommended for deploying FastAPI APIs in AWS Lambda because the container image size is only 0.5 GB, which is well below the 10 GB limit for AWS Lambda. This approach is suitable for most ML-based APIs and provides a more efficient and scalable way to deploy FastAPI APIs in AWS Lambda.
## Challenge Part 4
An implementation of CI/CD pipelines using GitHub Actions was used. The pipelines consist of two workflows: a continuous integration pipeline and a continuous deployment pipeline.

The continuous integration pipeline is implemented using the `ci.yml` workflow file. This workflow is triggered by push events to the `main` branch, pull request events targeting the `main` branch, and manual workflow dispatch events. The workflow has a single job named `build` that runs on an Ubuntu latest runner. The `build` job consists of several steps that are executed in sequence, including setting up a Python environment, creating a virtual environment for the project, installing project dependencies, and running model and API tests. By using GitHub Actions, this workflow can be automated and run on every push or pull request, ensuring that the project is always tested and up-to-date.

The continuous deployment pipeline is implemented using the `cd.yml` workflow file. This workflow is triggered by push events to the `main` branch, pull request events targeting the `main` branch, and manual workflow dispatch events. The workflow has two jobs: `deploy` and `test_api`. The `deploy` job runs on an Ubuntu latest runner and consists of several steps that are executed in sequence, including building Docker images for the development and production environments. The `test_api` job runs on an Ubuntu latest runner and depends on the `deploy` job. This job consists of several steps that are executed in sequence, including creating a virtual environment for the project, installing project dependencies, and running stress tests on the API.

However, there are two caveats to this pipeline. Firstly, the AWS authorization, tagging, and deployment of the Docker image to AWS ECR is not part of this CD pipeline. Secondly, the AWS Lambda deployment is not part of this CD pipeline. For evaluating the steps for deploying the Docker image to AWS ECR and AWS Lambda, please refer to the `Push Dockerized API to AWS ECR` and `Deploy API in AWS Lambda from ECR` respectively.

Overall, these CI/CD pipelines provide a robust and efficient way to develop, test, and deploy machine learning-based FastAPI APIs. By using GitHub Actions, these pipelines can be automated and run on every push or pull request, ensuring that the project is always tested and up-to-date.