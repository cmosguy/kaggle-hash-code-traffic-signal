#%%
print('Extracting data')

# =============================================================================
# load problem file
# =============================================================================
train = open('hashcode.in').read().split('\n')
# %%
# =============================================================================
# problem parameters
# =============================================================================
D, I, S, V, F =  map(int, train[0].split(' '))
streets = [x.split(' ') for x in train[1:S]]
vehicles = [[x.split(' ')[0], x.split(' ')[1:]] for x in train[S+1:S+1+V]]
vehicleState = {i:{
    'streetsNum': k[0], 
    'arr': k[1], 
    'curIndex': 0, 
    'state': 'queue', 
    'timeConsume': 0, 
    'onRoadSecond' : 0} for i,k in enumerate(vehicles)}
dstreets = {str(x[2]): {'B': int(x[0]), 'E': int(x[1]), 'L': int(x[3]), 'C': 0} for x in streets}


# %%
import numpy as np
import pandas as pd
import copy
import random

debugcar = 0 
simulateSeconds = 0
intersetions = 0
streets = 0
cars = 0
scoresWhenOnTime = 0
intersetionTable = [[]]
streetToIndex = {}
carsState = []
intersetionLight = {}
streetEndQueue = {}
streetBlockSeconds = {}
prestreetBlockSeconds = {}
maxScore = 0
maxIntersetionLight = {}
inicarsState = []
iniStreetEndQueue = {}
streetCountMap = {}
endPassCars = {}
maxLenToHash = 5

endList = {4739: 1, 3254: 1, 7894: 1, 6287: 1, 6448: 1, 2191: 1, 7770: 1, 3645: 1, 7788: 1, 5190: 1, 7058: 1, 1355: 1, 7572: 1, 4254: 1, 4968: 1, 1964: 1, 7723: 1, 5655: 1, 7798: 1, 2918: 1, 5964: 1, 7620: 1, 7564: 1, 6051: 1, 2895: 1, 7231: 1, 7030: 1, 7573: 1, 6062: 1, 7829: 1, 4623: 1, 4719: 1, 7112: 1, 2181: 1, 7855: 1, 4749: 1, 4747: 1, 7109: 1, 5140: 1, 4976: 1, 6675: 1, 2662: 1, 3674: 1, 4472: 1, 7021: 1, 2949: 1, 6601: 1, 4293: 1, 5978: 1, 6129: 1, 5042: 1, 5872: 1, 3369: 1, 6567: 1, 5974: 1, 2441: 1, 7371: 1, 1790: 1, 5078: 1, 7661: 1, 5665: 1, 7954: 1, 5279: 1, 6966: 1, 3612: 1, 6104: 1, 6365: 1, 6813: 1, 3580: 1, 3881: 1, 6437: 1, 7086: 1, 4882: 1, 7681: 1, 7747: 1, 4657: 1, 7145: 1, 7933: 1, 7998: 1, 2543: 1, 4129: 1, 4734: 1, 7178: 1, 3856: 1, 7696: 1, 5456: 1, 6987: 1, 7099: 1, 7334: 1, 7659: 1, 7910: 1, 7117: 1, 5033: 1, 6133: 1, 3498: 1, 5959: 1, 3748: 1, 7673: 1, 6661: 1, 7140: 1, 7094: 1, 5462: 1, 6142: 1, 6984: 1, 4092: 1, 2443: 1, 2618: 1, 5247: 1, 6327: 1, 7622: 1, 7627: 1, 4510: 1, 4685: 1, 1553: 1, 4658: 1, 6228: 1, 7174: 1, 7521: 1, 5973: 1, 4047: 1, 6933: 1, 6806: 1, 6346: 1, 5381: 1, 3020: 1, 5897: 1, 3567: 1, 6305: 1, 5074: 1, 6870: 1, 6174: 1, 5145: 1, 6941: 1, 4342: 1, 2725: 1, 7913: 1, 5300: 1, 7473: 1, 5211: 1, 3017: 1, 6341: 1, 7865: 1, 6020: 1, 2982: 1, 3904: 1, 2995: 1, 6920: 1, 7944: 1, 7496: 1, 5412: 1, 6712: 1, 5860: 1, 4554: 1, 6403: 1, 3186: 1, 7474: 1, 4021: 1, 7999: 1, 7556: 1, 3292: 1, 7565: 1, 7018: 1, 6772: 1, 5056: 1, 3764: 1, 3354: 1, 5286: 1, 4547: 1, 4527: 1, 3984: 1, 5542: 1, 6222: 1, 6547: 1, 6575: 1, 4774: 1, 4743: 1, 7924: 1, 5254: 1, 7721: 1, 3372: 1, 5763: 1, 7615: 1, 6432: 1, 5091: 1, 3518: 1, 7438: 1, 6055: 1, 6658: 1, 6110: 1, 7001: 1, 4817: 1, 6735: 1, 3716: 1, 6979: 1, 4643: 1, 4188: 1, 4127: 1, 2407: 1, 4605: 1, 2217: 1, 7477: 1, 4054: 1, 5218: 1, 6921: 1, 5167: 1, 3588: 1, 6673: 1, 6294: 1, 7143: 1, 3494: 1, 3524: 1, 4726: 1, 6642: 1, 4464: 1, 4281: 1, 3763: 1, 5568: 1, 7219: 1, 3743: 1, 6097: 1, 6705: 1, 2866: 1, 6487: 1, 6030: 1, 7213: 1, 5209: 1, 1129: 1, 3894: 1, 7800: 1, 5643: 1, 6991: 1, 7779: 1, 5488: 1, 7828: 1, 4627: 1, 2861: 1, 3907: 1, 3704: 1, 2913: 1, 3490: 1, 7070: 1, 7455: 1, 6876: 1, 6132: 1, 7448: 1, 4677: 1, 6319: 1, 7478: 1, 7256: 1, 2189: 1, 4041: 1, 3762: 1, 6997: 1, 6599: 1, 7658: 1, 7756: 1, 6184: 1, 7352: 1, 4867: 1, 6517: 1, 4081: 1, 7974: 1, 6760: 1, 6364: 1, 4528: 1, 3658: 1, 6725: 1, 3545: 1, 7349: 1, 7320: 1, 7475: 1, 4778: 1, 6740: 1, 7720: 1, 3333: 1, 6439: 1, 6354: 1, 7331: 1, 3058: 1, 7356: 1, 6769: 1, 7497: 1, 7824: 1, 6752: 1, 6064: 1, 5103: 1, 7878: 1, 6990: 1, 4995: 1, 7514: 1, 2891: 1, 4998: 1, 7903: 1, 5782: 1, 6982: 1, 5939: 1, 5556: 1, 7246: 1, 4473: 1, 7306: 1, 7354: 1, 6625: 1, 7840: 1, 7886: 1, 2575: 1, 6805: 1, 4798: 1, 6282: 1, 7794: 1, 5437: 1, 1947: 1, 6122: 1, 6945: 1, 7396: 1, 6383: 1, 7449: 1, 2674: 1, 5235: 1, 5935: 1, 4787: 1, 3219: 1, 5977: 1, 6537: 1, 6595: 1, 7610: 1, 7163: 1, 3765: 1, 5047: 1, 4987: 1, 7689: 1, 5570: 1, 3246: 1, 7114: 1, 4827: 1, 4069: 1, 7363: 1, 5915: 1, 7102: 1, 6518: 1, 7428: 1, 2763: 1, 7426: 1, 6399: 1, 7602: 1, 5711: 1, 4960: 1, 7343: 1, 2116: 1, 4345: 1, 6453: 1, 4819: 1, 5829: 1, 7415: 1, 4898: 1, 6969: 1, 6317: 1, 7039: 1, 4506: 1, 5899: 1, 928: 1, 7707: 1, 7580: 1, 397: 1, 7255: 1, 5737: 1, 7820: 1, 7401: 1, 6333: 1, 5845: 1, 3030: 1, 1569: 1, 7545: 1, 6506: 1, 6569: 1, 5874: 1, 5564: 1, 3315: 1, 7032: 1, 6799: 1, 2579: 1, 952: 1, 6548: 1, 7393: 1, 4154: 1, 7008: 1, 6774: 1, 6071: 1, 6377: 1, 3905: 1, 3914: 1, 4405: 1, 7932: 1, 4633: 1, 7892: 1, 1800: 1, 6027: 1, 7692: 1, 3507: 1, 6977: 1, 7158: 1, 4350: 1, 4689: 1, 2601: 1, 6555: 1, 6171: 1, 7234: 1, 7706: 1, 6653: 1, 7066: 1, 5408: 1, 5001: 1, 6046: 1, 3600: 1, 7290: 1, 7458: 1, 7188: 1, 6296: 1, 5574: 1, 7813: 1, 4471: 1, 7237: 1, 5535: 1, 5649: 1, 7757: 1, 1975: 1, 4949: 1, 4755: 1, 6669: 1, 4738: 1, 6738: 1, 5367: 1, 7726: 1, 3514: 1, 6887: 1, 4030: 1, 687: 1, 1750: 1, 7224: 1, 3266: 1, 7777: 1, 4594: 1, 2360: 1, 1881: 1, 6773: 1, 7277: 1, 1777: 1, 5554: 1, 6693: 1, 3280: 1, 7249: 1, 7888: 1, 3406: 1, 3806: 1, 5100: 1, 6417: 1, 7884: 1, 4933: 1, 6311: 1, 5492: 1, 7251: 1, 7611: 1, 4793: 1, 7347: 1, 6839: 1, 6147: 1, 7744: 1, 6508: 1, 5835: 1, 2981: 1, 6808: 1, 4860: 1, 3497: 1, 5107: 1, 6362: 1, 6344: 1, 2890: 1, 6716: 1, 3101: 1, 1624: 1, 5679: 1, 5900: 1, 6150: 1, 5040: 1, 7479: 1, 7064: 1, 7212: 1, 5573: 1, 6109: 1, 3788: 1, 6479: 1, 7381: 1, 7124: 1, 5153: 1, 6900: 1, 5214: 1, 5697: 1, 4854: 1, 6009: 1, 7831: 1, 6742: 1, 6855: 1, 7126: 1, 6894: 1, 6617: 1, 5971: 1, 7818: 1, 7601: 1, 3790: 1, 7444: 1, 7043: 1, 6522: 1, 7375: 1, 6688: 1, 6828: 1, 6885: 1, 4599: 1, 7618: 1, 7576: 1, 5840: 1, 5754: 1, 3642: 1, 7847: 1, 5702: 1, 3290: 1, 5335: 1, 5703: 1, 5176: 1, 4866: 1, 4327: 1, 3538: 1, 6261: 1, 3013: 1, 7594: 1, 3016: 1, 1838: 1, 5582: 1, 2998: 1, 7503: 1, 7235: 1, 2327: 1, 7243: 1, 2776: 1, 7287: 1, 3772: 1, 3921: 1, 7899: 1, 4871: 1, 5605: 1, 7857: 1, 3413: 1, 4777: 1, 5498: 1, 7718: 1, 5079: 1, 6189: 1, 7926: 1, 5764: 1, 6685: 1, 4847: 1, 5480: 1, 7294: 1, 4165: 1, 4980: 1, 4413: 1, 7614: 1, 5122: 1, 6322: 1, 5932: 1, 4143: 1, 7295: 1, 3960: 1, 7833: 1, 1413: 1, 545: 1, 3837: 1, 7881: 1, 7801: 1, 3576: 1, 7197: 1, 6909: 1, 1916: 1, 1004: 1, 6804: 1, 6907: 1, 7983: 1, 7241: 1, 4724: 1, 5708: 1, 6452: 1, 7923: 1, 7261: 1, 7641: 1, 4620: 1, 7214: 1, 6433: 1, 3488: 1, 5450: 1, 7165: 1, 7171: 1, 7377: 1, 6739: 1, 5156: 1, 7930: 1, 4033: 1, 6746: 1, 5856: 1, 5602: 1, 7690: 1, 2269: 1, 7305: 1, 4040: 1, 7185: 1, 5717: 1, 2678: 1, 5936: 1, 7403: 1, 6268: 1, 6842: 1, 7715: 1, 7739: 1, 6091: 1, 3742: 1, 4768: 1, 6524: 1, 4253: 1, 4484: 1, 2214: 1, 4909: 1, 6825: 1, 7761: 1, 5195: 1, 7007: 1, 5330: 1, 5560: 1, 4067: 1, 7971: 1, 3629: 1, 3985: 1, 6415: 1, 6425: 1, 6376: 1, 7466: 1, 5982: 1, 5278: 1, 6267: 1, 2860: 1, 3801: 1, 5825: 1, 5738: 1, 7285: 1, 5530: 1, 4369: 1, 3531: 1, 6930: 1, 7568: 1, 6520: 1, 5646: 1, 2254: 1, 7131: 1, 6728: 1, 5766: 1, 7639: 1, 5688: 1, 4917: 1, 6266: 1, 7160: 1, 5875: 1, 7204: 1, 4896: 1, 7882: 1, 7044: 1, 6194: 1, 7355: 1, 5796: 1, 5419: 1, 4701: 1, 7834: 1, 7941: 1, 4534: 1, 3976: 1, 5586: 1, 4014: 1, 7764: 1, 7917: 1, 7990: 1, 5699: 1, 7433: 1, 6505: 1, 4298: 1, 2456: 1, 6973: 1, 7532: 1, 7789: 1, 7460: 1, 4660: 1, 7585: 1, 2983: 1, 7653: 1, 7950: 1, 7309: 1, 7861: 1, 6056: 1, 5651: 1, 7555: 1, 7374: 1, 6872: 1, 3145: 1, 5472: 1, 6950: 1, 7994: 1, 6993: 1, 1126: 1, 7982: 1, 6753: 1, 7242: 1, 6373: 1, 4051: 1, 3836: 1, 4944: 1, 3231: 1, 7012: 1, 3312: 1, 5896: 1, 5015: 1, 3093: 1, 3358: 1, 7553: 1, 3432: 1, 2721: 1, 4246: 1, 5021: 1, 5502: 1, 3428: 1, 4926: 1, 5180: 1, 6736: 1, 5622: 1, 3318: 1, 7116: 1, 4425: 1, 6528: 1, 7912: 1, 4145: 1, 6579: 1, 5160: 1, 5911: 1, 4615: 1, 7387: 1, 3102: 1, 4367: 1, 3177: 1, 7940: 1, 6687: 1, 4956: 1, 4332: 1, 2979: 1, 3329: 1, 5561: 1, 7079: 1, 6666: 1, 4870: 1, 6447: 1, 6371: 1, 2666: 1, 5907: 1, 7893: 1, 7316: 1, 7337: 1, 6721: 1, 7656: 1, 2287: 1, 7339: 1, 5698: 1, 5154: 1, 5275: 1, 7853: 1, 2067: 1, 3125: 1, 4117: 1, 5315: 1, 5755: 1, 6757: 1, 4456: 1, 6985: 1}
endList = {2: 1}

def readfile(filename):
    global simulateSeconds
    global intersetions
    global streets
    global cars
    global scoresWhenOnTime
    global intersetionTable
    global streetToIndex
    global carsState
    global intersetionLight
    global streetEndQueue
    global iniStreetEndQueue
    global inicarsState
    f = open(filename)
    line = f.readline()
    line = line.replace('\n', '')
    arr = line.split(' ')
    simulateSeconds = int(arr[0])
    intersetions = int(arr[1])
    streets = int(arr[2])
    cars = int(arr[3])
    scoresWhenOnTime = int(arr[4])
    intersetionTable = {}
    carsState = [-1] * cars
    intersectionLightList = {}
    intersetionLight = {}
    streetEndQueue = {}
    for num in range(0, streets):
        line = f.readline()
        line = line.replace('\n', '')
        arr = line.split(' ')
        start = int(arr[0])
        end = int(arr[1])
        streetsName = arr[2]
        timeToDrive = int(arr[3])
        if streetsName == 'bebc-gf':
            print(streetsName + ' need ' + str(timeToDrive))
        streetToIndex[streetsName] = {'start': start, 'end': end}
        if start not in intersetionTable:
            intersetionTable[start] = {}
        intersetionTable[start][end] = {'streetsName': streetsName, 'timeToDrive': timeToDrive}
        
    #print(intersetionLight[1])
    for num in range(0, cars):
        line = f.readline()
        line = line.replace('\n', '')
        arr = line.split(' ')
        streetsNum = int(arr[0])
        streetsArr = arr[1:]
        for streetName in streetsArr:
            if streetName not in streetCountMap:
                streetCountMap[streetName] = 0
            streetCountMap[streetName] = streetCountMap[streetName] + 1
        carsState[num] = {}
        carsState[num]['streetsNum'] = streetsNum
        carsState[num]['arr'] = streetsArr
        carsState[num]['curIndex'] = 0
        carsState[num]['state'] = 'queue'
        carsState[num]['timeConsume'] = 0
        carsState[num]['onRoadSecond'] = 0
        if streetsArr[0] not in streetEndQueue:
            streetEndQueue[streetsArr[0]] = []
        streetEndQueue[streetsArr[0]].append(num)
    inicarsState = copy.deepcopy(carsState)
    iniStreetEndQueue = copy.deepcopy(streetEndQueue)
    for streetName in streetCountMap:
        end = streetToIndex[streetName]['end']
        if end not in intersectionLightList:
            intersectionLightList[end] = []
        intersectionLightList[end].append({'street': streetName, 'count': streetCountMap[streetName]})
    for end in intersectionLightList:
        streets = intersectionLightList[end]
        intersetionLight[end] = []
        random.shuffle(streets)
        for street in streets:
            #for i in range(0, street['count']):
            for i in range(0, 1):
                intersetionLight[end].append(street['street'])


def iniInter(sub):
    global intersetionLight
    f = open(sub)
    line = f.readline()
    line = line.replace('\n', '')
    n = int(line)
    intersetionLight = {}
    for i in range(0, n):
        line = f.readline()
        line = line.replace('\n', '')
        end = int(line)
        line = f.readline()
        line = line.replace('\n', '')
        num = int(line)
        intersetionLight[end] = []
        for j in range(0, num):
            line = f.readline()
            line = line.replace('\n', '')
            arr = line.split(' ')
            street = arr[0]
            replaceNum = int(arr[1])
            for k in range(0, replaceNum):
                intersetionLight[end].append(street)

def reinit():
    global carsState
    global iniStreetEndQueue
    global inicarsState
    global streetEndQueue
    carsState = copy.deepcopy(inicarsState)
    streetEndQueue = copy.deepcopy(iniStreetEndQueue)
        
        
def simulate():
    global simulateSeconds
    global intersetions
    global streets
    global cars
    global scoresWhenOnTime
    global intersetionTable
    global streetToIndex
    global carsState
    global intersetionLight
    global streetEndQueue
    global streetBlockSeconds
    finishCarNum = 0
    i = -1
    while i < simulateSeconds + 3:
        i = i + 1
        streetQueueToPop = {}
        for j in range(0, cars):
            if j == debugcar:
                print('========second:'+str(i)+'==========')
            if carsState[j]['state'] == 'end':
                continue
            carsState[j]['timeConsume'] = carsState[j]['timeConsume'] + 1
            if carsState[j]['state'] == 'queue':
                streetQueueToPop[carsState[j]['arr'][carsState[j]['curIndex']]] = 1
                
            if carsState[j]['state'] == 'onTheRoad':
                curIndex = carsState[j]['curIndex']
                streetName = carsState[j]['arr'][curIndex]
                streetIndex = streetToIndex[streetName]
                timeToDrive = intersetionTable[streetIndex['start']][streetIndex['end']]['timeToDrive']
                if j== debugcar:
                    print('on the road ' + streetName)
                    print(streetIndex)
                    print('timeToDrive is ' + str(timeToDrive))
                    print(intersetionTable[streetIndex['start']][streetIndex['end']])
                if timeToDrive <= carsState[j]['onRoadSecond']:
                    if curIndex + 1 == len(carsState[j]['arr']):
                        carsState[j]['state'] = 'end'
                        finishCarNum = finishCarNum + 1
                    else:
                        #carsState[j]['curIndex'] = carsState[j]['curIndex'] + 1
                        streetName = carsState[j]['arr'][carsState[j]['curIndex']]
                        carsState[j]['state'] = 'queue'
                        carsState[j]['onRoadSecond'] = 0
                        if streetName not in streetEndQueue:
                            streetEndQueue[streetName] = []
                        streetEndQueue[streetName].append(j)
                        streetQueueToPop[carsState[j]['arr'][carsState[j]['curIndex']]] = 1
                        if j == debugcar:
                            print(streetQueueToPop)
                else:
                    carsState[j]['onRoadSecond'] = carsState[j]['onRoadSecond'] + 1
                    if carsState[j]['onRoadSecond'] == timeToDrive and curIndex + 1 == len(carsState[j]['arr']):
                        carsState[j]['state'] = 'end'
                        finishCarNum = finishCarNum + 1
                        continue;
                        
          
        for street in streetQueueToPop:
            end = streetToIndex[street]['end']
            lightStreet = intersetionLight[end]
            totalWait = len(lightStreet)
            steetToGreenIndex = i%totalWait;
            #print(intersetionLight[end][steetToGreenIndex] + ' is green light when street ' + street + ' is waiting')
            if intersetionLight[end][steetToGreenIndex] == street:
                carPassLightIndex = streetEndQueue[street].pop(0)
                if len(streetEndQueue[street])>0:
                    if street not in streetBlockSeconds:
                        streetBlockSeconds[street] = 0
                    streetBlockSeconds[street] = streetBlockSeconds[street] + len(streetEndQueue[street])
                carsState[carPassLightIndex]['state'] = 'onTheRoad'
                carsState[carPassLightIndex]['curIndex'] = carsState[carPassLightIndex]['curIndex'] + 1
                carsState[carPassLightIndex]['onRoadSecond'] = 1
                curIndex = carsState[carPassLightIndex]['curIndex']
                streetName = carsState[carPassLightIndex]['arr'][curIndex]
                streetIndex = streetToIndex[streetName]
                timeToDrive = intersetionTable[streetIndex['start']][streetIndex['end']]['timeToDrive']
                if carsState[carPassLightIndex]['curIndex'] + 1 == len(carsState[carPassLightIndex]['arr']) and carsState[carPassLightIndex]['onRoadSecond'] == timeToDrive:
                    carsState[carPassLightIndex]['state'] = 'end'
                if carPassLightIndex == debugcar:
                    print('car ' + str(carPassLightIndex) + ' pass ' + street )
            else:
                if street not in streetBlockSeconds:
                    streetBlockSeconds[street] = 0
                streetBlockSeconds[street] = streetBlockSeconds[street] + len(streetEndQueue[street])
        for j in range(0, cars):
            if j == debugcar:
                print('car:'+ str(j))
                print('state:' + carsState[j]['state'])
                print('curIndex: ' + str(carsState[j]['curIndex']))
                print('len:' + str(len(carsState[j]['arr'])))   
                print('onRoadSecond:' + str(carsState[j]['onRoadSecond']))
                print('timeConsume:' + str(carsState[j]['timeConsume']))
                curIndex = carsState[j]['curIndex']
                if curIndex < len(carsState[j]['arr']): 
                    streetName = carsState[j]['arr'][curIndex]
                    streetIndex = streetToIndex[streetName]
                    print('pass street ' + streetName + " need " + str(intersetionTable[streetIndex['start']][streetIndex['end']]['timeToDrive']) )
                print('roads:')
                print(carsState[j]['arr'])
                
                
def calScore():
    global simulateSeconds
    global carsState
    global scoresWhenOnTime
    global maxScore
    global intersetionLight
    global maxIntersetionLight
    global streetBlockSeconds
    global prestreetBlockSeconds
    global streetToIndex
    score = 0
    for car in carsState:
        if car['timeConsume']>simulateSeconds:
            continue
        score = score + simulateSeconds - car['timeConsume'] + scoresWhenOnTime
    print('score: ' + str(score))
    
    for end in intersetionLight:
        streetList = intersetionLight[end]
        for firstName in streetList:
            if firstName != -1:
                break
        curName = firstName
        for i in range(0, len(streetList)):
            if streetList[i] == -1:
                streetList[i] = curName
            else:
                curName = streetList[i]
        
    if maxScore == 0:
        prestreetBlockSeconds = copy.deepcopy(streetBlockSeconds)
        maxIntersetionLight = copy.deepcopy(intersetionLight)
        print('ini')
    if score >= maxScore:
        maxScore = score
        print('cover')
        maxIntersetionLight = copy.deepcopy(intersetionLight)
            
            
    intersetionLight = copy.deepcopy(maxIntersetionLight)
    #reinit()
    #simulate() 
    #score = 0    
    #for car in carsState:
    #    if car['timeConsume']>simulateSeconds:
    #        continue
    #    score = score + simulateSeconds - car['timeConsume'] + scoresWhenOnTime
    #print('after: ' + str(score))
def readTimes():
    file = open('time.txt', 'r')
    return eval(file.read())
def getArr(arr):
    minSlotLen = len(arr)
    maxSlotLen = arr[0]['arriveTime']
    for item in arr:
        if item['arriveTime']<maxSlotLen:
            continue;
        maxSlotLen = item['arriveTime']
    flag = False
    if minSlotLen>6:
        maxSlotLen = 1
    else:
        maxSlotLen = 1000
    for l in range(minSlotLen, maxSlotLen):
        slots = [-1] * l
        flag = True
        streetIndexMap = {}
        for item in arr:
            index = item['arriveTime']%l;
            if slots[index] != -1:
                flag = False
            for streetName in streetIndexMap:
                if streetName != item['street'] and streetIndexMap[streetName]['min'] < index and streetIndexMap[streetName]['max'] > index:
                    flag = False
                    break
            if flag == True:
                slots[index] = item['street']
                if item['street'] not in streetIndexMap:
                    streetIndexMap[item['street']] = {'min': index, 'max': index}
                else:
                    
                    if index > streetIndexMap[item['street']]['max']:
                        streetIndexMap[item['street']]['max'] = index
                    if index < streetIndexMap[item['street']]['min']:
                        streetIndexMap[item['street']]['min'] = index
                    for streetName in streetIndexMap:
                        if streetName != item['street'] and streetIndexMap[streetName]['min'] > streetIndexMap[item['street']]['min']  and streetIndexMap[streetName]['max'] < streetIndexMap[item['street']]['max']:
                            flag = False
                            break
                        if streetName != item['street'] and streetIndexMap[item['street']]['min'] < streetIndexMap[streetName]['max'] and streetIndexMap[streetName]['max'] < streetIndexMap[item['street']]['max']:
                            flag = False
                            break
                        if streetName != item['street'] and streetIndexMap[item['street']]['min'] < streetIndexMap[streetName]['min'] and streetIndexMap[streetName]['min'] < streetIndexMap[item['street']]['max']:
                            flag = False
                            break
            else:
                break
        if flag == True:
            return slots
            
    if flag == False:
        return -1
def optimal():
    global simulateSeconds
    global intersetions
    global streets
    global cars
    global scoresWhenOnTime
    global intersetionTable
    global streetToIndex
    global carsState
    global intersetionLight
    global streetEndQueue
    global streetBlockSeconds
    
    trafficObj = {}
    AreadyHashIndex = {}
    areadyHashStreet = {}
    finishCarNum = 0
    i = -1
    while i < simulateSeconds + 3:
        i = i + 1
        streetQueueToPop = {}
        for j in range(0, cars):
            if j == debugcar:
                print('========second:'+str(i)+'==========')
            if carsState[j]['state'] == 'end':
                continue
            carsState[j]['timeConsume'] = carsState[j]['timeConsume'] + 1
            if carsState[j]['state'] == 'queue':
                streetQueueToPop[carsState[j]['arr'][carsState[j]['curIndex']]] = 1
                
            if carsState[j]['state'] == 'onTheRoad':
                curIndex = carsState[j]['curIndex']
                streetName = carsState[j]['arr'][curIndex]
                streetIndex = streetToIndex[streetName]
                timeToDrive = intersetionTable[streetIndex['start']][streetIndex['end']]['timeToDrive']
                if j== debugcar:
                    print('on the road ' + streetName)
                    print(streetIndex)
                    print('timeToDrive is ' + str(timeToDrive))
                    print(intersetionTable[streetIndex['start']][streetIndex['end']])
                if timeToDrive <= carsState[j]['onRoadSecond']:
                    if curIndex + 1 == len(carsState[j]['arr']):
                        carsState[j]['state'] = 'end'
                        finishCarNum = finishCarNum + 1
                    else:
                        #carsState[j]['curIndex'] = carsState[j]['curIndex'] + 1
                        streetName = carsState[j]['arr'][carsState[j]['curIndex']]
                        carsState[j]['state'] = 'queue'
                        carsState[j]['onRoadSecond'] = 0
                        if streetName not in streetEndQueue:
                            streetEndQueue[streetName] = []
                        streetEndQueue[streetName].append(j)
                        streetQueueToPop[carsState[j]['arr'][carsState[j]['curIndex']]] = 1
                        if j == debugcar:
                            print(streetQueueToPop)
                else:
                    carsState[j]['onRoadSecond'] = carsState[j]['onRoadSecond'] + 1
                    if carsState[j]['onRoadSecond'] == timeToDrive and curIndex + 1 == len(carsState[j]['arr']):
                        carsState[j]['state'] = 'end'
                        finishCarNum = finishCarNum + 1
                        continue;
                        
        alreadPop = {}
        for street in streetQueueToPop:
            end = streetToIndex[street]['end']
            lightStreet = intersetionLight[end]
            if end not in AreadyHashIndex:
                AreadyHashIndex[end] = {}
                areadyHashStreet[end] = {}
            totalWait = len(lightStreet)
            steetToGreenIndex = i%totalWait;
            #print(intersetionLight[end][steetToGreenIndex] + ' is green light when street ' + street + ' is waiting')
            if end not in endList:
                if intersetionLight[end][steetToGreenIndex] == street:
                    AreadyHashIndex[end][steetToGreenIndex] = 1
                    areadyHashStreet[end][street] = 1
                    carPassLightIndex = streetEndQueue[street].pop(0)
                    if len(streetEndQueue[street])>0:
                        if street not in streetBlockSeconds:
                            streetBlockSeconds[street] = 0
                        streetBlockSeconds[street] = streetBlockSeconds[street] + len(streetEndQueue[street])
                    carsState[carPassLightIndex]['state'] = 'onTheRoad'
                    carsState[carPassLightIndex]['curIndex'] = carsState[carPassLightIndex]['curIndex'] + 1
                    carsState[carPassLightIndex]['onRoadSecond'] = 1
                    curIndex = carsState[carPassLightIndex]['curIndex']
                    streetName = carsState[carPassLightIndex]['arr'][curIndex]
                    streetIndex = streetToIndex[streetName]
                    timeToDrive = intersetionTable[streetIndex['start']][streetIndex['end']]['timeToDrive']
                    if carsState[carPassLightIndex]['curIndex'] + 1 == len(carsState[carPassLightIndex]['arr']) and carsState[carPassLightIndex]['onRoadSecond'] == timeToDrive:
                        carsState[carPassLightIndex]['state'] = 'end'
                    if carPassLightIndex == debugcar:
                        print('car ' + str(carPassLightIndex) + ' pass ' + street )
                else:
                    for streetIndex in range(0, len(intersetionLight[end])):
                        if intersetionLight[end][streetIndex] == street:
                            break;
                    if steetToGreenIndex not in AreadyHashIndex[end] and street not in areadyHashStreet[end]:
                        tmp = intersetionLight[end][steetToGreenIndex]
                        intersetionLight[end][steetToGreenIndex] = intersetionLight[end][streetIndex]
                        intersetionLight[end][streetIndex] = tmp
                        AreadyHashIndex[end][steetToGreenIndex] = 1
                        areadyHashStreet[end][street] = 1
                    #elif steetToGreenIndex in AreadyHashIndex[end] and street not in areadyHashStreet[end]:
                    #    preIndex = streetIndex
                    #    for c in range(0, len(intersetionLight[end])):
                    #        streetIndex = (steetToGreenIndex + c)%len(intersetionLight[end])
                    #        if streetIndex not in AreadyHashIndex[end]:
                    #            tmp = intersetionLight[end][preIndex]
                    #            intersetionLight[end][preIndex] = intersetionLight[end][streetIndex]
                    #            intersetionLight[end][streetIndex] = tmp
                    #            AreadyHashIndex[end][streetIndex] = 1
                    #            areadyHashStreet[end][street] = 1
                    #            break
                                #print('swap from ' + intersetionLight[end][preIndex] + ' to ' + intersetionLight[end][streetIndex])
                    if intersetionLight[end][steetToGreenIndex] == street:
                        carPassLightIndex = streetEndQueue[street].pop(0)
                        if len(streetEndQueue[street])>0:
                            if street not in streetBlockSeconds:
                                streetBlockSeconds[street] = 0
                            streetBlockSeconds[street] = streetBlockSeconds[street] + len(streetEndQueue[street])
                        carsState[carPassLightIndex]['state'] = 'onTheRoad'
                        carsState[carPassLightIndex]['curIndex'] = carsState[carPassLightIndex]['curIndex'] + 1
                        carsState[carPassLightIndex]['onRoadSecond'] = 1
                        curIndex = carsState[carPassLightIndex]['curIndex']
                        streetName = carsState[carPassLightIndex]['arr'][curIndex]
                        streetIndex = streetToIndex[streetName]
                        timeToDrive = intersetionTable[streetIndex['start']][streetIndex['end']]['timeToDrive']
                        if carsState[carPassLightIndex]['curIndex'] + 1 == len(carsState[carPassLightIndex]['arr']) and carsState[carPassLightIndex]['onRoadSecond'] == timeToDrive:
                            carsState[carPassLightIndex]['state'] = 'end'
                        if carPassLightIndex == debugcar:
                            print('car ' + str(carPassLightIndex) + ' pass ' + street )
                    else:
                        if street not in streetBlockSeconds:
                            streetBlockSeconds[street] = 0
                        streetBlockSeconds[street] = streetBlockSeconds[street] + len(streetEndQueue[street])
            else:
                if end in alreadPop:
                    continue
                alreadPop[end] = 1
                if end not in trafficObj:
                    trafficObj[end] = []
                trafficObj[end].append({"arriveTime": i, "street": street})
                intersetionLight[end] = getArr(trafficObj[end])
                steetToGreenIndex = i%(len(intersetionLight[end]));
                if intersetionLight[end][steetToGreenIndex] == street:
                    carPassLightIndex = streetEndQueue[street].pop(0)
                    if len(streetEndQueue[street])>0:
                        if street not in streetBlockSeconds:
                            streetBlockSeconds[street] = 0
                        streetBlockSeconds[street] = streetBlockSeconds[street] + len(streetEndQueue[street])
                    carsState[carPassLightIndex]['state'] = 'onTheRoad'
                    carsState[carPassLightIndex]['curIndex'] = carsState[carPassLightIndex]['curIndex'] + 1
                    carsState[carPassLightIndex]['onRoadSecond'] = 1
                    curIndex = carsState[carPassLightIndex]['curIndex']
                    streetName = carsState[carPassLightIndex]['arr'][curIndex]
                    streetIndex = streetToIndex[streetName]
                    timeToDrive = intersetionTable[streetIndex['start']][streetIndex['end']]['timeToDrive']
                    if carsState[carPassLightIndex]['curIndex'] + 1 == len(carsState[carPassLightIndex]['arr']) and carsState[carPassLightIndex]['onRoadSecond'] == timeToDrive:
                        carsState[carPassLightIndex]['state'] = 'end'
                    if carPassLightIndex == debugcar:
                        print('car ' + str(carPassLightIndex) + ' pass ' + street )
                
        for j in range(0, cars):
            if j == debugcar:
                print('car:'+ str(j))
                print('state:' + carsState[j]['state'])
                print('curIndex: ' + str(carsState[j]['curIndex']))
                print('len:' + str(len(carsState[j]['arr'])))   
                print('onRoadSecond:' + str(carsState[j]['onRoadSecond']))
                print('timeConsume:' + str(carsState[j]['timeConsume']))
                curIndex = carsState[j]['curIndex']
                if curIndex < len(carsState[j]['arr']): 
                    streetName = carsState[j]['arr'][curIndex]
                    streetIndex = streetToIndex[streetName]
                    print('pass street ' + streetName + " need " + str(intersetionTable[streetIndex['start']][streetIndex['end']]['timeToDrive']) )
                print('roads:')
                print(carsState[j]['arr'])
def writeFile():
    f = open('submission.csv', 'w')
    lenght = len(maxIntersetionLight.keys())
    f.write(str(lenght)+'\n')
    for key in maxIntersetionLight:
        f.write(str(key)+'\n')
        streetMap = {}
        streetList = maxIntersetionLight[key]
        
        
        for street in streetList:
            if street not in streetMap:
                streetMap[street] = 0
            streetMap[street] = streetMap[street] + 1
        f.write(str(len(streetMap.keys()))+'\n')
        streetList = sorted(set(streetList),key=streetList.index)
        for street in streetList:
            if street == 'fgha-hbec':
                f.write(street + ' ' + str(2) + '\n')
            else:
                f.write(street + ' ' + str(streetMap[street]) + '\n')

#readfile('hashcode.in')
readfile('example.in')
reinit()
optimal()
calScore()
writeFile()

iniInter('submission.csv')
reinit()
simulate()  
calScore()
# %%
