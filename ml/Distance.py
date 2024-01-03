import numpy as np
import math

class Distance:
    @staticmethod
    def calculateCosineDistance(x, y):
        return 1 - ((np.dot(x, y)) / (np.linalg.norm(x) * np.linalg.norm(y)))
    @staticmethod
    def calculateMinkowskiDistance(x, y, p=2):
        return np.power(np.sum(np.power(np.absolute(np.subtract(x, y)), p)), 1/p)
    @staticmethod
    def calculateMahalanobisDistance(x,y, S_minus_1):
        x_minus_y = np.subtract(x,y)
        S_minus_1_result = np.linalg.inv(np.cov(S_minus_1))
        return np.sqrt(np.dot(np.dot(x_minus_y.T,S_minus_1_result),x_minus_y))
    @staticmethod
    def confidenceInterval(givenAccuracy,givenNoSamples):
        z = {"90%": 1.64, "95%": 1.96, "98%": 2.33, "99%": 2.58}
        return z["90%"]*math.sqrt((givenAccuracy*(1-givenAccuracy)) /givenNoSamples)