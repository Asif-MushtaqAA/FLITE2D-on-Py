import numpy as np

def conelem(mesh):
    tri = mesh['connec']
    xy = mesh['xy']
    NoPoints = len(xy)
    NoElem = len(tri)

    # Check and reorder connectivity if necessary
    def reorder_connectivity(tri, xy):
        for i in range(NoElem):
            xy12 = xy[tri[i, 0]] - xy[tri[i, 1]]
            xy32 = xy[tri[i, 2]] - xy[tri[i, 1]]
            te = xy32[0] * xy12[1] - xy32[1] * xy12[0]
            if te < 0:
                tri[i, [1, 2]] = tri[i, [2, 1]]
        return tri

    tri = reorder_connectivity(tri, xy)
    mesh['connec'] = tri

    # Create lhowm and lwhere arrays efficiently
    lhowm = np.bincount(tri.flatten(), minlength=NoPoints)
    lwhere = np.cumsum(lhowm) - lhowm

    ConElemN = np.sum(lhowm)
    conelem = np.zeros(ConElemN, dtype=int)

    lhowm.fill(0)
    for ie in range(NoElem):
        for in_ in range(3):
            ip = tri[ie, in_]
            lhowm[ip] += 1
            j = lwhere[ip] + lhowm[ip] - 1
            conelem[j] = ie

    # Construct iside efficiently
    iside = [[] for _ in range(NoPoints)]
    for ip in range(NoPoints):
        iele = lhowm[ip]
        if iele > 0:
            iwhere = lwhere[ip]
            ip1 = ip
            for iel in range(1, iele + 1):
                ie = conelem[iwhere + iel - 1]
                in1 = np.where(tri[ie] == ip)[0][0] + 1
                for j in range(2):
                    in2 = (in1 + j) % 3
                    ip2 = tri[ie, in2]
                    if ip2 >= ip1:
                        found = False
                        for item in iside[ip1]:
                            if item[1] == ip2:
                                item[2 + j] = ie
                                found = True
                                break
                        if not found:
                            iside[ip1].append([ip1, ip2, 0, 0])
                            iside[ip1][-1][2 + j] = ie

            # Post-process iside
            for item in iside[ip1]:
                if item[2] == 0:
                    item[2] = item[3]
                    item[3] = 0
                    item[0] = item[1]
                    item[1] = ip1

    # Create intmel array efficiently
    intmel = np.zeros((NoElem, 3), dtype=int)
    for ip1, items in enumerate(iside):
        for item in items:
            ip1, ie1, ie2 = item[0], item[2], item[3]
            if ie1 != 0:
                i1, i2, i3 = tri[ie1]
                ipos = np.where([ip1 == i1, ip1 == i2, ip1 == i3])[0][0] + 1
                intmel[ie1, ipos - 1] = ie2
            if ie2 != 0:
                i1, i2, i3 = tri[ie2]
                ipos = np.where([ip1 == i1, ip1 == i2, ip1 == i3])[0][0] + 1
                intmel[ie2, ipos - 1] = ie1

    mesh.update({'lhowm': lhowm, 'lwhere': lwhere, 'conelem': conelem, 'iside': iside, 'intmel': intmel})

    return mesh
