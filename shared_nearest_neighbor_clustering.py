"""
http://www.georeference.org/forum/t76320 by jonno
"""


import math

class kinf:
    def __init__(self, p, dt, nsn, il):
        self.Point = p
        self.distance_to = dt
        self.NumOfSharedNeigh = nsn
        self.is_linked = il


class inf:
    def __init__(self, p, t, cx, cy, kn, d, cid):
        self.Point = int(p)
        self.Type = t
        self.coord_x = float(cx)
        self.coord_y = float(cy)
        self.knearest = []
        self.Density = -1
        self.ClusterID = cid


class SSNClusters():
    def __init__(self, points_list, neighbors=7, radius=None):
        self.ssn_array = []
        self.K = neighbors

        if radius is None:
            self.EPS = int(self.K * 3 / 10)
        else:
            self.EPS = radius
        self.MinPts = int(self.K * 7 / 10)
        self.MyColec = []
        self.cluster_dict = {}

        count = 1
        for point in points_list:
            p = inf(count, '', point[0], point[1], None, None, -1)
            self.ssn_array.insert(count, p)
            count += 1

    def insertKN(self, i, val):
        kn = self.ssn_array[i].knearest
        kn.insert(len(kn)-1, val)

    def get_knearest(self):
        for i in range(0, len(self.ssn_array)):
            count = 0
            for j in range(0, len(self.ssn_array)):
                if i != j:
                    count += 1
                    dist = math.sqrt(((self.ssn_array[i].coord_x - self.ssn_array[j].coord_x) * (self.ssn_array[i].coord_x - self.ssn_array[j].coord_x))
                                     + ((self.ssn_array[i].coord_y - self.ssn_array[j].coord_y) * (self.ssn_array[i].coord_y - self.ssn_array[j].coord_y)))

                    if count <= self.K:
                        kn = kinf(self.ssn_array[j].Point, dist, None, 0)
                        self.insertKN(i, kn)

                    else:
                        index = self.get_max(self.ssn_array[i].knearest)
                        if self.ssn_array[i].knearest[index].distance_to > dist:
                            self.ssn_array[i].knearest[index].distance_to = dist
                            self.ssn_array[i].knearest[index].Point = self.ssn_array[j].Point
                            self.ssn_array[i].knearest[index].is_linked = 0

        self.order_knearest_array()

    def order_knearest_array(self):
        temp = []
        for i in range(0, len(self.ssn_array)):
            for j in range(0, len(self.ssn_array[i].knearest)-1):
                for l in range((j + 1), len(self.ssn_array[i].knearest)):
                    if self.ssn_array[i].knearest[j].distance_to > self.ssn_array[i].knearest[l].distance_to:
                        temp.insert(0, self.ssn_array[i].knearest[j])
                        self.ssn_array[i].knearest[j] = self.ssn_array[i].knearest[l]
                        self.ssn_array[i].knearest[l] = temp[0]

    def shared_nearest(self):
        for i in range(0, len(self.ssn_array)):
            for j in range(0, len(self.ssn_array[i].knearest)):
                count_share = 0
                for l in range(0, len(self.ssn_array)):
                    if self.ssn_array[i].knearest[j].Point == self.ssn_array[l].Point:
                        for n in range(0, len(self.ssn_array[l].knearest)):
                            if self.ssn_array[l].knearest[n].Point == self.ssn_array[i].Point:
                                self.ssn_array[i].knearest[j].is_linked = 1

                        if self.ssn_array[i].knearest[j].is_linked == 0:
                            self.ssn_array[i].knearest[j].NumOfSharedNeigh = 0
                        else:
                            for n in range(0, len(self.ssn_array[l].knearest)):
                                for m in range(0, len(self.ssn_array[l].knearest)):
                                    if self.ssn_array[l].knearest[m].Point == self.ssn_array[i].knearest[n].Point:
                                        count_share += 1

                            self.ssn_array[i].knearest[j].NumOfSharedNeigh = count_share

                            break

    def calculate_density(self):
        for i in range(0, len(self.ssn_array)):
            for j in range(0, len(self.ssn_array[i].knearest)):
                if self.ssn_array[i].knearest[j].NumOfSharedNeigh >= self.EPS:
                    self.ssn_array[i].Density = self.ssn_array[i].Density + (1 * self.ssn_array[i].knearest[j].is_linked)
                else:
                    self.ssn_array[i].Density = self.ssn_array[i].Density + (0 * self.ssn_array[i].knearest[j].is_linked)

    def check_cores(self):
        for i in range(0, len(self.ssn_array)):
            if self.ssn_array[i].Density >= self.MinPts:
                self.ssn_array[i].Type = 'Core'
                self.MyColec.insert(len(self.MyColec), i)
            else:
                self.ssn_array[i].Type = 'Border'
                self.MyColec.insert(len(self.MyColec), i)

    def build_clusters(self):
        ClusterID = 0
        for i in range(0, len(self.ssn_array)):
            if self.ssn_array[i].Type != 'Noise' and self.ssn_array[i].ClusterID == -1:
                ClusterID += 1
                self.ssn_array[i].ClusterID = ClusterID
                self.cluster_neighbors(self.ssn_array[i].Point, ClusterID)

        for i in range(0, len(self.ssn_array)):
            if self.ssn_array[i].ClusterID > 0:
                if self.ssn_array[i].ClusterID in self.cluster_dict.keys():
                    self.cluster_dict[self.ssn_array[i].ClusterID].append((self.ssn_array[i].coord_x, self.ssn_array[i].coord_y))
                else:
                    self.cluster_dict[self.ssn_array[i].ClusterID] = [(self.ssn_array[i].coord_x, self.ssn_array[i].coord_y)]
        return ClusterID

    def cluster_neighbors(self, Point, ClusterID):
        neighbors = []
        index = None
        new_point = None
        for m in range(0, len(self.ssn_array)):
            if self.ssn_array[m].Point == Point:
                neighbors = self.ssn_array[m].knearest # all k's of the ssn_array(m).point
                index = m
                break
        for j in range(0, len(neighbors)):
            new_point = neighbors[j].Point # 1 of the ssn_array(m).point K's
            for l in range(0, len(self.ssn_array)):
                if self.ssn_array[l].Point == new_point:
                    if self.ssn_array[l].Type != 'Noise' and self.ssn_array[l].ClusterID == -1 and neighbors[j].NumOfSharedNeigh >= self.EPS:
                        self.ssn_array[l].ClusterID = ClusterID
                        self.cluster_neighbors(new_point, ClusterID)

    def check_similarity(self, i, j):
        result = 0
        for m in range(0, len(self.ssn_array[i].knearest)):
            if self.ssn_array[i].Point == self.ssn_array[j].knearest[m].Point:
                for n in range(0, len(self.ssn_array[i].knearest)):
                    if self.ssn_array[j].Point == self.ssn_array[i].knearest[n].Point:
                         result = self.ssn_array[i].knearest[n].Point
                         break
        return result

    def noise_points(self):
        similarity1 = None
        similarity2 = None
        for i in range(0, len(self.ssn_array)):
            similarity1 = 0
            if self.ssn_array[i].Type == 'Border':
                for j in range(0, len(self.MyColec)):
                    similarity2 = self.check_similarity(i, j)
                    if similarity2 > similarity1:
                        similarity1 = similarity2
                if similarity1 < self.EPS:
                    self.ssn_array[i].Type = 'Noise'
                    self.ssn_array[i].ClusterID = 0

    def get_max(self, kn):
        max = float
        for idx in range(0, len(kn)):
            if idx == 0:
                max = kn[idx].distance_to
                max_idx = idx
            elif kn[idx].distance_to > max:
                max = kn[idx].distance_to
                max_idx = idx
        return max_idx

    def get_clusters(self):
        self.get_knearest()
        self.shared_nearest()
        self.calculate_density()
        self.check_cores()
        self.noise_points()
        self.build_clusters()
        return self.cluster_dict
