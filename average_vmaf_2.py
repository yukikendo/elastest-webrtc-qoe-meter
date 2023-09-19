import json
import matplotlib.pyplot as plt

path = "/home/ohzahata-qoe/Documents/GitHub/elastest-webrtc-qoe-meter/score/480_640/0916/average/"
values = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45]
vmaf_scores_values = []

for value in values:
    f = f"480_640_{value}"
    source = path + f + '.json'
    print(f'file : {source}')
    with open(source, 'r') as file:
        data = json.load(file)

    vmaf_score = data['aggregate']['VMAF_score']
    vmaf_scores_values.append(vmaf_score)
    print("VMAF Score:", vmaf_score)

# プロット
plt.plot(values, vmaf_scores_values, marker='o')
plt.xlabel('Packet Loss(%)')
plt.ylabel('VMAF Score')
plt.title('VMAF Score vs Packet Loss')
plt.grid(True)
plt.yticks([0, 10, 20, 30, 40, 50, 60, 70])  # これを追加
plt.xticks([0, 5, 10, 15, 20, 25, 30, 35, 40, 45])
plt.savefig(path + "vmaf_graph/vmaf_scores_2.png")
plt.show()
