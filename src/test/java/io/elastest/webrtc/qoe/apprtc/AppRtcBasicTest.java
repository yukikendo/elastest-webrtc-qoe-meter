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
package io.elastest.webrtc.qoe.apprtc;

import static java.lang.invoke.MethodHandles.lookup;
import static java.util.UUID.randomUUID;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.slf4j.LoggerFactory.getLogger;

import java.io.File;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.openqa.selenium.By;
import org.openqa.selenium.JavascriptExecutor;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.slf4j.Logger;

import io.elastest.webrtc.qoe.ElasTestRemoteControlParent;
import io.github.bonigarcia.seljup.Arguments;
import io.github.bonigarcia.seljup.SeleniumExtension;
import io.github.bonigarcia.wdm.WebDriverManager;

import java.util.ArrayList;

@ExtendWith(SeleniumExtension.class)
public class AppRtcBasicTest extends ElasTestRemoteControlParent {

    final Logger log = getLogger(lookup().lookupClass());

    public static final String FAKE_VIDEO = "--use-file-for-fake-video-capture=/home/ohzahata-qoe/Documents/GitHub/elastest-webrtc-qoe-meter/test.y4m"; //自分の環境に合わせて変える
    public static final String FAKE_AUDIO = "--use-file-for-fake-audio-capture=/home/ohzahata-qoe/Documents/GitHub/elastest-webrtc-qoe-meter/test.wav";

    static final String SUT_URL = "https://localhost/?wshpp=localhost:8089&wstls=true";

    static final int TEST_TIME_SEC = 40; //動画の長さとパディング2つの長さの合計
    static final String SESSION_NAME = randomUUID().toString(); 

    //network config
    String loss = "40%";
    String rate = "1Mbps";
    String jitter = "";
    //encode bitrate
    String bitrate = "9000000";

    String[] file_string = FAKE_VIDEO.split("/");
    String file_name = file_string[file_string.length - 1].substring(0,file_string[file_string.length - 1].lastIndexOf(".")) + "-" + loss + "-" + rate; //+ "-" + rate + "-" + jitter;
    String stream = "interview";
    String framerate = "24fps";
    String resolution = "480p";
    String dst_dir = resolution + "/" + framerate;
    String stats_file = stream;

    ChromeDriver presenter;
    ChromeDriver viewer;

    public AppRtcBasicTest(
            @Arguments({ FAKE_DEVICE, FAKE_UI, FAKE_VIDEO, FAKE_AUDIO, IGNORE_CERTIFICATE,DISABLE_SMOOTHNESS}) ChromeDriver presenter,
            @Arguments({ FAKE_DEVICE, FAKE_UI, IGNORE_CERTIFICATE, DISABLE_SMOOTHNESS }) ChromeDriver viewer) {
        super(SUT_URL, presenter, viewer);
        this.presenter = presenter;
        this.viewer = viewer;
    }

    @Test
    void appRtcTest() throws Exception {
        // Presenter
        clearAndSendKeysToElementById(presenter, "room-id-input", SESSION_NAME);
        presenter.findElement(By.id("join-button")).click();

        // Viewer
        clearAndSendKeysToElementById(viewer, "room-id-input", SESSION_NAME);
        viewer.findElement(By.id("join-button")).click();

        // 統計情報の収集
        getStats(presenter,"presenter");
        getStats(viewer,"viewer");
        
        // presenter側で統計情報を見る用
        executeScript(presenter,"window.open()");
        ArrayList<String> tabs = new ArrayList<String>(presenter.getWindowHandles());
        presenter.switchTo().window(tabs.get(1));
        presenter.get("chrome://webrtc-internals");
        presenter.switchTo().window(tabs.get(0));

        // Recordings
        startRecording(presenter, "peerConnections[0].getLocalStreams()[0]");
        startRecording(viewer, "peerConnections[0].getRemoteStreams()[0]");

        // tc用の受信側ポートの取得
        JavascriptExecutor jsExecutor = (JavascriptExecutor) presenter;
        String script = "const pc = window.peerConnections[0];" +
                        "const stats = await pc.getStats();" +
                        "var port;" +
                        "stats.forEach((report) => { if (report.type === 'remote-candidate') { port = report.port } });" +
                        "return port;" ;
        int port = (int)(long)jsExecutor.executeScript(script);
        log.debug("port {}",port);


        //setting network 
        //Runtime.getRuntime().exec("sudo tcset lo --direction incoming --port " + port + " --loss " + loss + " --rate " + rate);// 
        //log.debug("sudo tcset lo --direction incoming --port " + port + " --loss " + loss  + " --rate " + rate);// 
        Runtime.getRuntime().exec("sudo tcset lo --direction incoming --port " + port + " --loss " + loss);
        log.debug("sudo tcset lo --direction incoming --port " + port + " --loss " + loss);


        // Call time
        log.debug("WebRTC call ({} seconds)", TEST_TIME_SEC);
        waitSeconds(TEST_TIME_SEC);

        //remove network setting
        Runtime.getRuntime().exec("sudo tcdel lo --all");
        log.debug("sudo tcdel lo --all");

        // Stop and get recordings
        stopRecording(presenter);
        stopRecording(viewer);

        String presenterRecordingName = "test-presenter.webm";
        File recordingPresenter = getRecording(viewer, presenterRecordingName);
        assertTrue(recordingPresenter.exists());

        String viewerRecordingName = "test-viewer.webm";
        File recordingViewer = getRecording(viewer, viewerRecordingName);
        assertTrue(recordingViewer.exists());

        // 以下、ファイル名をいじって保存する用
        //String presenterRecordingName = "./media/record/" + file_name + "-presenter.webm";
        //File recordingPresenter = getRecording(presenter, presenterRecordingName);
        //assertTrue(recordingPresenter.exists());
        //String viewerRecordingName = "./media/record/" + file_name + "-viewer.webm";
        //File recordingViewer = getRecording(viewer, viewerRecordingName);
        //assertTrue(recordingViewer.exists())
        //if (!loss.isEmpty()) {
        //    stats_file += "_" + loss;
        //}
        //if (!rate.isEmpty()) {
        //    stats_file += "_" + rate;
        //}
        //if (!jitter.isEmpty()) {
        //    stats_file += "_" + jitter;
        //}

        // デフォルトで統計がダウンロードされるディレクトリを指定できないので、名前を変更しつつ移動
        moveStatsFile("stats_presenter", dst_dir, stats_file,"_presenter");
        moveStatsFile("stats_viewer", dst_dir , stats_file, "_viewer");

    }

}