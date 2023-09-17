
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

# Fixes
* Add `xgboost` library to `requirements.txt` file
* Fix incorrect use of Union from the typing module. The correct way to use Union is to provide multiple types separated by commas within square brackets.

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
* The trained model was stored in a newly created `models` folder. The model was saved using the `joblib` library and was called `model.joblib`. This would be the model to be served for serving predictions. Even thoug it is not a good practice to upload ML models to repository, the fitted model was only 1.4K in size. Additionally, in the name of transparency the model has been uploaded for the evaluators to track all artifacts geenrated during the model operationalization challenge. Therefore, the trained model was pushed to the repository.

## Model Selection Pipeline
* `XGBCclassifier` VS `LogisticRegression`
  * Based on the results from the DS and the nature of the problem, given that the primary focus on predicting delayed flights (class label "1") as accurately as possible, the Logistic Regression model seems slightly better because it has a marginally higher __recall__. This means it can detect a slightly higher proportion of actual delayed flights.
  * However, it's essential to note that the differences between the two models are minimal. It may be worth considering other factors like the training time, ease of deployment, interpretability, and any business costs associated with false positives (incorrectly predicting a flight as delayed) for a real-world application.
 
