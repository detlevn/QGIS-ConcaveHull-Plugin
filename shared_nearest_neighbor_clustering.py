"""
http://www.georeference.org/forum/t76320 by jonno
"""


import math

class kinf:
    def __init__(self, p, dt, nsn, il):
        self.Point = p
        self.DistTo = dt
        self.NumOfSharedNeigh = nsn
        self.IsLinked = il


class inf:
    def __init__(self, p, t, cx, cy, kn, d, cid):
        self.Point = int(p)
        self.Type = t
        self.CoordX = float(cx)
        self.CoordY = float(cy)
        self.knearest = []
        self.Density = -1
        self.ClusterID = cid


class SSNClusters():
    def __init__(self, points_list, neighbors=7, radius=None):
        self.SNNArray = []
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
            self.SNNArray.insert(count, p)
            count += 1


    def insertKN(self, i, val):
        kn = self.SNNArray[i].knearest
        kn.insert(len(kn)-1, val)


    def GetKnearest(self):
        for i in range(0, len(self.SNNArray)):
            Count = 0
            for j in range(0, len(self.SNNArray)):
                if i != j:
                    Count += 1
                    dist = math.sqrt(((self.SNNArray[i].CoordX - self.SNNArray[j].CoordX) * (self.SNNArray[i].CoordX - self.SNNArray[j].CoordX))
                                     + ((self.SNNArray[i].CoordY - self.SNNArray[j].CoordY) * (self.SNNArray[i].CoordY - self.SNNArray[j].CoordY)))

                    if Count <= self.K:
                        kn = kinf(self.SNNArray[j].Point, dist, None, 0)
                        self.insertKN(i, kn)

                    else:
                        Ind = self.GetMax(self.SNNArray[i].knearest)
                        if self.SNNArray[i].knearest[Ind].DistTo > dist:
                            self.SNNArray[i].knearest[Ind].DistTo = dist
                            self.SNNArray[i].knearest[Ind].Point = self.SNNArray[j].Point
                            self.SNNArray[i].knearest[Ind].IsLinked = 0

        self.OrderKnearestArray()


    def OrderKnearestArray(self):
        temp = []
        for i in range(0, len(self.SNNArray)):
            for j in range(0, len(self.SNNArray[i].knearest)-1):
                for l in range((j + 1), len(self.SNNArray[i].knearest)):
                    if self.SNNArray[i].knearest[j].DistTo > self.SNNArray[i].knearest[l].DistTo:
                        temp.insert(0, self.SNNArray[i].knearest[j])
                        self.SNNArray[i].knearest[j] = self.SNNArray[i].knearest[l]
                        self.SNNArray[i].knearest[l] = temp[0]


    def SharedNearest(self):
        for i in range(0, len(self.SNNArray)):
            for j in range(0, len(self.SNNArray[i].knearest)):
                CountShare = 0
                for l in range(0, len(self.SNNArray)):
                    if self.SNNArray[i].knearest[j].Point == self.SNNArray[l].Point:
                        for n in range(0, len(self.SNNArray[l].knearest)):
                            if self.SNNArray[l].knearest[n].Point == self.SNNArray[i].Point:
                                self.SNNArray[i].knearest[j].IsLinked = 1

                        if self.SNNArray[i].knearest[j].IsLinked == 0:
                            self.SNNArray[i].knearest[j].NumOfSharedNeigh = 0
                        else:
                            for n in range(0, len(self.SNNArray[l].knearest)):
                                for m in range(0, len(self.SNNArray[l].knearest)):
                                    if self.SNNArray[l].knearest[m].Point == self.SNNArray[i].knearest[n].Point:
                                        CountShare += 1
                                        #break

                            self.SNNArray[i].knearest[j].NumOfSharedNeigh = CountShare

                            break


    def CalcDensity(self):
        for i in range(0, len(self.SNNArray)):
            for j in range(0, len(self.SNNArray[i].knearest)):
                if self.SNNArray[i].knearest[j].NumOfSharedNeigh >= self.EPS:
                    self.SNNArray[i].Density = self.SNNArray[i].Density + (1 * self.SNNArray[i].knearest[j].IsLinked)
                else:
                    self.SNNArray[i].Density = self.SNNArray[i].Density + (0 * self.SNNArray[i].knearest[j].IsLinked)


    def CheckCores(self):
        for i in range(0, len(self.SNNArray)):
            if self.SNNArray[i].Density >= self.MinPts:
                self.SNNArray[i].Type = 'Core'
                self.MyColec.insert(len(self.MyColec), i)
            else:
                self.SNNArray[i].Type = 'Border'
                self.MyColec.insert(len(self.MyColec), i)


    def BuildClusters(self):
        ClusterID = 0
        for i in range(0, len(self.SNNArray)):
            if self.SNNArray[i].Type != 'Noise' and self.SNNArray[i].ClusterID == -1:
                ClusterID += 1
                self.SNNArray[i].ClusterID = ClusterID
                self.ClusterNeighbours(self.SNNArray[i].Point, ClusterID)

        for i in range(0, len(self.SNNArray)):
            if self.SNNArray[i].ClusterID > 0:
                if self.SNNArray[i].ClusterID in self.cluster_dict.keys():
                    self.cluster_dict[self.SNNArray[i].ClusterID].append((self.SNNArray[i].CoordX, self.SNNArray[i].CoordY))
                else:
                    self.cluster_dict[self.SNNArray[i].ClusterID] = [(self.SNNArray[i].CoordX, self.SNNArray[i].CoordY)]
        return ClusterID


    def ClusterNeighbours(self, Point, ClusterID):
        Neighbours = []
        Index = None
        NovoPto = None
        for m in range(0, len(self.SNNArray)):
            if self.SNNArray[m].Point == Point:
                Neighbours = self.SNNArray[m].knearest # all k's of the Snnarray(m).point
                Index = m
                break
        for j in range(0, len(Neighbours)):
            NovoPto = Neighbours[j].Point # 1 of the Snnarray(m).point K's
            for l in range(0, len(self.SNNArray)):
                if self.SNNArray[l].Point == NovoPto:
                    if self.SNNArray[l].Type != 'Noise' and self.SNNArray[l].ClusterID == -1 and Neighbours[j].NumOfSharedNeigh >= self.EPS:
                        self.SNNArray[l].ClusterID = ClusterID
                        self.ClusterNeighbours(NovoPto, ClusterID)


    def CheckSimilarity(self, i, j):
        result = 0
        for m in range(0, len(self.SNNArray[i].knearest)):
            if self.SNNArray[i].Point == self.SNNArray[j].knearest[m].Point:
                for n in range(0, len(self.SNNArray[i].knearest)):
                    if self.SNNArray[j].Point == self.SNNArray[i].knearest[n].Point:
                         result = self.SNNArray[i].knearest[n].Point
                         break
        return result


    def NoisePoints(self):
        Similarity1 = None
        Similarity2 = None
        for i in range(0, len(self.SNNArray)):
            Similarity1 = 0
            if self.SNNArray[i].Type == 'Border':
                for j in range(0, len(self.MyColec)):
                    Similarity2 = self.CheckSimilarity(i, j)
                    if Similarity2 > Similarity1:
                        Similarity1 = Similarity2
                if Similarity1 < self.EPS:
                    self.SNNArray[i].Type = 'Noise'
                    self.SNNArray[i].ClusterID = 0


    def GetMax(self, kn):
        Max = float
        for i in range(0, len(kn)):
            if i == 0:
                Max = kn[i].DistTo
                MaxInd = i
            elif kn[i].DistTo > Max:
                Max = kn[i].DistTo
                MaxInd = i
        return MaxInd

    def get_clusters(self):
        self.GetKnearest()
        self.SharedNearest()
        self.CalcDensity()
        self.CheckCores()
        self.NoisePoints()
        self.BuildClusters()
        return self.cluster_dict


clusters = SSNClusters([(1, 0, 0), (2, 1, 0), (3, 0, 1), (4, 1, 1), (5, 0.5, 0.5),
                        (6, 50, 50), (7, 51, 51), (8, 52, 52), (9, 50, 53), (10, 50, 49),
                        (11, 100, 0), (12, -50, -50), (13, -48, -48)])
print clusters.get_clusters()
