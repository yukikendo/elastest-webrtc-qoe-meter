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


path = "/home/ohzahata-qoe/Documents/GitHub/elastest-webrtc-qoe-meter/score/480_640/"
f = "480_640_1"

# ファイル読み込み
source = path + f + '.json'
print(f'file : {source}')
with open(source, 'r') as file:
    data = json.load(file)

# 設定と初期化
fps = 24
vmaf_scores = []
vmaf_mos = []
vmaf = 0
count = 0
seconds = 30

# VMAFをMOS値に変換し、1秒ごとに平均を取る
for frame in data['frames']:
    vmaf += frame['VMAF_score']
    # vmaf += MOS_form_VMAF(fps, frame['VMAF_score']) 
    count = count + 1
    if(count == fps):
        vmaf_mos.append( 1 + 4*((vmaf/fps) / 100))
        #mean = vmaf / fps
        #vmaf_mos.append(mean)
        vmaf = 0
        count = 0

average_vmaf_mos = sum(vmaf_mos) / len(vmaf_mos)
print("Average VMAF MOS:", average_vmaf_mos)

print(len(vmaf_mos))
plt.plot(vmaf_mos)
ax = plt.gca()
ticks = list(range(seconds))  # 0から30までの整数のリスト
labels = [f"{i+1}" for i in range(seconds)]
ax.set_xticks(ticks)
ax.set_xticklabels(labels)
ax.tick_params(axis='x', labelsize=8)
plt.ylim(0,5)
plt.xlabel('Time(second)')
plt.ylabel('MOS_from_VMAF per second')
plt.title('MOS score from VMAF')
plt.savefig(path+"vmaf_graph/"+f+".png")
#plt.show()