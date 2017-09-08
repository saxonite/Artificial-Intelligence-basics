import json, math
euler = []
# class Path:

    # def __init__(self):
    # # Load the path from a file and convert it into a list of coordinates
    #     self.loadPath('Path-to-bed.json')
    #     self.vecPath = self.vectorizePath()
    
# def loadPath(file_name):

#     with open(file_name) as path_file:
#         data = json.load(path_file)

    # self.path = data

# def vectorizePath(data):
#     vecArray = [{'X': v['Pose']['Position']['X'],'Y': v['Pose']['Position']['Y'],'Z': v['Pose']['Position']['Z']}for v in data]
#     print vecArray
def vectorizePath(data):
	"""
	This function outputs the positon of the potential carrots on the path parsed from the JSON files

	Output format : [[X,Y,Z]]
	"""
	vecArray = [[v['Pose']['Position']['X'], v['Pose']['Position']['Y'], v['Pose']['Position']['Z']] for v in data]
	# print "VECTOR ARRAY", vecArray

def heading(data):
	"""
	This function outputs the heading angle (in degrees) of the potential carrots on the path parsed from the JSON files

	Output format : [[X,Y,Z]]
	"""
	head = [[h['Pose']['Orientation']['W'], h['Pose']['Orientation']['X'],h['Pose']['Orientation']['Y'],h['Pose']['Orientation']['Z']]for h in data]
	for i in range(len(head)-1):
		w = head[i][0]
		x = head[i][1]
		y = head[i][2]
		z = head[i][3]
		quat2euler(w,x,y,z)
		euler.append([X,Y,Z])
	# print "HEADING", head
	print euler

def quat2euler(w,x,y,z):
	global X,Y,Z
	ysqr = y*y
	
	t0 = +2.0 * (w * x + y*z)
	t1 = +1.0 - 2.0 * (x*x + ysqr)
	X = math.degrees(math.atan2(t0, t1))
	
	t2 = +2.0 * (w*y - z*x)
	t2 =  1 if t2 > 1 else t2
	t2 = -1 if t2 < -1 else t2
	Y = math.degrees(math.asin(t2))
	
	t3 = +2.0 * (w * z + x*y)
	t4 = +1.0 - 2.0 * (ysqr + z*z)
	Z = math.degrees(math.atan2(t3, t4))
	return [X,Y,Z]
	
	# print "X", X, "Y", Y, "Z", Z, "\n"
	

if __name__ == '__main__':
	file_name = "Path-to-bed.json"
	with open(file_name) as path_file:
        	data = json.load(path_file)

	heading(data)
	vectorizePath(data)
	
