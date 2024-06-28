# ip_camera_stream_recoder

This is a python based project created for recording ip_camera streams into computer hard disk

# Developer instructions

### Install dependancies

pip install -r .\requirements.txt -U pip --user //In Windows
pip install -r .\requirements.txt -U pip --user //Linux, and MacOS

### Command Line Arguments

- LogLevel setup

  - short-hand: -ll
  - regular: --logLevel
  - Available Options: INFO, DEBUG, WARNING

- IP Camera URLs

  - short-hand: -cu
  - regular: --cameraURLs
  - Format: "rtsp://username:XXXXXX@<local-ip-address-of-the-ip-camera>:554"

- Stream Recording Path Config

  - short-hand: -rp
  - regular: --recordingPath
  - Format: <follow operating system specific path formats>
