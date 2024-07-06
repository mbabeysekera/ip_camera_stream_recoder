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

- IP Camera Base URLs

  - short-hand: -cu
  - regular: --cameraURLs
  - Format: "rtsp://username:XXXXXX@<local-ip-address-of-the-ip-camera>:554"

- Camera Main Stream and Sub Streams

  - short-hand: -ms
  - regular: --mainStream
  - Format: "/Streaming/Channels/101" (Please refer your camera model for specifics)

  - short-hand: -ss
  - regular: --subStream
  - Format: "/Streaming/Channels/102" (Please refer your camera model for specifics)

- Stream Recording Path Config

  - short-hand: -rp
  - regular: --recordingPath
  - Format: <follow operating system specific path formats>

- Device Names corresponding to each camera

  - short-hand: -dn
  - regular: --deviceName
  - Format: "ANY_NAME" (type: String)
