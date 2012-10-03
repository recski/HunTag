import numpy as np
import scipy
import sys
import heapq



def read_liblinear_model(model):

    model_parameters = {}
    model_parameters["nr_feature"] = model.nr_feature
    model_parameters["nr_class"] = model.nr_class
    model_parameters["solver_type"] = model.param
    model_parameters["bias"] = model.bias
    model_parameters["label"] = model.label
    model_matrix =np.ctypeslib.as_array(model.w,(model.nr_feature, model.nr_class))
    for index,value in enumerate(model_matrix.flat):
        model.w[index] = value
    return model_parameters, model_matrix


def write_liblinear_model(m, model_matrix):
       
    for index,value in enumerate(model_matrix.flat):
          model.w[index] = value
    return m


def large_weighted_features(fC_Bookkeaper,model,limit):
       
        large_feature_list = []
        parameters, matrix = read_liblinear_model(model)

        for i in range(int(model.nr_feature)):
            max_abs_value = abs(matrix[i, :]).max()
            if max_abs_value > float(limit):
                large_feature_list.append(fC_Bookkeaper.noToFeat[(i+1)])
        return large_feature_list

def largest_weighted_features(fC_Bookkeeper, lC_Bookkeeper, model,count):
            
            maximum_abs_values = []
            parameters, matrix = read_liblinear_model(model)

            for featIndex in range(int(model.nr_feature)):
                absRow = abs(matrix[featIndex, :])
                maxVal = absRow.max()
                labelIndex = absRow.argmax()
                maximum_abs_values.append((-1*maxVal, featIndex, labelIndex, matrix[featIndex, labelIndex]))
                #maximum_abs_values.append((-1 * (abs(matrix[i, :]).max()), i + 1))
            h = []
            heapq.heapify(h)
            largest_weighted_feature_list = []
            for item in maximum_abs_values:
                heapq.heappush(h, item)
            for i in range(int(count)):
                featNo, labelNo, weight = heapq.heappop(h)[1:]
                featName = fC_Bookkeeper.noToFeat[(featNo+1)]
                labelName = lC_Bookkeeper.noToFeat[(labelNo+1)]
                largest_weighted_feature_list.append((weight, featName, labelName))
            return largest_weighted_feature_list  
    
    

class LiblinearModel(object):
    def __init__(self, weightMatrix = None, labelToName = None, nameToLabel = None,
                 featureToName = None, nameToFeature = None, modelParameters = None):
        self.weightMatrix = weightMatrix
        self.labelToName = labelToName
        self.nameToLabel = nameToLabel
        self.featureToName = featureToName
        self.nameToFeature = nameToFeature
        self.modelParameters = modelParameters

    def max_in_coloumn(self, index):
        if self.weightMatrix == None:
            raise ValueError("No matrix given")
        else:
            return self.weightMatrix[:, index].max(), int(self.weightMatrix.argmax(axis = 0)[index])
           
    def max_in_row(self, index):
        if self.weightMatrix == None:
            raise ValueError("No matrix given")
        else:
            return self.weightMatrix[index, :].max(), int(self.weightMatrix.argmax(axis = 1)[index])
            
    def max_absolute_in_coloumn(self, index):
        if self.weightMatrix == None:
            raise ValueError("No matrix given")
        else:
            return abs(self.weightMatrix[:, index]).max(), int(abs(self.weightMatrix).argmax(axis = 0)[index])
            

    def max_absolute_in_row(self, index):
        if self.weightMatrix == None:
            raise ValueError("No matrix given")
        else:
            return abs(self.weightMatrix[index, :]).max(), int(abs(self.weightMatrix).argmax(axis = 1)[index])
    
    def large_weighted_features(self,limit):
        if self.weightMatrix == None:
            raise ValueError("No matrix given")
        if self.featureToName == None:
            raise ValueError("No number-feature mapping given")
        else:
            large_feature_list = []
            for i in range(int(self.modelParameters["nr_feature"])):
                max_abs_value = abs(self.weightMatrix[i, :]).max()
                if max_abs_value > float(limit):
                    large_feature_list.append(self.featureToName[str(i+1)])
        return large_feature_list


    def set_small_weights_to_zero(matrix, limit):
          for i in range(int(self.modelParameters["nr_feature"])):
              max_abs_value = abs(self.matrix[i, :]).max()
              if max_abs_value < limit:
                  self.weightMatrix[i] = numpy.zeros(self.modelParameters["nr_class"])
              return matrix


    def nonzero_weighted_features(self):
        return self.large_weighted_features(0)


    def largest_weighted_features(self,count):                 
        if self.weightMatrix == None:
            raise ValueError("No matrix given")
        if self.featureToName == None:
            raise ValueError("No number-feature mapping given")
            
        else:
            maximum_abs_values = []
            for i in range(int(self.modelParameters["nr_feature"])):
                maximum_abs_values.append((-1 * (abs(self.weightMatrix[i, :]).max()), i + 1))
            h = []
            heapq.heapify(h)
            largest_weighted_feature_list = []
            for item in maximum_abs_values:
                heapq.heappush(h, item)
            for i in range(int(count)):
                feature = heapq.heappop(h)[1]  
                largest_weighted_feature_list.append(self.featureToName[str(feature)])         
        return largest_weighted_feature_list  
   

    def largest_among_large_weights(self, value, count):
        if self.weightMatrix == None:
            raise ValueError("No matrix given")
        if self.featureToName == None:
            raise ValueError("No number-feature mapping given")
            
        else:
            maximum_abs_values = []
            for i in range(int(self.modelParameters["nr_feature"])):
                if abs(self.weightMatrix[i, :]).max() > float(value):   
                    maximum_abs_values.append((-1 * (abs(self.weightMatrix[i, :]).max()), i + 1))
            h = []
            heapq.heapify(h)
            largest_weighted_feature_list = []
            for item in maximum_abs_values:
                heapq.heappush(h, item)
            for i in range(int(count)):
                if not len(h) == 0:
                    feature = heapq.heappop(h)[1]  
                    largest_weighted_feature_list.append(self.featureToName[str(feature)])
                else:
                    break           
        return largest_weighted_feature_list  
    
    def largest_model_weights(self, count):
         if self.weightMatrix == None:
             raise ValueError("No matrix given")
         if self.featureToName == None:
             raise ValueError("No number-feature name mapping given") 
         if self.model_parameters == None:
             raise ValueError("No model parameters given")
         if self.labelToName == None:
             raise ValueError("No number-label name mapping given")
         else:
             matrix_abs = abs(self.weightMatrix)
             matrix_abs_line = matrix_abs.reshape(int(self.model_parameters["nr_feature"]), int(self.model_parameters["nr_class"]))
             
    @staticmethod
    def read_mapping(f):
        number_name = {}
        name_number = {}
        for line in f:
            name, number = line.strip().split('\t')
            number_name[number] = name
            name_number[name] = number
        return number_name, name_number
    @staticmethod
    def read_weight(f):
        model_parameters = {}
        options, matrix = f.read().split("w")
        for option in options.split('\n'):
            if not option.strip():
                continue
            fields = option.strip().split(' ')
            name = fields[0]
	    value = fields[1:]
            if len(value) == 1:
                model_parameters[name.strip()] = value[0].strip()
            else:
                model_parameters[name.strip()] = value
	
        matrix_2 = matrix.split('\n')[1:]
        data_string = ''.join(matrix_2)
        model_array = np.fromstring(data_string, sep =' ')  
        model_parameters["nr_class"]
        model_matrix = model_array.reshape(int(model_parameters["nr_feature"]), int(model_parameters["nr_class"]))
        return model_parameters, model_matrix  

        
if __name__ == '__main__':
    from liblinearutil import *
    from tools import *
    modelName = sys.argv[1]
    model = load_model('{0}.model'.format(modelName))
    featCounter = BookKeeper()
    featCounter.readFromFile('{0}.featureNumbers'.format(modelName))
    labelCounter = BookKeeper()
    labelCounter.readFromFile('{0}.labelNumbers'.format(modelName))
    topFeats = largest_weighted_features(featCounter, labelCounter, model, int(sys.argv[2]))
    for weight, name, label in topFeats:
        print weight, name, label

