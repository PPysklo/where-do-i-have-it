const socket = new WebSocket(`ws://${window.location.host}/ws/image_reco/`);

const img_cont = document.getElementsByClassName('smaller-display-cover-img-reco');
const controls = document.querySelector('.controls');
const cameraOptions = document.querySelector('.video-options>select');
const video = document.querySelector('video');
const buttons = [...controls.querySelectorAll('button')];
let streamStarted = false;
let currentStream = null;


const [play] = buttons;

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
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const context = canvas.getContext('2d');
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            canvas.toBlob(function(blob) {
                socket.send(blob);
            }, 'image/jpeg');
        }, 1000);
    });
};

    socket.onmessage = function(event) {
        var imageData = event.data;
//        imageData = imageData.slice(0, imageData.size, 'image/jpeg')
//        console.log(imageData);
        if (imageData) {
            var img = document.getElementById('img');
//            var urlObject = URL.createObjectURL(imageData);
            img.src = "data:image/png;base64," + imageData;
            img.style.display = 'block';
            }else {
            alert('Failed to upload image');
        };
};

socket.onopen = function open() {
   socket.send(id);
};