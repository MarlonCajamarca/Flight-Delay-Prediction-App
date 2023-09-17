
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
11. Add `workflow` section and `fixes` section to challenge.md file
12. Git add, commit and push all changes to `dev` branch
13. Implement challenge Part 1 and push to `dev` branch

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
## Model Selection Pipeline
* `XGBCclassifier` VS `LogisticRegression`
  * 
  * XGBCLassifier:
    * From the matrix, we can make a few observations:
      * The classifier did not predict any samples as positive (class 1). Both the TP and FP counts are 0.
      * All the negative samples were correctly classified, resulting in a TP value of 18403.
      * All the positive samples were misclassified as negative, which is a significant problem if correctly classifying positive samples is important.
      * In summary, the classifier seems to be biased towards predicting the negative class and fails to correctly classify any of the positive samples.
    * Results
  ```
               precision    recall  f1-score   support

            0       0.82      1.00      0.90     18403
            1       0.00      0.00      0.00      4105

    accuracy                            0.82     22508
    macro avg       0.41      0.50      0.45     22508
    weighted avg    0.67      0.82      0.74     22508
    ```
 
