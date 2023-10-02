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

def get_average_vmaf_mos_values(resolution, path):
    values = [0, 15, 30, 45]
    average_vmaf_mos_values = []
    fps = 24

    for value in values:
        f = f"{resolution}_{value}"
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

    return values, average_vmaf_mos_values

path = "/home/ohzahata-qoe/Documents/GitHub/elastest-webrtc-qoe-meter/score/"

# 480pのデータを取得
values_480, average_vmaf_mos_values_480 = get_average_vmaf_mos_values("480_640", path + "480_640/0916/average/")

# 720pのデータを取得 (パスと解像度を適切に変更してください)
values_720, average_vmaf_mos_values_720 = get_average_vmaf_mos_values("720_1280", path + "720_1280/0918/average/")

# プロット
plt.plot(values_480, average_vmaf_mos_values_480, marker='o', label='480p')
plt.plot(values_720, average_vmaf_mos_values_720, marker='x', label='720p')
plt.xlabel('Packet Loss(%)')
plt.ylabel('MOS Score from VMAF')
plt.title('MOS Score vs Packet Loss')
plt.legend()
plt.grid(True)
plt.savefig(path + "vmaf_graph/average_vmaf_mos_combined.png")
#plt.show()
