from ml.Distance import Distance


class KNN:
    def __init__(self, dataset, data_label, similarity_function, similarity_function_parameters=None, K=1):
        """
        :param dataset: dataset on which KNN is executed, 2D numpy array
        :param data_label: class labels for each data sample, 1D numpy array
        :param similarity_function: similarity/distance function, Python function
        :param similarity_function_parameters: auxiliary parameter or parameter array for distance metrics
        :param K: how many neighbors to consider, integer
        """
        self.K = K
        self.dataset = dataset
        self.dataset_label = data_label
        self.similarity_function = similarity_function
        self.similarity_function_parameters = similarity_function_parameters

    def predict(self, instance):
        instance_label = []
        for each_instance in instance:
            distance_array = []
            if self.similarity_function == "minkowski":
                distance_array = [(self.dataset_label[i],Distance.calculateMinkowskiDistance(self.dataset[i],each_instance,self.similarity_function_parameters)) for i in range(len(self.dataset))]
            if self.similarity_function == "cosine":
                distance_array = [(self.dataset_label[i],Distance.calculateCosineDistance(self.dataset[i],each_instance)) for i in range(len(self.dataset))]
            if self.similarity_function == "mahalanobis":
                distance_array = [(self.dataset_label[i],Distance.calculateMahalanobisDistance(self.dataset[i],each_instance,self.similarity_function_parameters)) for i in range(len(self.dataset))]
            distance_array.sort(key=lambda a: a[1])
            nearest_neighbors = distance_array[0:self.K]
            votes = [labels for labels, distances in nearest_neighbors]
            instance_label.append(max(votes, key=lambda a: votes.count(a)))
        return instance_label
