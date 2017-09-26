"""
Example demonstrating how to communicate with Microsoft Robotic Developer
Studio 4 via the Lokarria http interface. 

Author: Chaitanya
"""

MRDS_URL = 'localhost:50000'

import httplib, json, time
from math import *

HEADERS = {"Content-type": "application/json", "Accept": "text/json"}

class UnexpectedResponse(Exception): pass

def postSpeed(angularSpeed,linearSpeed):
	"""Sends a speed command to the MRDS server"""
	mrds = httplib.HTTPConnection(MRDS_URL)
	params = json.dumps({'TargetAngularSpeed':angularSpeed,'TargetLinearSpeed':linearSpeed})
	mrds.request('POST','/lokarria/differentialdrive',params,HEADERS)
	response = mrds.getresponse()
	status = response.status
	#response.close()
	if status == 204:
		return response
	else:
		raise UnexpectedResponse(response)

def getLaser():
	"""Requests the current laser scan from the MRDS server and parses it into a dict"""
	mrds = httplib.HTTPConnection(MRDS_URL)
	mrds.request('GET','/lokarria/laser/echoes')
	response = mrds.getresponse()
	if (response.status == 200):
		laserData = response.read()
		response.close()
		return json.loads(laserData)
	else:
		return response
	
def getLaserAngles():
	"""Requests the current laser properties from the MRDS server and parses it into a dict"""
	mrds = httplib.HTTPConnection(MRDS_URL)
	mrds.request('GET','/lokarria/laser/properties')
	response = mrds.getresponse()
	if (response.status == 200):
		laserData = response.read()
		response.close()
		properties = json.loads(laserData)
		beamCount = int((properties['EndAngle']-properties['StartAngle'])/properties['AngleIncrement'])
		a = properties['StartAngle']#+properties['AngleIncrement']
		angles = []
		while a <= properties['EndAngle']:
			angles.append(a)
			a+=pi/180 #properties['AngleIncrement']
		#angles.append(properties['EndAngle']-properties['AngleIncrement']/2)
		return angles
	else:
		raise UnexpectedResponse(response)

def getPose():
	global x,y,z
	"""Reads the current position and orientation from the MRDS"""
	mrds = httplib.HTTPConnection(MRDS_URL)
	mrds.request('GET','/lokarria/localization')
	response = mrds.getresponse()
	if (response.status == 200):
		poseData = response.read()
		response.close()
		pose =  json.loads(poseData)
		x = pose['Pose']['Position']['X']
		y = pose['Pose']['Position']['Y']
		z = pose['Pose']['Position']['Z']
		return pose
	else:
		return UnexpectedResponse(response)

def bearing(q):
	return rotate(q,{'X':1,'Y':1,"Z":0})

def rotate(q,v):
	return vector(qmult(qmult(q,quaternion(v)),conjugate(q)))

def quaternion(v):
	q=v.copy()
	q['W']=0.0;
	return q

def vector(q):
	v={}
	v["X"]=q["X"]
	v["Y"]=q["Y"]
	v["Z"]=q["Z"]
	return v

def conjugate(q):
	qc=q.copy()
	qc["X"]=-q["X"]
	qc["Y"]=-q["Y"]
	qc["Z"]=-q["Z"]
	return qc

def qmult(q1,q2):
	q={}
	q["W"]=q1["W"]*q2["W"]-q1["X"]*q2["X"]-q1["Y"]*q2["Y"]-q1["Z"]*q2["Z"]
	q["X"]=q1["W"]*q2["X"]+q1["X"]*q2["W"]+q1["Y"]*q2["Z"]-q1["Z"]*q2["Y"]
	q["Y"]=q1["W"]*q2["Y"]-q1["X"]*q2["Z"]+q1["Y"]*q2["W"]+q1["Z"]*q2["X"]
	q["Z"]=q1["W"]*q2["Z"]+q1["X"]*q2["Y"]-q1["Y"]*q2["X"]+q1["Z"]*q2["W"]
	return q
	
def getBearing():
	"""Returns the XY Orientation or Heading"""
	return bearing(getPose()['Pose']['Orientation'])

def vectorizePath(data):
	global vecArray
	"""
	This function outputs the positon of the potential carrots on the path parsed from the JSON files

	Output format : [[X,Y,Z]]
	"""
	vecArray = [[v['Pose']['Position']['X'], v['Pose']['Position']['Y'], v['Pose']['Position']['Z']] for v in data]
	return vecArray

def quat_disp():
	"""Compute all the to get the linear and the angular speed"""
	pose = getPose()
	"""Decide the goal coordinates dependent on the distance from the robot"""
	while 1:
		L = sqrt((vecArray[0][0]-x)**2 + (vecArray[0][1]-y)**2)
		if L < 0.4:
			del vecArray[0]
		else:
			break
	print "Linear Displacement from the goal =", L

	"""Angle between the RCS and WCS"""
	robo_head = getBearing()
	robo_ang = atan2(robo_head['Y'], robo_head['X'])

	"""Angle between the goal and WCS"""
	goal_ang = atan2(vecArray[0][1]-y, vecArray[0][0]-x)

	goal_quad = 0
	robo_quad = 0
	if ((goal_ang > pi/2) & (goal_ang < pi)):
	  goal_quad = 4
	if ((goal_ang < -pi/2) & (goal_ang > -pi)):
	  goal_quad = 3
	if ((robo_ang > pi/2) & (robo_ang < pi)):
	  robo_quad = 4
	if ((robo_ang < -pi/2) & (robo_ang > -pi)):
	  robo_quad = 3

	if (goal_quad == 3 & robo_quad == 4 | (robo_ang > goal_ang) & (abs(goal_ang - robo_ang) > pi)):
	  final_ang = goal_ang - robo_ang + 2*pi
	  
	elif (goal_quad == 4 & robo_quad == 3 | (robo_ang < goal_ang) & (abs(goal_ang - robo_ang) > pi)):
	  final_ang = goal_ang - robo_ang - 2*pi
	  
	else:
	  final_ang = goal_ang - robo_ang

	# """Project goal on RCS"""
	disp = sin(final_ang) / L
	print "Projection =", disp

	"""Constant Linear Speed"""
	lin_speed = 0.5
	
	
	"""Variable/Dependent Angular Speed"""
	ang_speed = 0.1 / (L**2/(2*disp))
	
	print "Angular speed =", ang_speed
	postSpeed(ang_speed,lin_speed) 
	# time.sleep(0.1)
	# del vecArray[0]

if __name__ == '__main__':
	# global lin_speed, ang_speed, L
	print 'Sending commands to MRDS server', MRDS_URL
	file_name = "Path-to-bed.json"
	with open(file_name) as path_file:
        	data = json.load(path_file)
	vecArray = vectorizePath(data)
	print 'Telling the robot to go to the target.'
	t1 = time.time()
	while vecArray:
		try:
			quat_disp()  
		except:
			postSpeed(0,0)
			t2 = time.time() 
			break	
		# except UnexpectedResponse, ex:
		# 	print 'Unexpected response from server when sending speed commands:', ex
		try:
			laser = getLaser()
			laserAngles = getLaserAngles()
			print 'The rightmost laser bean has angle %.3f deg from x-axis (straight forward) and distance %.3f meters.'%(
				laserAngles[0],laser['Echoes'][0])
			print 'Beam 1: %.3f Beam 269: %.3f Beam 270: %.3f'%( laserAngles[0]*180/pi, laserAngles[269]*180/pi, laserAngles[270]*180/pi)
		except UnexpectedResponse, ex:
			print 'Unexpected response from server when reading laser data:', ex

		try:
			pose = getPose()
			# print 'Current position: ', pose['Pose']['Position']

			print 'Current X position: ', pose['Pose']['Position']['X']
			print 'Current Y position: ', pose['Pose']['Position']['Y']
			print 'Current Z position: ', pose['Pose']['Position']['Z']

			# for t in range(30):    
			print 'Current heading vector: X:{X:.3}, Y:{Y:.3}'.format(**getBearing())
			# time.sleep(1)
		except UnexpectedResponse, ex:
			print 'Unexpected response from server when reading position:', ex
	print "Total time taken =", t2-t1
