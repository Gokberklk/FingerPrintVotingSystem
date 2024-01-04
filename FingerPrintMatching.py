# Adem Garip

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from PIL import Image
import io


# the code for gabor and minutiae is written after researching algorithms for them
# also remember that most of the variables might change due to the data set

def gabor_Filter(ksize, sigma, theta, lambd, gamma, ktype):
    sigma_x = sigma
    sigma_y = sigma / gamma
    theta_radians = theta * np.pi / 180

    kernel = cv2.getGaborKernel((ksize, ksize), sigma, theta_radians, lambd, gamma, 0, ktype)
    return kernel


def extract_gabor_Features(image, kernel, ktype):
    filtered_image = cv2.filter2D(image, ktype, kernel)
    return filtered_image


def extract_minutiae_Points(image):
    threshold_val, threshold = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    Contours, order = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    M_points = []
    for contour in Contours:
        Hull = cv2.convexHull(contour, returnPoints=False)
        defects = cv2.convexityDefects(contour, Hull)

        if defects is not None:
            for i in range(defects.shape[0]):
                start, end, far, _ = defects[
                    i, 0]  # the last variable should be distance but since it is not used we can ignore that
                startTuple = tuple(contour[start][0])
                endTuple = tuple(contour[end][0])
                farTuple = tuple(contour[far])

                distance1 = np.linalg.norm(np.array(farTuple) - np.array(endTuple))
                # the np.linalg.norm calculates the Euclidean distance between far and end point basically used built-in function instead of calculating using square roots etc.
                distance2 = np.linalg.norm(np.array(farTuple) - np.array(startTuple))
                distance3 = np.linalg.norm(np.array(startTuple) - np.array(endTuple))
                if distance1 + distance2 >= distance3 and abs(distance1 - distance2) <= distance3:
                    M_points.append(far)

                # the if statement above checks whether the sum of the distances between (far and end points)
                # and (far and start points) are greater or equal to the distance between the start and end points
                # Also it checks whether the difference of the first two distances are greater or equal to the third distance
                # of course since we look at that in magnitude wise we take the abstract of the operation
                # this geometric criteria is often used in minutiae extraction algorithms and the farTuple (point) represents a potential
                # minutiae point
            return M_points


def Gabor(image1, image2):
    ktype = cv2.CV_32F
    image1 = cv2.resize(image1, (image2.shape[1], image2.shape[0]))
    # gabor filter parameters shall be arranged through testing
    # for the current dataset this values are appropriate
    ksize = 15
    sigma = 4
    theta = 90
    lambd = 10
    gamma = 0.5
    gabor_kernel = gabor_Filter(ksize, sigma, theta, lambd, gamma, ktype)
    # Extraction of gabor features
    im_features1 = extract_gabor_Features(image1, gabor_kernel, ktype)
    im_features2 = extract_gabor_Features(image2, gabor_kernel, ktype)
    # calculate similarity

    similarity_index = ssim(im_features1, im_features2, data_range=im_features1.max() - im_features1.min())

    return similarity_index, im_features1, im_features2


def Minutiae(image1, image2):
    minutiae_image_1 = extract_minutiae_Points(image1)
    minutiae_image_2 = extract_minutiae_Points(image2)
    #print(minutiae_image_1,minutiae_image_2)
    minutiae_image_1 = [0] if minutiae_image_1 == None else minutiae_image_1
    minutiae_image_2 = [0] if minutiae_image_2 == None else minutiae_image_2
    similarity = len(set(minutiae_image_1) & set(minutiae_image_2)) / len(set(minutiae_image_1) | set(minutiae_image_2))
    # the line above basically calculates the similarity between two sets of points
    # the formula is found from minutiae algorithm
    return similarity, minutiae_image_1, minutiae_image_2


def Check_Fingerprint(image1, image2):
    # image1 = cv2.imread("Dataset/DB1_B/101_3.tif", 0)  # the full path of the image if it is in the database change accordingly
    #image2 = cv2.imread("Dataset/DB1_B/101_1.tif", 0)  # one will be taken from the device and the other from the database so arrange them
    image1_blob_file = io.BytesIO(image1)
    image2_blob_file = io.BytesIO(image2)  # create byteesIO object to work with binary data
    image_1 = Image.open(image1_blob_file)
    image_2 = Image.open(image2_blob_file)  # open image using Pillow
    image_1=image_1.convert('L')
    image_2= image_2.convert('L')
    image1array=np.array(image_1)
    image2array=np.array(image_2)

    Gabor_similarity, a, b = Gabor(image1array, image2array)
    Minutiae_similarity, c, d = Minutiae(image1array, image2array)
    M_similarity_treshold = 0.70  # this value will change according to the tests of the dataset images and the images taken from the machine
    G_similarity_index_treshold = 0.95  # will be updated according to the data set the above values as well
    if Gabor_similarity > G_similarity_index_treshold and Minutiae_similarity > M_similarity_treshold:
        return True
    else:
        return False

def alternativeTesting():#Casia fingerprint dataset
    dataset = []
    train = []
    root = "ml/DB1_B/"
    for fp_owner in range(101,111):
        for fp_sample in range(1,9):
            destination = root+str(fp_owner)+'_'+str(fp_sample)+".tif"
            image = cv2.imread(destination,0)
            Gb_similarity,Gimfeature1,Gimfeature2 = Gabor(image,image)
            #Mt_similarity,Mimfeature1,Mimfeature2 = Minutiae(image,image)
            dataset.append(np.ravel(Gimfeature1,order='F')[0:300])# Dimentionality Reduction, Original = (300,300), now = (90000)
            train.append(fp_owner-100)
    train = np.array(train)
    dataset = np.array(dataset)
    #print()
    #print(dataset[0])
    #print(train)
    #print(len(train),np.shape(dataset),np.shape(train))
    return dataset,train
def getGaborFromBinary(image1):
    image1_blob_file = io.BytesIO(image1)
    image_1 = Image.open(image1_blob_file)
    image_1 = image_1.convert('L')
    image1array = np.array(image_1)

    Gabor_similarity, gbimage1, gbimage2 = Gabor(image1array, image1array)
    return gbimage1