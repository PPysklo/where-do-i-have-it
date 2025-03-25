const socket = new WebSocket(`ws://${window.location.host}/ws/scanner/`);

const find_container = document.getElementById('find-container');
const to_delete = document.getElementById('deletethis');

const play_btn = document.getElementById('play_btn');
const controls = document.querySelector('.controls');
const cameraOptions = document.querySelector('.video-options>select');
const video = document.querySelector('video');
const canvas = document.querySelector('canvas');
const buttons = [...controls.querySelectorAll('button')];
let streamStarted = false;
let currentStream = null;

const [play] = buttons;

// Assign the video element to window.localVideo
window.localVideo = video;

function getLocalStream() {
  navigator.mediaDevices
    .getUserMedia({ video: { facingMode: "environment" }, audio: false })
    .then((stream) => {
      window.localStream = stream;
      window.localVideo.srcObject = stream;
      window.localVideo.autoplay = true;
    })
    .catch((err) => {
      console.error(`Wystąpił błąd: ${err}`);
    });
}
getLocalStream();

const constraints = {
  video: {
    width: {
      ideal: 1920,
      max: 2560,
    },
    height: {
      ideal: 1080,
      max: 1440
    }
  }
};

const getCameraSelection = async () => {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const videoDevices = devices.filter(device => device.kind === 'videoinput');
    const options = videoDevices.map(videoDevice => {
        return `<option value="${videoDevice.deviceId}">${videoDevice.label}</option>`;
    });
    cameraOptions.innerHTML = options.join('');
};

play.onclick = () => {
    if (streamStarted) {
        video.play();
        play.classList.add('d-none');
        return;
    }
    if ('mediaDevices' in navigator && navigator.mediaDevices.getUserMedia) {
        const updatedConstraints = {
            ...constraints,
            video: {
                ...constraints.video,
                deviceId: {
                    exact: cameraOptions.value
                }
            }
        };
        startStream(updatedConstraints);
    }
};

const startStream = async (constraints) => {
    if (currentStream) {
        currentStream.getTracks().forEach(track => track.stop());
    }
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    handleStream(stream);
};

getCameraSelection();

cameraOptions.onchange = () => {
    const updatedConstraints = {
        ...constraints,
        video: {
            ...constraints.video,
            deviceId: {
                exact: cameraOptions.value
            }
        }
    };
    startStream(updatedConstraints);
};

const handleStream = (stream) => {
    video.srcObject = stream;
    play.classList.add('d-none');
    streamStarted = true;

    video.addEventListener('play', function() {
        setInterval(function() {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            const screenshotDataURL = canvas.toDataURL('image/webp');

            canvas.toBlob(function(blob) {
                socket.send(blob);
            }, 'image/jpeg');
        }, 500);
    });
};

socket.onmessage = function(event) {
    var data = JSON.parse(event.data);
    var thing_name = data.found_thing;
    var thing_id = data.thing_id;
    var thing_description = data.thing_description;
    var msg = data.message;

    if (msg){
        find_container.innerHTML = `<h3>${msg}</h3>`;
    }
    else if (typeof thing_name != 'undefined') {
        find_container.innerHTML = '<h1>Found thing:</h1>'

        find_container.innerHTML += `<h3>Name: ${thing_name}</h3></br>`;
        find_container.innerHTML += `<h3>Id: ${thing_id}</h3> </br><h3>Description: ${thing_description}</h3>`;
    }
};


