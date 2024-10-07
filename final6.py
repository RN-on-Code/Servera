<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rubik's Cube Face Capture</title>
    <style>
        body {
            text-align: center;
        }

        #cameraFeed {
            display: none;
            border: 2px solid #333;
        }

        #cubeCanvas {
            border: 2px solid #333;
        }

        #previewCanvas {
            border: 2px solid #333;
        }

        #captureBtn {
            margin-top: 10px;
            padding: 5px 10px;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <video id="cameraFeed" width="300" height="300"></video>
    <canvas id="cubeCanvas" width="300" height="300"></canvas>
    <canvas id="previewCanvas" width="300" height="300"></canvas>
    <button id="captureBtn" onclick="startCamera()">Start Camera</button>

    <script async src="https://docs.opencv.org/master/opencv.js" onload="onOpenCvReady();" type="text/javascript"></script>
    <script>
        let video, cubeCanvas, cubeCtx, previewCanvas, previewCtx, capturing;

        async function startCamera() {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ video: true });
                video.srcObject = stream;

                // Load OpenCV.js
                await new Promise((resolve) => {
                    window.onOpenCvReady = () => {
                        video.play();
                        capturing = true;
                        requestAnimationFrame(captureFrame);
                        resolve();
                    };
                });
            } catch (error) {
                console.error('Error accessing camera:', error);
            }
        }

        function captureFrame() {
            if (capturing) {
                const src = new cv.Mat(video.height, video.width, cv.CV_8UC4);
                const dst = new cv.Mat(video.height, video.width, cv.CV_8UC4);
                const cap = new cv.VideoCapture(video);

                cap.read(src);
                cv.imshow('cubeCanvas', src);

                // Further processing logic (e.g., adjusting the cube within boxes)
                // You may need to add more advanced computer vision logic here

                src.delete();
                dst.delete();

                requestAnimationFrame(captureFrame);
            }
        }

        function captureFace() {
            capturing = true;

            // Stop capturing after a short delay (adjust as needed)
            setTimeout(() => {
                capturing = false;
            }, 1000);
        }

        function stopCamera() {
            const stream = video.srcObject;
            const tracks = stream.getTracks();

            tracks.forEach((track) => {
                track.stop();
            });

            video.srcObject = null;
        }

        // Start the camera when the page loads
        document.addEventListener('DOMContentLoaded', () => {
            video = document.getElementById('cameraFeed');
            cubeCanvas = document.getElementById('cubeCanvas');
            cubeCtx = cubeCanvas.getContext('2d');
            previewCanvas = document.getElementById('previewCanvas');
            previewCtx = previewCanvas.getContext('2d');
        });
    </script>
</body>
</html>
