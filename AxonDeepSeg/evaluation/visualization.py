import pickle
import matplotlib.pyplot as plt
from scipy.misc import imread
from sklearn.metrics import accuracy_score
from segmentation_scoring import score_analysis, dice
from sklearn import preprocessing
import os
from tabulate import tabulate
from os.path import dirname, abspath


def visualize_training(path_model, path_model_init = None, start_visu=0):
    """
    :param path_model: path of the folder with the model parameters .ckpt
    :param path_model_init: if the model is initialized by another, path of its folder
    :param start_visu: first iterations can reach extreme values, start_visu set another start than epoch 0
    :return: no return

    figure(1) represent the evolution of the loss and the accuracy evaluated on the test set along the learning process
    figure(2) if learning initialized by another, evolution of the model of initialisation and of the new are merged

    """

    file = open(path_model + '/evolution.pkl', 'r') # learning variables : loss, accuracy, epoch
    evolution = pickle.load(file)

    if path_model_init:
        file_init = open(path_model_init + '/evolution.pkl', 'r')
        evolution_init = pickle.load(file_init)
        last_epoch = evolution_init['steps'][-1]

        evolution_merged = {} # Merging the two plots : learning of the init and learning of the model
        for key in ['steps','accuracy','loss'] :
            evolution_merged[key] = evolution_init[key]+evolution[key]

        fig = plt.figure(1)
        ax = fig.add_subplot(111)
        ax.plot(evolution_merged['steps'][start_visu:], evolution_merged['accuracy'][start_visu:], '-', label = 'accuracy')
        plt.ylabel('Accuracy')
        plt.ylim(ymin = 0.7)
        ax2 = ax.twinx()
        ax2.axvline(last_epoch, color='k', linestyle='--')
        plt.title('Evolution merged (before and after restoration')
        ax2.plot(evolution_merged['steps'][start_visu:], evolution_merged['loss'][start_visu:], '-r', label = 'loss')
        plt.ylabel('Loss')
        plt.ylim(ymax = 100)
        plt.xlabel('Epoch')

    fig = plt.figure(2)
    ax = fig.add_subplot(111)
    ax.plot(evolution['steps'][start_visu:], evolution['accuracy'][start_visu:], '-', label = 'accuracy')
    plt.ylabel('Accuracy')
    plt.ylim(ymin = 0.7)
    ax2 = ax.twinx()
    plt.title('Accuracy and loss evolution')
    ax2.plot(evolution['steps'][start_visu:], evolution['loss'][start_visu:], '-r', label = 'loss')
    plt.ylabel('Loss')
    plt.ylim(ymax = 100)
    plt.xlabel('Epoch')
    plt.show()



def visualize_segmentation(path) :
    """
    :param path: path of the folder including the data and the results obtained after by the segmentation process.
    :return: no return
    if there is a mask (ground truth) in the folder, scores are calculated : sensitivity, errors and dice
    figure(1) segmentation without mrf
    figure(2) segmentation with mrf
    if there is myelin.jpg in the folder, myelin and image, myelin and axon segmentated, myelin and groundtruth are represented
    """

    path_img = path+'/image.jpg'
    mask = False

    if not 'results.pkl' in os.listdir(path):
        print 'results not present'

    file = open(path+'/results.pkl','r')
    res = pickle.load(file)

    img_mrf = res['img_mrf']
    prediction = res['prediction']
    image_init = imread(path_img, flatten=False, mode='L')

    i_figure = 1

    plt.figure(i_figure)
    plt.title('Axon Segmentation mask')
    plt.imshow(image_init, cmap=plt.get_cmap('gray'))
    plt.hold(True)
    plt.imshow(img_mrf, alpha=0.7)

    i_figure += 1
    if 'mask.jpg' in os.listdir(path):
        Mask = True
        path_mask = path+'/mask.jpg'
        mask = preprocessing.binarize(imread(path_mask, flatten=False, mode='L'), threshold=125)

        acc = accuracy_score(prediction, mask)
        score = score_analysis(image_init, mask, prediction)
        Dice = dice(image_init, mask, prediction)['dice'].mean()
        acc_mrf = accuracy_score(img_mrf, mask)
        score_mrf = score_analysis(image_init, mask, img_mrf)
        Dice_mrf = dice(image_init, mask, img_mrf)['dice'].mean()

        headers = ["MRF", "accuracy", "sensitivity", "precision", "diffusion", "Dice"]
        table = [["False", acc, score[0], score[1], score[2], Dice],
        ["True", acc_mrf, score_mrf[0], score_mrf[1], score_mrf[2], Dice_mrf]]

        subtitle2 = '\n\n---Scores---\n\n'
        scores = tabulate(table, headers)
        text = subtitle2+scores
        print text

        file = open(path+"/Report_results.txt", 'w')
        file.write(text)
        file.close()

    if 'myelin.jpg' in os.listdir(path):
        path_myelin = path + '/myelin.jpg'
        myelin = preprocessing.binarize(imread(path_myelin, flatten=False, mode='L'), threshold=125)

        fig = plt.figure(i_figure)
        ax1 = fig.add_subplot(1,2,1)
        ax1.set_title('Myelin')
        ax1.imshow(image_init, cmap=plt.get_cmap('gray'))
        ax1.hold(True)
        ax1.imshow(myelin, alpha=0.7)

        ax2 = fig.add_subplot(1,2,2)
        ax2.set_title('Myelin Segmentation - Axon Segmentation')
        ax2.imshow(img_mrf, cmap=plt.get_cmap('gray'))
        ax2.hold(True)
        ax2.imshow(myelin, alpha=0.7)

        i_figure+=1

        if Mask :
            plt.figure(i_figure)
            plt.title('Myelin - GroundTruth')
            plt.imshow(mask, cmap=plt.get_cmap('gray'))
            plt.hold(True)
            plt.imshow(myelin, alpha=0.7)

    plt.show()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--path_model", required=True, help="")
    ap.add_argument("-m_init", "--path_model_init", required=False, help="")

    args = vars(ap.parse_args())
    path_model = args["path_model"]
    path_model_init = args["path_model_init"]

    visualize_training(path_model, path_model_init)