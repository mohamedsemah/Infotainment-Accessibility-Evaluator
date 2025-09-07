import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

// ISSUE: No accessibility properties defined
ApplicationWindow {
    id: mainWindow
    width: 800
    height: 480
    visible: true
    title: "Car Media Player"
    
    // ISSUE: No color scheme for high contrast mode
    color: "#f0f0f0"
    
    // ISSUE: No focus management
    property bool isPlaying: false
    property int currentVolume: 50
    property string currentTrack: "Sample Track"
    property string currentArtist: "Sample Artist"
    
    // ISSUE: No ARIA live regions
    Rectangle {
        id: mainContainer
        anchors.fill: parent
        color: "#ffffff"
        
        // ISSUE: No heading structure
        Text {
            id: titleText
            text: "Media Player"
            font.pixelSize: 24
            color: "#888888" // ISSUE: Low contrast
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.margins: 20
        }
        
        // ISSUE: No labels for controls
        Row {
            id: controlRow
            anchors.top: titleText.bottom
            anchors.left: parent.left
            anchors.margins: 20
            spacing: 10
            
            Button {
                id: playButton
                text: isPlaying ? "⏸" : "▶"
                width: 60
                height: 60
                // ISSUE: No accessible name
                onClicked: {
                    isPlaying = !isPlaying
                    // ISSUE: No state announcement
                }
            }
            
            Button {
                id: prevButton
                text: "⏮"
                width: 60
                height: 60
                // ISSUE: No accessible name
                onClicked: {
                    // ISSUE: No track change announcement
                    console.log("Previous track")
                }
            }
            
            Button {
                id: nextButton
                text: "⏭"
                width: 60
                height: 60
                // ISSUE: No accessible name
                onClicked: {
                    // ISSUE: No track change announcement
                    console.log("Next track")
                }
            }
        }
        
        // ISSUE: No accessible slider
        Row {
            id: volumeRow
            anchors.top: controlRow.bottom
            anchors.left: parent.left
            anchors.margins: 20
            spacing: 10
            
            Text {
                text: "Volume:"
                color: "#666666" // ISSUE: Low contrast
                anchors.verticalCenter: parent.verticalCenter
            }
            
            Slider {
                id: volumeSlider
                width: 200
                from: 0
                to: 100
                value: currentVolume
                // ISSUE: No accessible name
                onValueChanged: {
                    currentVolume = value
                    // ISSUE: No volume change announcement
                }
            }
        }
        
        // ISSUE: Low contrast track info
        Column {
            id: trackInfo
            anchors.top: volumeRow.bottom
            anchors.left: parent.left
            anchors.margins: 20
            spacing: 5
            
            Text {
                text: currentTrack
                font.pixelSize: 18
                font.bold: true
                color: "#777777" // ISSUE: Low contrast
            }
            
            Text {
                text: currentArtist
                font.pixelSize: 14
                color: "#999999" // ISSUE: Very low contrast
            }
        }
        
        // ISSUE: Flashing status indicators - seizure risk
        Row {
            id: statusRow
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.margins: 20
            spacing: 15
            
            Rectangle {
                id: wifiStatus
                width: 80
                height: 30
                color: "#4CAF50"
                radius: 15
                
                // ISSUE: Seizure-inducing animation
                SequentialAnimation on opacity {
                    running: true
                    loops: Animation.Infinite
                    NumberAnimation { to: 0; duration: 500 }
                    NumberAnimation { to: 1; duration: 500 }
                }
                
                Text {
                    text: "WiFi"
                    color: "white"
                    anchors.centerIn: parent
                    font.pixelSize: 12
                }
            }
            
            Rectangle {
                id: bluetoothStatus
                width: 80
                height: 30
                color: "#2196F3"
                radius: 15
                
                // ISSUE: Pulsing animation
                SequentialAnimation on opacity {
                    running: true
                    loops: Animation.Infinite
                    NumberAnimation { to: 0.3; duration: 1000 }
                    NumberAnimation { to: 1; duration: 1000 }
                }
                
                Text {
                    text: "BT"
                    color: "white"
                    anchors.centerIn: parent
                    font.pixelSize: 12
                }
            }
        }
    }
    
    // ISSUE: No keyboard navigation support
    Keys.onPressed: {
        switch(event.key) {
            case Qt.Key_Space:
                isPlaying = !isPlaying
                break
            case Qt.Key_Left:
                // Previous track
                break
            case Qt.Key_Right:
                // Next track
                break
            case Qt.Key_Up:
                currentVolume = Math.min(currentVolume + 5, 100)
                break
            case Qt.Key_Down:
                currentVolume = Math.max(currentVolume - 5, 0)
                break
        }
    }
    
    // ISSUE: No focus management
    Component.onCompleted: {
        // ISSUE: No initial focus set
        console.log("Media Player loaded")
    }
}
