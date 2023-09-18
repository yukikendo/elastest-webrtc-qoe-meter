/*
 * (C) Copyright 2017-2019 ElasTest (http://elastest.io/)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 */
function ElasTestRemoteControl() {
	this.recordRTC = null;
}

ElasTestRemoteControl.prototype.startRecording = function(stream) {
	var options = {
		type : "video",
		mimeType : "video/webm",
		// frameRate : 60,
		// bitsPerSecond: 9000000,
		numberOfAudioChannels : 2,
		sampleRate : 48000,
	};
	this.recordRTC = RecordRTC(stream, options);
	this.recordRTC.startRecording();
}

ElasTestRemoteControl.prototype.stopRecording = function () {
	if (!this.recordRTC) {
		console.warn("No recording found.");
	} else {
		if (this.recordRTC.length) {
			this.recordRTC[0].stopRecording(function (url) {
				if (!this.recordRTC[1]) {
					console.info("[0] Recorded track: " + url);
					return;
				}
				this.recordRTC[1].stopRecording(function (url) {
					console.info("[1] Recorded track: " + url);
				});
			});
		} else {
			this.recordRTC.stopRecording(function (url) {
				console.info("Recorded track: " + url);
			});
		}
	}
}

ElasTestRemoteControl.prototype.saveRecordingToDisk = function (fileName) {
	if (!this.recordRTC) {
		console.warn("No recording found.");
	} else {
		var output = this.recordRTC.save(fileName);
		console.info(output);
	}
}

ElasTestRemoteControl.prototype.openRecordingInNewTab = function () {
	if (!this.recordRTC) {
		console.warn("No recording found.");
	} else {
		window.open(this.recordRTC.toURL());
	}
}

ElasTestRemoteControl.prototype.recordingToData = function () {
	var self = this;
	if (!self.recordRTC) {
		console.warn("No recording found.");
	} else {
		var blob = self.recordRTC.getBlob();
		var reader = new window.FileReader();
		reader.readAsDataURL(blob);
		reader.onloadend = function () {
			self.recordingData = reader.result;
		}
	}
}

ElasTestRemoteControl.prototype.getStats = function (name) {
	var stats_report = {}
	var num = 0;
	if (!peerConnections) {
		console.warn("No peerConnections found.");
	} else {
		console.info("peerConnections found");
		const timer = setInterval(() => {
			let stats_all = {}
			// producerが動画本体を流している間の統計
			if (num >= 5 && num <= 35) {
				peerConnections[0].getStats(null).then((stats) => {
					stats.forEach((report) => {
						let type = report.type;
						stats_all[type] = report;
					})
				})
				stats_report[++num] = stats_all;
				console.info(stats_report)
				if (num == 21) {
					//download json
					clearInterval(timer);
					console.info("num = " + num);
					const filename = "stats_"+name+".json";
					const data = JSON.stringify(stats_report, null, "\t");
					const link = document.createElement("a");
					link.href = "data:," + encodeURIComponent(data);
					link.download = filename;
					link.click();
					//このあとはjava側でファイルのリネームと移動をやる
				}
			} else {
				++num;
			}
		}, 1000);
		console.info("finish");
	}
}

/*
 * Monkey Patching (override RTCPeerConnection)
 */
var peerConnections = [];
var origPeerConnection = window.RTCPeerConnection;
window.RTCPeerConnection = function (pcConfig, pcConstraints) {
	var pc = new origPeerConnection(pcConfig, pcConstraints);
	peerConnections.push(pc);
	return pc;
}
window.RTCPeerConnection.prototype = origPeerConnection.prototype;

/*
 * Instantiation of ElasTestRemoteControl object
 */
var elasTestRemoteControl = new ElasTestRemoteControl();