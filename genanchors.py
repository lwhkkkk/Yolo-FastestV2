'''
Created on Feb 20, 2017

@author: jumabek
'''
from os import listdir
from os.path import isfile, join
import argparse
#import cv2
import numpy as np
import sys
import os
import shutil
import random 
import math

def IOU(x,centroids):
    similarities = []
    k = len(centroids)
    for centroid in centroids:
        c_w,c_h = centroid
        w,h = x
        if c_w>=w and c_h>=h:
            similarity = w*h/(c_w*c_h)
        elif c_w>=w and c_h<=h:
            similarity = w*c_h/(w*h + (c_w-w)*c_h)
        elif c_w<=w and c_h>=h:
            similarity = c_w*h/(w*h + c_w*(c_h-h))
        else: #means both w,h are bigger than c_w and c_h respectively
            similarity = (c_w*c_h)/(w*h)
        similarities.append(similarity) # will become (k,) shape
    return np.array(similarities) 
 
def avg_IOU(X,centroids):
    n,d = X.shape
    sum = 0.
    for i in range(X.shape[0]):
        #note IOU() will return array which contains IoU for each centroid and X[i] // slightly ineffective, but I am too lazy
        sum+= max(IOU(X[i],centroids)) 
    return sum/n

def write_anchors_to_file(centroids,X,anchor_file, width_in_cfg_file, height_in_cfg_file):
    f = open(anchor_file,'w')
    
    anchors = centroids.copy()
    print(anchors.shape)

    for i in range(anchors.shape[0]):
        anchors[i][0]*=width_in_cfg_file
        anchors[i][1]*=height_in_cfg_file
         

    widths = anchors[:,0]
    sorted_indices = np.argsort(widths)

    print('Anchors = ', anchors[sorted_indices])
        
    for i in sorted_indices[:-1]:
        f.write('%0.2f,%0.2f, '%(anchors[i,0],anchors[i,1]))

    #there should not be comma after last anchor, that's why
    f.write('%0.2f,%0.2f\n'%(anchors[sorted_indices[-1:],0],anchors[sorted_indices[-1:],1]))
    
    f.write('%f\n'%(avg_IOU(X,centroids)))
    print()

def kmeans(X,centroids,eps,anchor_file, width_in_cfg_file, height_in_cfg_file):
    
    N = X.shape[0]
    iterations = 0
    k,dim = centroids.shape
    prev_assignments = np.ones(N)*(-1)    
    iter = 0
    old_D = np.zeros((N,k))

    while True:
        D = [] 
        iter+=1           
        for i in range(N):
            d = 1 - IOU(X[i],centroids)
            D.append(d)
        D = np.array(D) # D.shape = (N,k)
        
        print("iter {}: dists = {}".format(iter,np.sum(np.abs(old_D-D))))
            
        #assign samples to centroids 
        assignments = np.argmin(D,axis=1)
        
        if (assignments == prev_assignments).all() :
            print("Centroids = ",centroids)
            write_anchors_to_file(centroids,X,anchor_file, width_in_cfg_file, height_in_cfg_file)
            return

        #calculate new centroids
        centroid_sums=np.zeros((k,dim),np.float64)
        for i in range(N):
            centroid_sums[assignments[i]]+=X[i]        
        for j in range(k):            
            centroids[j] = centroid_sums[j]/(np.sum(assignments==j))
        
        prev_assignments = assignments.copy()     
        old_D = D.copy()  

def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--traintxt', default = '', 
                        help='path to traintxt\n' )
    parser.add_argument('--output_dir', default = './', type = str, 
                        help='Output anchor directory\n' )  
    parser.add_argument('--num_clusters', default = 6, type = int, 
                        help='number of clusters\n' )  
    
    parser.add_argument('--input_width', default = 352, type = int, 
                        help='model input width\n' )  

    parser.add_argument('--input_height', default = 352, type = int, 
                        help='model input height\n' )  
   
    args = parser.parse_args()
    
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    f = open(args.traintxt)
  
    lines = [line.rstrip('\n') for line in f.readlines()]
    
    annotation_dims = []

    size = np.zeros((1,1,3))
    for line in lines:
                    
        #line = line.replace('images','labels')
        #line = line.replace('img1','labels')
        # line = line.replace('JPEGImages','labels')        
        

        # line = line.replace('.jpg','.txt')
        # line = line.replace('.png','.txt')
        # 将 "images" 替换成 "labels"，并将图片扩展名换成 .txt
        # line = line.replace('/images/', '/labels/').replace('\\images\\', '\\labels\\')  # 针对不同系统路径写法
        line = line.replace('train/images', 'train/labels')
        line = line.replace('.jpg','.txt').replace('.png','.txt').replace('.jpeg','.txt')

        print(line)
        print("Trying to open:", repr(line))  # ← 打印原始路径，检查是否有空格或 \r 等隐藏符

        label_path = os.path.normpath(line.strip())  # 自动统一路径分隔符
        f2 = open(label_path)



        for line in f2.readlines():
            line = line.rstrip('\n')
            w,h = line.split(' ')[3:]            
            #print(w,h)
            annotation_dims.append(tuple(map(float,(w,h))))
    annotation_dims = np.array(annotation_dims)
  
    eps = 0.005
    width_in_cfg_file = args.input_width
    height_in_cfg_file = args.input_height

    if args.num_clusters == 0:
        for num_clusters in range(1,11): #we make 1 through 10 clusters 
            anchor_file = join( args.output_dir,'anchors%d.txt'%(num_clusters))

            indices = [ random.randrange(annotation_dims.shape[0]) for i in range(num_clusters)]
            centroids = annotation_dims[indices]
            kmeans(annotation_dims,centroids,eps,anchor_file, width_in_cfg_file, height_in_cfg_file)
            print('centroids.shape', centroids.shape)
    else:
        anchor_file = join( args.output_dir,'anchors%d.txt'%(args.num_clusters))
        indices = [ random.randrange(annotation_dims.shape[0]) for i in range(args.num_clusters)]
        centroids = annotation_dims[indices]
        kmeans(annotation_dims,centroids,eps,anchor_file, width_in_cfg_file, height_in_cfg_file)
        print('centroids.shape', centroids.shape)

if __name__=="__main__":
    main(sys.argv)
