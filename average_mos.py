import json
import matplotlib.pyplot as plt

def MOS_form_VMAF(fps, score):
    coefficients = {
        60:{
            "a":0.6576,
            "b":0.02944,
            "c":0.0001419
        },
        30:{
            "a":0.9265,
            "b":0.01552,
            "c":0.0002275
        },
        15:{
            "a":1.256,
            "b":0.0006649,
            "c":0.0002285
        }
    }
    a = coefficients[fps]["a"]
    b = coefficients[fps]["b"]
    c = coefficients[fps]["c"]

    mos = a + b*score + c*pow(score,2)
    
    return mos

path = "/home/ohzahata-qoe/Documents/GitHub/elastest-webrtc-qoe-meter/score/480_640/0914/"
values = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]
average_vmaf_mos_values = []

fps = 24

for value in values:
    f = f"480_640_{value}"
    source = path + f + '.json'
    print(f'file : {source}')
    with open(source, 'r') as file:
        data = json.load(file)

    vmaf_scores = []
    vmaf_mos = []
    vmaf = 0
    count = 0
    seconds = 30

    for frame in data['frames']:
        vmaf += frame['VMAF_score']
        count = count + 1
        if(count == fps):
            vmaf_mos.append(1 + 4*((vmaf/fps) / 100))
            vmaf = 0
            count = 0

    average_vmaf_mos = sum(vmaf_mos) / len(vmaf_mos)
    average_vmaf_mos_values.append(average_vmaf_mos)
    print("Average VMAF MOS:", average_vmaf_mos)

# プロット
plt.plot(values, average_vmaf_mos_values, marker='o')
plt.xlabel('Packet Loss(%)')
plt.ylabel('average MOS from VMAF')
plt.title('MOS Score vs Packet Loss')
plt.grid(True)
plt.savefig(path + "vmaf_graph/average_vmaf_mos.png")
#plt.show()
