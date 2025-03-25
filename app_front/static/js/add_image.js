
const socket = new WebSocket(`ws://${window.location.host}/ws/add_image/`);

const find_container = document.getElementById('find-container');
const to_delete = document.getElementById('deletethis');

const play_btn = document.getElementById('play_btn');
const controls = document.querySelector('.controls');
const cameraOptions = document.querySelector('.video-options>select');
const video = document.querySelector('video');
const canvas = document.querySelector('canvas');
const screenshotImage = document.querySelector('img');
const buttons = [...controls.querySelectorAll('button')];
let streamStarted = false;

const [play, screenshot] = buttons;
let currentStream = null;



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




const doScreenshot = () => {
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  const screenshotDataURL = canvas.toDataURL('image/webp');
};


screenshot.onclick = doScreenshot;



const handleStream = (stream) => {
    video.srcObject = stream;
    play.classList.add('d-none');
    screenshot.classList.remove('d-none');
    streamStarted = true;

    play_btn.addEventListener('click', function() {
        canvas.toBlob(function(blob) {

            socket.send(blob);
        }, 'image/jpeg');
    });
};


socket.onopen = function open() {
   socket.send(id);
};

socket.onmessage = function(event) {
        var data = JSON.parse(event.data);
        var message = data.message;
        var image_data = data.image;
        console.log(message);
        if (data) {
            if(message != ""){
                swal(message);
            }

            var img = document.createElement('img');
            img.setAttribute("class","img-fluid rounded existed-img");
            img.src = "data:image/png;base64," + image_data;
            if(to_delete){
                to_delete.remove();
                };
            find_container.appendChild(img);
        } else {
            alert('Failed to upload image');
        }
    };


