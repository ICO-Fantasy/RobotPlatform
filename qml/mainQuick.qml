import QtQuick 2.15
import QtQuick.Controls 2.15

ApplicationWindow {
    visible: true
    width: 400
    height: 300
    title: "Qt Quick Example"

    Rectangle {
        width: 200
        height: 100
        color: "lightblue"
        anchors.centerIn: parent

        Text {
            anchors.centerIn: parent
            text: "Hello, Qt Quick!"
            font.pixelSize: 16
            color: "white"
        }

        MouseArea {
            anchors.fill: parent
            onClicked: {
                console.log("Rectangle Clicked!");
            }
        }
    }
}
