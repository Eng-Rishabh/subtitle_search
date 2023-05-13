console.log('In main.js!');

var mapPeers = {};

//var labelUsername = document.querySelector('#label-username');
var usernameInput = document.querySelector('#username');
var btnJoin = document.querySelector('#btn-join');

var username;

let myoffer;
let youroffer;

function webSocketOnMessage(event) {
    var parsedData = JSON.parse(event.data);
    myoffer = parsedData
    var peerUserName = parsedData['peer'];
    var action = parsedData['action'];

    if (username == peerUserName) {
        return;
    }

    var receiver_channel_name = parsedData['message']['receiver_channel_name'];

    if (action == 'new-peer') {
        createofferer(peerUserName, receiver_channel_name);
        return;
    }

    if (action == 'new-offer') {
        var offer = parsedData['message']['sdp']

        createAnswer(offer, peerUserName, receiver_channel_name);
    }

    if (action == 'new-answer') {
        var answer = parsedData['message']['sdp'];

        var peer = mapPeers[peerUserName][0];
        peer.setLocalDescription(answer);

        return;
    }
}

btnJoin.addEventListener('click', () => {
    username = usernameInput.value;

    if (username == '') {
        return;
    }

    usernameInput.value = '';
    usernameInput.disabled = true;
    usernameInput.style.visibility = 'hidden';

    btnJoin.disabled = true;
    btnJoin.style.visibility = 'hidden';

    var labelUsername = document.querySelector('#label-username');
    labelUsername.innerHTML = username;

    var loc = window.location;
    var wsStart = 'ws://';

    if (loc.protocol == 'https:') {
        wsStart = 'wss://';
    }

    var endPoint = wsStart + loc.host + loc.pathname;

    webSocket = new WebSocket(endPoint);
    webSocket.addEventListener('open', (e) => {
        console.log('Connection Opened');
        sendSignal('new-peer', {});
    });

    webSocket.addEventListener('message', webSocketOnMessage);
    webSocket.addEventListener('close', (e) => {
        console.log('Connection Closed');
    });

    webSocket.addEventListener('error', (e) => {
        console.log('Error Occurred');
    });
});



var localStream = new MediaStream();

const constraints = {
    'video': true,
    'audio': true
};

const localVideo = document.querySelector('#local-video');
const btnToggleAudio = document.querySelector('#btn-toggle-audio');
const btnToggleVideo = document.getElementById('btn-toggle-video');



var userMedia = navigator.mediaDevices.getUserMedia(constraints)
    .then(stream => {
        localStream = stream;
        localVideo.srcObject = localStream;
        localVideo.muted = true;

        var audioTracks = stream.getAudioTracks();
        var videoTracks = stream.getVideoTracks();

        audioTracks[0].enabled = true;
        videoTracks[0].enabled = true;

        btnToggleAudio.addEventListener('click', () => {
            audioTracks[0].enabled = !audioTracks[0].enabled;

            if (audioTracks[0].enabled) {
                btnToggleAudio.innerHTML = 'Audio Mute';

                return;
            }
            btnToggleAudio.innerHTML = 'Audio Unmute';
        });

        btnToggleVideo.addEventListener('click', () => {
            videoTracks[0].enabled = !videoTracks[0].enabled;

            if (videoTracks[0].enabled) {
                btnToggleVideo.innerHTML = 'Video off';

                return;
            }
            btnToggleVideo.innerHTML = 'Video On';
        });
    })
    .catch(error => {
        console.log('Error accessing media devices.', error);
    })

var btnSendMsg = document.querySelector('#btn-send-msg');
var messageList = [...document.querySelectorAll('#message-list')];
var MessageInput = document.querySelector('#msg');

btnSendMsg.addEventListener('click', sendMsgOnClick);

function sendMsgOnClick() {
    var message = MessageInput;

    var li = document.createElement('li');
    li.innerHTML = `Me: ${message}`;

    messageList.push(li);

    var datachannels = getDataChannels();

    message = username + ': ' + message;

    for (index in dataChannels) {
        datachannels[index].send(message);
    }

    MessageInput.value = '';
}

function sendSignal(action, message) {
    var jsonStr = JSON.stringify({
        'peer': username,
        'action': action,
        'message': message,
    });
    webSocket.send(jsonStr);
}

function createofferer(peerUserName, receiver_channel_name) {
    var peer = new RTCPeerConnection(null);

    addLocalTracks(peer);

    var dc = peer.createDataChannel('channel');
    dc.addEventListener('open', () => {
        console.log('Connection Opened!');
    });

    dc.addEventListener('message', dcOnMessage);

    var remoteVideo = createVideo(peerUserName);
    setOnTrack(peer, remoteVideo);

    mapPeers[peerUserName] = [peer, dc];

    peer.addEventListener('iceconnectionstatechange', () => {
        var iceconnectionstatechange = peer.iceConnectionsState;
        if (iceconnectionstatechange === 'failed' || iceconnectionstatechange === 'disconnected' || iceconnectionstatechange === 'closed') {
            delete mapPeers[peerUserName];

            if (iceConnectionsState != 'closed') {
                peer.close();
            }

            removeVideo(remoteVideo);
        }
    });

    peer.addEventListener('icecandidate', (event) => {
        console.log('New ice candidate: ', JSON.stringify(peer.localDescription));

        return;
    })

    sendSignal('new-offer', {
        'sdp': peer.localDescription,
        'receiver_channel_name': receiver_channel_name
    });

    peer.createOffer()
        .then(o => peer.setLocalDescription(o))

        .then(() => {
            console.log("Local Descriptor set successfully.");
        });
}

function createAnswer(offer, peerUserName, receiver_channel_name) {
    var peer = new RTCPeerConnection(null);

    addLocalTracks(peer);

    var remoteVideo = createVideo(peerUserName);
    setOnTrack(peer, remoteVideo);

    peer.addEventListener('datachannel', e => {
        peer.dc = e.channel;
        peer.dc.addEventListener('open', () => {
            console.log('Connection Opened!');
        });
        peer.dc.addEventListener('message', dcOnMessage);

        mapPeers[peerUserName] = [peer, peer.dc];
    });

    peer.addEventListener('iceconnectionstatechange', () => {
        var iceconnectionstatechange = peer.iceConnectionsState;
        if (iceconnectionstatechange === 'failed' || iceconnectionstatechange === 'disconnected' || iceconnectionstatechange === 'closed') {
            delete mapPeers[peerUserName];

            if (iceConnectionsState != 'closed') {
                peer.close();
            }

            removeVideo(remoteVideo);
        }
    });

    peer.addEventListener('icecandidate', (event) => {
        if (event.candidate) {
            console.log('New ice candidate: ', JSON.stringify(peer.localDescription));
            return;
        }

        sendSignal('new-answer', {
            'sdp': peer.localDescription,
            'receiver_channel_name': receiver_channel_name
        })
    });

    peer.setRemoteDescription(offer)
        .then(() => {
            console.log('Remote description set successfully for %s', peerUserName);

            return peer.createAnswer();

        })
        .then(a => {
            console.log("answer");
            peer.setLocalDescription(a);
        })

}


function addLocalTracks(peer) {
    localStream.getTracks().forEach(track => {
        peer.addTrack(track, localStream);
    })

    return;
}

function dcOnMessage(event) {
    var message = event.data;

    var li = document.createElement('li');
    li.appendChild(document.createTextNode(message));
    messageList.appendChild(li);
}

function createVideo(peerUserName) {
    var videoContainer = document.querySelector('.video-container');

    var remoteVideo = document.createElement('video');

    remoteVideo.id = peerUserName + '-video';
    remoteVideo.autoplay = true;
    remoteVideo.playsInline = true;

    var videoWrapper = document.createElement('div');

    videoContainer.appendChild(videoWrapper);

    videoWrapper.appendChild(remoteVideo);

    return remoteVideo;
}

function setOnTrack(peer, remoteVideo) {
    var remoteStream = new MediaStream();

    remoteVideo.srcObject = remoteStream;

    peer.addEventListener('track', async (event) => {
        remoteStream.addTrack(even.track, remoteStream);
    })
}

function removeVideo(video) {
    var videoWrapper = video.parentNode;

    videoWrapper.parentNode.removeChild(videoWrapper);
}

function getDataChannels() {
    var datachannel = [];

    for (peerUserName in mapPeers) {
        var datachannel = mapPeers[peerUserName][1];

        datachannel.push(datachannel);
    }

    return datachannels;
}