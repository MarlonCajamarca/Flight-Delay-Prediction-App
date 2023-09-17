import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

from sklearn.model_selection import GridSearchCV

from typing import Tuple, Union, List

import warnings
warnings.filterwarnings('ignore')

class DelayModel:

    def __init__(
        self
    ):
        self._model = None # Model should be saved in this attribute.

    def preprocess(
        self,
        data: pd.DataFrame,
        target_column: str = None
    ) -> Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]:
        """
        Prepare raw data for training or predict.

        Args:
            data (pd.DataFrame): raw data.
            target_column (str, optional): if set, the target is returned.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: features and target.
            or
            pd.DataFrame: features.
        """
        # Create feature generator object
        feature_generator = FeatureGenerator(data)
        # Generate features
        features = feature_generator.generate_features()
        # Target column extraction
        if target_column is not None:
            # Shuffle data to ensure that the model being trained on this data is not biased towards any particular order of the rows
            features = shuffle(features[['OPERA', 'MES', 'TIPOVUELO', 'SIGLADES', 'DIANOM', 'delay']], random_state = 111)
            # Target column extraction
            target = features['delay'].to_frame()
        else:
            # Shuffle data to ensure that the model being trained on this data is not biased towards any particular order of the rows
            features = shuffle(features[['OPERA', 'MES', 'TIPOVUELO', 'SIGLADES', 'DIANOM']], random_state = 111)
        # One-hot encoding using DS selected sub-set of features for training
        features = pd.concat([
            pd.get_dummies(features['OPERA'], prefix = 'OPERA'),
            pd.get_dummies(features['TIPOVUELO'], prefix = 'TIPOVUELO'), 
            pd.get_dummies(features['MES'], prefix = 'MES')], 
            axis = 1
        )
        # From feature importance analysis, the following features were selected
        top_10_features = [
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
        ]
        # Select top 10 features for training
        features = features[top_10_features]
        # If target column is not None, return features and target as a Tuple [pd.DataFrame, pd.DataFrame], else return features dataframe
        if target_column is not None:          
            return features, target
        else:
            return features

    def fit(
        self,
        features: pd.DataFrame,
        target: pd.DataFrame
    ) -> None:
        """
        Fit model with preprocessed data.

        Args:
            features (pd.DataFrame): preprocessed data.
            target (pd.DataFrame): target.
        """
        # Split data into train and test sets
        x_train, _, y_train, _ = train_test_split(
            features, 
            target, 
            test_size = 0.33, 
            random_state = 42
        )
        ### Appraoch based on DS exploration notebook

        # # Data balance through Scaling
        # n_y0 = len(y_train[y_train == 0])
        # n_y1 = len(y_train[y_train == 1])
        # scale = n_y0/n_y1
        # # Instantiating the model using feature importance and Balanced class weight
        # self._model = LogisticRegression(
        #     class_weight={1: n_y0/len(y_train), 0: n_y1/len(y_train)}
        #     )
        # # Fitting the model
        # self._model.fit(x_train, y_train)

        ### Approach based in my ML expertise

        # Define hyperparameters and values to test
        param_grid = {
            'C': [0.001, 0.01, 0.1, 1, 10, 100],
            'solver': ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga'],
            'class_weight': ['balanced']
        }
        
        # Define a grid search with a focus on recall
        grid_search = GridSearchCV(
            LogisticRegression(max_iter=10000), # Increased max_iter for convergence with some solvers
            param_grid, 
            scoring='recall', 
            cv=5
        )
        
        # Fit the grid search to the data
        grid_search.fit(x_train, y_train)
        
        # Use the best estimator found by the grid search
        self._model = grid_search.best_estimator_

    def predict(
        self,
        features: pd.DataFrame
    ) -> List[int]:
        """
        Predict delays for new flights.

        Args:
            features (pd.DataFrame): preprocessed data.
        
        Returns:
            (List[int]): predicted targets.
        """
        delay_predictions = self._model.predict(features).tolist()
        return delay_predictions
    
class FeatureGenerator(object):
    """
    Class for generating features from raw data.
    """
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data

    def generate_features(self, threshold_in_minutes: int = 15) -> pd.DataFrame:
        """
        Generate features from raw data. Return dataframe with generated features.

        Args:
            threshold_in_minutes (int, optional): threshold in minutes for delay. Defaults to 15.
        
        Returns:
            (pd.DataFrame): features.
        """
        self.data['period_day'] = self.data['Fecha-I'].apply(self.get_period_day)
        self.data['high_season'] = self.data['Fecha-I'].apply(self.is_high_season)
        self.data['min_diff'] = self.data.apply(self.get_min_diff, axis=1)
        self.data['delay'] = np.where(self.data['min_diff'] > threshold_in_minutes, 1, 0)
        return self.data
    
    def get_min_diff(self, data) -> float:
        """
        Get difference in minutes between two dates. Return difference in minutes.

        Args:
            data (pd.DataFrame): raw data.

        Returns:
            (float): difference in minutes.
        """
        fecha_o = datetime.strptime(data['Fecha-O'], '%Y-%m-%d %H:%M:%S')
        fecha_i = datetime.strptime(data['Fecha-I'], '%Y-%m-%d %H:%M:%S')
        min_diff = ((fecha_o - fecha_i).total_seconds())/60
        return min_diff
    
    def is_high_season(self, fecha) -> int:
        """
        Check if date is in high season. Return 1 if date is in high season, 0 otherwise.

        Args:
            fecha (str): date in format YYYY-MM-DD HH:MM:SS.

        Returns:
            (int): 1 if date is in high season, 0 otherwise.
        """
        fecha_año = int(fecha.split('-')[0])
        fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
        range1_min = datetime.strptime('15-Dec', '%d-%b').replace(year = fecha_año)
        range1_max = datetime.strptime('31-Dec', '%d-%b').replace(year = fecha_año)
        range2_min = datetime.strptime('1-Jan', '%d-%b').replace(year = fecha_año)
        range2_max = datetime.strptime('3-Mar', '%d-%b').replace(year = fecha_año)
        range3_min = datetime.strptime('15-Jul', '%d-%b').replace(year = fecha_año)
        range3_max = datetime.strptime('31-Jul', '%d-%b').replace(year = fecha_año)
        range4_min = datetime.strptime('11-Sep', '%d-%b').replace(year = fecha_año)
        range4_max = datetime.strptime('30-Sep', '%d-%b').replace(year = fecha_año)
        
        if ((fecha >= range1_min and fecha <= range1_max) or 
            (fecha >= range2_min and fecha <= range2_max) or 
            (fecha >= range3_min and fecha <= range3_max) or
            (fecha >= range4_min and fecha <= range4_max)):
            return 1
        else:
            return 0
    
    def get_period_day(self, date) -> str:
        """
        Get period of day from date. Return string with period of day.

        Args:
            date (str): date in format YYYY-MM-DD HH:MM:SS.
        
        Returns:
            (str): period of day.
        """
        date_time = datetime.strptime(date, '%Y-%m-%d %H:%M:%S').time()
        morning_min = datetime.strptime("05:00", '%H:%M').time()
        morning_max = datetime.strptime("11:59", '%H:%M').time()
        afternoon_min = datetime.strptime("12:00", '%H:%M').time()
        afternoon_max = datetime.strptime("18:59", '%H:%M').time()
        evening_min = datetime.strptime("19:00", '%H:%M').time()
        evening_max = datetime.strptime("23:59", '%H:%M').time()
        night_min = datetime.strptime("00:00", '%H:%M').time()
        night_max = datetime.strptime("4:59", '%H:%M').time()
        
        if(date_time > morning_min and date_time < morning_max):
            return 'mañana'
        elif(date_time > afternoon_min and date_time < afternoon_max):
            return 'tarde'
        elif(
            (date_time > evening_min and date_time < evening_max) or
            (date_time > night_min and date_time < night_max)
        ):
            return 'noche'
    
# Creating main entrypoint for runnig this file as CLI for easy-testing implementation
if __name__ == "__main__":
    print("Running model.py as CLI")
    # Create dalay model object
    model = DelayModel()
    # Execute preprocess method
    features, target = model.preprocess(
            data=pd.read_csv(filepath_or_buffer="/home/marlon/MachineLearning/Flight-Delay-Prediction-App/data/data.csv"),
            target_column="delay"
        )
    # Simulating test assertions for this step
    FEATURES_COLS = [
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
    ]

    TARGET_COL = [
        "delay"
    ]
    assert isinstance(features, pd.DataFrame)
    assert features.shape[1] == len(FEATURES_COLS)
    assert set(features.columns) == set(FEATURES_COLS)

    assert isinstance(target, pd.DataFrame)
    assert target.shape[1] == len(TARGET_COL)
    assert set(target.columns) == set(TARGET_COL)
    # Split data into train and test sets
    _, features_validation, _, target_validation = train_test_split(features, target, test_size = 0.33, random_state = 42)
    # Execute fit method
    model.fit(
        features=features,
        target=target
    )
    predicted_target = model._model.predict(
            features_validation
        )
    report = classification_report(target_validation, predicted_target, output_dict=True)
    print(report)
    # execute predict method
    features = model.preprocess(
            data=pd.read_csv(filepath_or_buffer="/home/marlon/MachineLearning/Flight-Delay-Prediction-App/data/data.csv")
        )
    if model._model is None:
        raise ValueError("Model has not been initialized or trained!")
    predicted_targets = model.predict(
            features=features
        )
    assert isinstance(predicted_targets, list)
    assert len(predicted_targets) == features.shape[0]
    assert all(isinstance(predicted_target, int) for predicted_target in predicted_targets)
