#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
from kmodes import kmodes
from kmodes import kprototypes
import json

# random categorical data
# data = np.random.choice(20, (100, 10))
data = [["en", "T"],["k", "T"],["ch", "T"],
        ["en", "F"],["k", "T"],["ch", "T"],
        ["en", "T"],["k", "F"],["ch", "T"]]
y = ['bit1', 'bit2', 'bit3', 'bit4', 'bit5', 'bit6', 'bit7', 'bit8', 'bit9', 'bit10', 'bit11', 'bit12', 'bit13', 'bit14', 'bit15', 'bit16', 'bit17', 'bit18', 'bit19', 'bit20', 'bit21', 'bit22', 'bit23', 'bit24', 'tinyurl1', 'tinyurl2', 'tinyurl3', 'tinyurl4', 'tinyurl5', 'tinyurl6', 'goo1', 'goo2', 'goo3', 'goo4', 'goo5', 'goo6', 'goo7', 'goo8', 'goo9', 'goo10', 'dld1', 'dld2', 'dld3', 'dld4', 'dld5', 'dld6', 'dld7', 'dld8', 'dld9', 'dld10', 'ift1', 'ift2', 'ift3', 'ift4', 'dlvr1', 'dlvr2', 'dlvr3', 'dlvr4', 'dlvr5', 'dlvr6', 'dlvr7', 'dlvr8', 'dlvr9', 'dlvr10', 'dlvr11', 'dlvr12', 'dlvr13', 'dlvr14', 'dlvr15', 'dlvr16', 'dlvr17', 'dlvr18', 'dlvr19', 'dlvr20', 'dlvr21', 'dlvr22', 'dlvr23', 'dlvr24', 'dlvr25', 'dlvr26', 'dlvr27', 'dlvr28', 'dlvr29', 'dlvr30', 'ow1', 'ow2', 'ow3', 'ow4', 'ow5', 'ow6', 'ow7', 'ow8', 'ow9', 'lnis1', 'lnis2', 'lnis3', 'lnis4', 'lnis5', 'lnis6', 'lnis7', 'viid1', 'viid2']

data = [[1.4775939508933684, u'en'], [0.62667253174157023, u'en'], [1.3461382967033908, u'en'], [0.24205842296290267, u'en-gb'], [1.9421845398375757, u'en'], [1.011554987050385, u'en'], [1.1574165577868467, u'en'], [2.537949745614918, u'en'], [0.035523803255693633, u'en'], [0.8843546413877853, u'en'], [1.1592046414074306, u'en'], [1.7303003697166908, u'en'], [1.5025445001702784, u'en'], [1.4411168995985961, u'en'], [0.23551648788937438, u'en'], [2.0010191908832189, u'en'], [1.3194543168861197, u'en'], [2.4062883632072509, u'en'], [0.15698349395855024, u'en'], [0.68276889740851665, u'en'], [1.7188804184979822, u'en'], [0.92188512729901795, u'en'], [1.2946949745049872, u'en'], [2.0018485109066204, u'en'], [1.4511272741402346, u'en'], [0.99611858064153058, u'en'], [1.4197964179433045, u'en'], [1.3255998915612184, u'en'], [0.77890436093167714, u'en'], [0.51557252757307814, u'en'], [0.44468417017393275, u'en'], [0.27236503807641793, u'en'], [1.4978432771016534, u'en'], [0.57220210442894304, u'en'], [0.44956298553971541, u'tr'], [0.13294212485391374, u'en'], [0.72154888299991427, u'en'], [1.5005486453383625, u'en'], [0.85045234588453678, u'en'], [3.3961776673772452, u'en'], [0.49222197278498003, u'en'], [0.5992085560255892, u'en'], [0.53395533068083478, u'en'], [0.81085493202571868, u'en'], [1.2222070919689889, u'en'], [0.37216863871713129, u'en'], [2.4873827938091448, u'en'], [0.43702885022834631, u'en'], [0.84915378740708958, u'en'], [0.357695967922465, u'en'], [0.51504590872166034, u'en'], [1.7789845939989246, u'en'], [1.6860466040821738, u'en'], [0.2910326316135865, u'en'], [1.4918345287188608, u'en'], [1.8885693256935254, u'en'], [1.7761132796327974, u'en'], [1.0692798260056373, u'en'], [0.52292433240428404, u'en'], [0.3012632952743019, u'en'], [0.54160510066894252, u'en'], [0.70145098953449603, u'en'], [1.1183227859180997, u'en'], [0.045032176903083997, u'en'], [0.8624482187270256, u'en'], [1.0740936461074415, u'en'], [0.029610039013034828, u'en'], [0.64910266270218009, u'en'], [0.43761670650299844, u'en'], [0.52668209721832182, u'en'], [0.4633028335355785, u'en'], [0.11854051913331211, u'en'], [0.93178227016992743, u'en'], [0.42145902292620924, u'en'], [0.053259859495549434, u'en'], [0.29555417454779997, u'en'], [1.5898838896346521, u'en'], [0.057343063087007477, u'en'], [1.5427834032628265, u'en'], [0.1873485438679679, u'en'], [0.41673452031228841, u'en'], [0.59075001735416399, u'en'], [0.053598941681637813, u'en'], [0.82115056743746717, u'en'], [0.21418944628938399, u'en'], [0.58801060141346295, u'en'], [0.56860382553426947, u'ru'], [0.99137901762681557, u'en'], [0.50605928481593743, u'en'], [4.5780761343832079, u'en'], [1.3821872801210691, u'en'], [3.5396235561908522, u'ru'], [0.57534312166630031, u'en'], [1.255058357265721, u'ar'], [0.52413864450009373, u'en'], [0.53511560886671783, u'ja'], [1.6600331026562134, u'es'], [0.4649003110348735, u'en'], [1.0556233465673961, u'en'], [1.596997655261309, u'fr'], [0.72711195406704043, u'es'], [1.3217825905180927, u'es']]
# data = [np.array([d[0] for d in data]), np.array([d[1] for d in data])]
data = [[d[0]] for d in data]
data = np.array(data)
print(data)

n_clusters = 5
def kprototypes_cluster(data):
    km = kprototypes.KPrototypes(n_clusters=n_clusters, init='Cao', n_init=5, verbose=1, max_iter=200)
    clusters = km.fit_predict(data, categorical=[1])
    print(km.cluster_centroids_)
    return clusters

def kmeans_cluter(data):
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(data)
    # array([0, 0, 0, 1, 1, 1], dtype=int32)
    # kmeans.predict([[0, 0], [4, 4]])
    # array([0, 1], dtype=int32)
    print kmeans.cluster_centers_
    return kmeans.labels_

def url_group_map():
    filename = "spam_category.json"
    spam_group = json.load(open(filename, 'r'))
    group_to_id = {}

    for url_dic in spam_group:
        for url, url_category in url_dic.iteritems():
            for category, group_info in url_category.iteritems():
                for single_group in group_info['spam_group_id']:
                    group_to_id[url + str(single_group)] = category

    return group_to_id

# Print the cluster centroids

url_group_to_id = url_group_map()
print(url_group_to_id)
#clusters = kprototypes_cluster(data)
clusters = kmeans_cluter(data)
print(clusters)

for cluster in range(n_clusters):
    print cluster
    print([url_group_to_id[y[index]] for index, p in enumerate(clusters) if p == cluster])
    print([y[index] for index, p in enumerate(clusters) if p == cluster])
    # print
# print y
