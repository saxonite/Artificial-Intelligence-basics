"""
Example demonstrating how to communicate with Microsoft Robotic Developer
Studio 4 via the Lokarria http interface. 

Author: Erik Billing (billing@cs.umu.se)

Updated by Ola Ringdahl 204-09-11
"""

MRDS_URL = 'localhost:50000'

import httplib, json, time, path
from math import *
# import numpy as np
import path

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
	global x,y,z,W,X,Y,Z
	"""Reads the current position and orientation from the MRDS"""
	mrds = httplib.HTTPConnection(MRDS_URL)
	mrds.request('GET','/lokarria/localization')
	response = mrds.getresponse()
	if (response.status == 200):
		poseData = response.read()
		response.close()
		print "YOLO BITCHES...!!"
		print "\n"
		pose =  json.loads(poseData)
		x = pose['Pose']['Position']['X']
		y = pose['Pose']['Position']['Y']
		z = pose['Pose']['Position']['Z']
		W = pose['Pose']['Orientation']['W']
		X = pose['Pose']['Orientation']['X']
		Y = pose['Pose']['Orientation']['Y']
		Z = pose['Pose']['Orientation']['Z']
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

def quat_disp():
	"""Determine the displacement of the robot from its position"""
	global lin_speed, ang_speed
	pose = getPose()

	lin_speed = (sqrt((0.92469644546508789-x)**2+(1.8556557893753052-y)**2+(0.077600695192813873-z)**2))/10
	print lin_speed
	# dot_product = sum((a*b) for a, b in zip(v1, v2))

	ang_speed = ((path.quat2euler(0.4858168363571167, -6.0485918496056E-09, 4.6814268017669747E-08, 0.87406432628631592)[2]-\
				path.quat2euler(W, X, Y, Z)[2]))/10
	print ang_speed

def PID(y, yc):
	"""Calculate System Input using a PID Controller

	Arguments:
	y  .. Measured Output of the System
	yc .. Desired Output of the System
	h  .. Sampling Time
	Kp .. Controller Gain Constant
	Ti .. Controller Integration Constant
	Td .. Controller Derivation Constant
	u0 .. Initial state of the integrator
	e0 .. Initial error

	Make sure this function gets called every h seconds!
	"""
	h=1
	Ti=1
	Td=1
	Kp=1
	u0=0
	e0=0

	# Initialization
	ui_prev = u0
	e_prev = e0

	# Error between the desired and actual output
	e = yc - y

	# Integration Input
	ui = ui_prev + 1/Ti * h*e
	# Derivation Input
	ud = 1/Td * (e - e_prev)/h

	# Adjust previous values
	e_prev = e
	ui_prev = ui

	# Calculate input for the system
	u = Kp * (e + ui + ud)

	return u


# def unit_vector(vector):
#     """ Returns the unit vector of the vector"""
#     return vector / np.linalg.norm(vector)

# def angle_between(v1, v2):
#     """ Returns the angle in radians between vectors 'v1' and 'v2'"""
#     v1_u = unit_vector(v1)
#     v2_u = unit_vector(v2)
#     return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

if __name__ == '__main__':
	# global lin_speed, ang_speed
	
	print 'Sending commands to MRDS server', MRDS_URL
	while 1:
		quat_disp()
		try:
			# print 'Telling the robot to go streight ahead.'
			# response = postSpeed(0,0.1) 
			# print 'Waiting for a while...'
			# time.sleep(3)
			print 'Telling the robot to go to the target.'
			response = postSpeed(ang_speed,lin_speed)        
		except UnexpectedResponse, ex:
			print 'Unexpected response from server when sending speed commands:', ex

		try:
			laser = getLaser()
			laserAngles = getLaserAngles()
			print 'The rightmost laser bean has angle %.3f deg from x-axis (streight forward) and distance %.3f meters.'%(
				laserAngles[0],laser['Echoes'][0]
			)
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

		time.sleep(0.5)

		if (0.92469644546508789-x) == (1.8556557893753052-y) == (0.077600695192813873-z) == 0:
			print 'The robot has reached the destination'
			response = postSpeed(0,0)
			break

	

	
