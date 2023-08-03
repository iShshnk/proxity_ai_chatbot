'use strict';
let DID_API;


const RTCPeerConnection = (
  window.RTCPeerConnection ||
  window.webkitRTCPeerConnection ||
  window.mozRTCPeerConnection
).bind(window);

let peerConnection;
let streamId;
let sessionId;
let sessionClientAnswer;

let statsIntervalId;
let videoIsPlaying;
let lastBytesReceived;

const talkVideo = document.getElementById('talk-video');
talkVideo.setAttribute('playsinline', '');

(async function autoConnect() {

  // Fetch the config before executing rest of the function
  const configResponse = await fetch('/api/config');
  const config = await configResponse.json();

  if (config.key === '🤫') {
    alert('Please put your api key inside app_config.py and restart..');
    return; // End execution if API key is not set
  }

  // Assign the fetched config to DID_API
  DID_API = config;

  if (peerConnection && peerConnection.connectionState === 'connected') {
    return;
  }

  stopAllStreams();
  closePC();

  const imgResponse = await fetch("/get_img_url");
  const imgData = await imgResponse.json();
  const imgUrl = imgData.img_url;

  const sessionResponse = await fetchWithRetries(
    `${DID_API.url}/talks/streams`,
    {
      method: "POST",
      headers: {
        Authorization: `Basic ${DID_API.key}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        source_url: imgUrl,
      }),
    }
  );

  const { id: newStreamId, offer, ice_servers: iceServers, session_id: newSessionId } = await sessionResponse.json();
  streamId = newStreamId;
  sessionId = newSessionId;

  try {
    sessionClientAnswer = await createPeerConnection(offer, iceServers);
  } catch (e) {
    console.log('error during streaming setup', e);
    stopAllStreams();
    closePC();
    return;
  }

  const sdpResponse = await fetch(`${DID_API.url}/talks/streams/${streamId}/sdp`, {
    method: 'POST',
    headers: {
      Authorization: `Basic ${DID_API.key}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      answer: sessionClientAnswer,
      session_id: sessionId,
    }),
  });
})();

vidButton.onclick = async () => {
  // Set a flag in localStorage and then refresh the page
  startSession();
};

async function startSession() {
  
  const audioResponse = await fetch('/get_audio');
  const audioData = await audioResponse.json();
  const audioUrl = audioData.audio_url;
  const audio = new Audio(audioUrl);
  audio.play();
// // connectionState not supported in firefox
// if (peerConnection?.signalingState === 'stable' || peerConnection?.iceConnectionState === 'connected') {
//   const talkResponse = await fetchWithRetries(`${DID_API.url}/talks/streams/${streamId}`, {
//     method: 'POST',
//     headers: {
//       Authorization: `Basic ${DID_API.key}`,
//       'Content-Type': 'application/json',
//     },
//     body: JSON.stringify({
//       script: {
//         type: 'audio',
//         audio_url: audioUrl,
//       },
//       driver_url: 'bank://lively/',
//       config: {
//         stitch: true,
//       },
//       session_id: sessionId,
//     }),
//   });
// } else {
//   // Play the audio automatically if peerConnection is not stable or connected
//   const audio = new Audio(audioUrl);
//   audio.play();
// }
 }

function onIceGatheringStateChange() {
  console.log("ICE gathering status: " + peerConnection.iceGatheringState);
}
function onIceCandidate(event) {
  console.log('onIceCandidate', event);
  if (event.candidate) {
    const { candidate, sdpMid, sdpMLineIndex } = event.candidate;

    fetch(`${DID_API.url}/talks/streams/${streamId}/ice`, {
      method: 'POST',
      headers: {
        Authorization: `Basic ${DID_API.key}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        candidate,
        sdpMid,
        sdpMLineIndex,
        session_id: sessionId,
      }),
    });
  }
}
function onIceConnectionStateChange() {
  console.log("ICE status: " + peerConnection.iceConnectionState);
  if (peerConnection.iceConnectionState === 'failed' || peerConnection.iceConnectionState === 'closed') {
    stopAllStreams();
    closePC();
  }
}
function onConnectionStateChange() {
  // not supported in firefox
  console.log("Peer connection status: " + peerConnection.connectionState);

  if(peerConnection.connectionState === 'failed' || peerConnection.connectionState === 'disconnected') {
    location.reload(); // Reload the page if connection state is 'failed'
  }
}
function onSignalingStateChange() {
  console.log("Signaling status: " + peerConnection.signalingState);
}

function onVideoStatusChange(videoIsPlaying, stream) {
  let status;
  if (videoIsPlaying) {
    status = 'streaming';
    const remoteStream = stream;
    setVideoElement(remoteStream);
  } else {
    status = 'empty';
    playIdleVideo();
  }
  console.log("Streaming status: " + status);
}

function onTrack(event) {
  /**
   * The following code is designed to provide information about wether currently there is data
   * that's being streamed - It does so by periodically looking for changes in total stream data size
   *
   * This information in our case is used in order to show idle video while no talk is streaming.
   */

  if (!event.track) return;


  statsIntervalId = setInterval(async () => {
    const stats = await peerConnection.getStats(event.track);
    stats.forEach((report) => {
      if (report.type === 'inbound-rtp' && report.mediaType === 'video') {
        const videoStatusChanged = videoIsPlaying !== report.bytesReceived > lastBytesReceived;

        if (videoStatusChanged) {
          videoIsPlaying = report.bytesReceived > lastBytesReceived;
          onVideoStatusChange(videoIsPlaying, event.streams[0]);
        }
        lastBytesReceived = report.bytesReceived;
      }
    });
  }, 500);
}

async function createPeerConnection(offer, iceServers) {
  if (!peerConnection) {
    peerConnection = new RTCPeerConnection({ iceServers });
    peerConnection.addEventListener('icegatheringstatechange', onIceGatheringStateChange, true);
    peerConnection.addEventListener('icecandidate', onIceCandidate, true);
    peerConnection.addEventListener('iceconnectionstatechange', onIceConnectionStateChange, true);
    peerConnection.addEventListener('connectionstatechange', onConnectionStateChange, true);
    peerConnection.addEventListener('signalingstatechange', onSignalingStateChange, true);
    peerConnection.addEventListener('track', onTrack, true);
  }

  await peerConnection.setRemoteDescription(offer);
  console.log('set remote sdp OK');

  const sessionClientAnswer = await peerConnection.createAnswer();
  console.log('create local sdp OK');

  await peerConnection.setLocalDescription(sessionClientAnswer);
  console.log('set local sdp OK');

  return sessionClientAnswer;
}

function setVideoElement(stream) {
  if (!stream) return;
  talkVideo.srcObject = stream;
  talkVideo.loop = false;

  // safari hotfix
  if (talkVideo.paused) {
    talkVideo
      .play()
      .then((_) => {})
      .catch((e) => {});
  }
}

function playIdleVideo() {
    talkVideo.srcObject = undefined;
    talkVideo.src = '/idle.mp4';
    talkVideo.loop = true;
  }

function stopAllStreams() {
  if (talkVideo.srcObject) {
    console.log('stopping video streams');
    talkVideo.srcObject.getTracks().forEach((track) => track.stop());
    talkVideo.srcObject = null;
  }
}

function closePC(pc = peerConnection) {
  if (!pc) return;
  console.log('stopping peer connection');
  pc.close();
  pc.removeEventListener('icegatheringstatechange', onIceGatheringStateChange, true);
  pc.removeEventListener('icecandidate', onIceCandidate, true);
  pc.removeEventListener('iceconnectionstatechange', onIceConnectionStateChange, true);
  pc.removeEventListener('connectionstatechange', onConnectionStateChange, true);
  pc.removeEventListener('signalingstatechange', onSignalingStateChange, true);
  pc.removeEventListener('track', onTrack, true);
  clearInterval(statsIntervalId);
  console.log('stopped peer connection');
  if (pc === peerConnection) {
    peerConnection = null;
  }
}

const maxRetryCount = 3;
const maxDelaySec = 4;

async function fetchWithRetries(url, options, retries = 1) {
  try {
    return await fetch(url, options);
  } catch (err) {
    if (retries <= maxRetryCount) {
      const delay = Math.min(Math.pow(2, retries) / 4 + Math.random(), maxDelaySec) * 1000;

      await new Promise((resolve) => setTimeout(resolve, delay));

      console.log(`Request failed, retrying ${retries}/${maxRetryCount}. Error ${err}`);
      return fetchWithRetries(url, options, retries + 1);
    } else {
      throw new Error(`Max retries exceeded. error: ${err}`);
    }
  }
}