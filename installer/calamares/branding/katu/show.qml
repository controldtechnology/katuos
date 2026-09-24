/* Katu OS — Calamares Installation Slideshow
   Slides informativos durante a instalação — PT-BR amigável
   Paleta: #041F16 / #0F7B43 / #E0B146                        */

import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: slideshow

    property color katuGreen:  "#0F7B43"
    property color katuAmber:  "#E0B146"
    property color katuBg:     "#041F16"
    property color katuBgAlt:  "#063723"
    property color katuText:   "#F4F1E2"
    property color katuMuted:  "#C2CBBF"
    property color katuBorder: "#326149"
    property color katuLink:   "#F0CC6C"

    // Cada slide tem: imagem de fundo + título + descrição
    property var slideData: [
        {
            img:   "slide-01.png",
            titulo: "Bem-vindo ao Katu OS!",
            desc:  "Uma experiência brasileira para estudar, trabalhar e criar."
        },
        {
            img:   "slide-02.png",
            titulo: "Simples e fácil",
            desc:  "Uma experiência clara para você começar a usar o Katu OS."
        },
        {
            img:   "slide-03.png",
            titulo: "Aplicativos essenciais",
            desc:  "Encontre ferramentas para navegar, estudar, trabalhar e criar."
        },
        {
            img:   "slide-04.png",
            titulo: "Seguro e atualizado",
            desc:  "Mantenha seu sistema protegido com atualizações regulares."
        },
        {
            img:   "slide-05.png",
            titulo: "Brasil no nosso DNA",
            desc:  "Uma identidade própria inspirada na diversidade brasileira."
        },
        {
            img:   "slide-06.png",
            titulo: "Software livre",
            desc:  "Liberdade para conhecer, compartilhar e transformar tecnologia."
        }
    ]

    Rectangle {
        anchors.fill: parent
        color: katuBg

        // Linha accent topo
        Rectangle {
            anchors { top: parent.top; left: parent.left; right: parent.right }
            height: 3
            color: katuGreen
            z: 20
        }

        // Área de imagem (metade superior)
        Item {
            id: areaImagem
            anchors { top: parent.top; left: parent.left; right: parent.right }
            height: parent.height * 0.55

            SwipeView {
                id: swipeView
                anchors.fill: parent
                currentIndex: 0

                Repeater {
                    model: slideData

                    Item {
                        Image {
                            anchors.fill: parent
                            source: modelData.img
                            fillMode: Image.PreserveAspectCrop
                            asynchronous: true
                            smooth: true

                            Rectangle {
                                anchors.fill: parent
                                color: katuBg
                                opacity: 0.10
                            }
                        }
                    }
                }
            }
        }

        // Área de texto (metade inferior)
        Rectangle {
            id: areaTexto
            anchors {
                top: areaImagem.bottom
                left: parent.left
                right: parent.right
                bottom: parent.bottom
            }
            color: katuBg

            Column {
                anchors {
                    fill: parent
                    margins: 36
                    topMargin: 28
                }
                spacing: 12

                // Número do slide
                Text {
                    text: (swipeView.currentIndex + 1) + " / " + slideData.length
                    color: katuGreen
                    font.pixelSize: 12
                    font.family: "Noto Sans"
                    font.letterSpacing: 1
                }

                // Título do slide
                Text {
                    id: tituloSlide
                    width: parent.width
                    text: slideData[swipeView.currentIndex] ? slideData[swipeView.currentIndex].titulo : ""
                    color: katuText
                    font.pixelSize: 22
                    font.family: "Noto Sans"
                    font.weight: Font.Bold
                    wrapMode: Text.WordWrap

                    Behavior on text {
                        SequentialAnimation {
                            NumberAnimation { target: tituloSlide; property: "opacity"; to: 0; duration: 150 }
                            PropertyAction { }
                            NumberAnimation { target: tituloSlide; property: "opacity"; to: 1; duration: 200 }
                        }
                    }
                }

                // Descrição
                Text {
                    id: descSlide
                    width: parent.width
                    text: slideData[swipeView.currentIndex] ? slideData[swipeView.currentIndex].desc : ""
                    color: katuMuted
                    font.pixelSize: 14
                    font.family: "Noto Sans"
                    lineHeight: 1.5
                    wrapMode: Text.WordWrap

                    Behavior on text {
                        SequentialAnimation {
                            NumberAnimation { target: descSlide; property: "opacity"; to: 0; duration: 150 }
                            PropertyAction { }
                            NumberAnimation { target: descSlide; property: "opacity"; to: 1; duration: 200 }
                        }
                    }
                }
            }

            // Indicadores pill na base
            Row {
                anchors {
                    bottom: parent.bottom
                    horizontalCenter: parent.horizontalCenter
                    bottomMargin: 20
                }
                spacing: 8

                Repeater {
                    model: slideData.length

                    Rectangle {
                        width:  swipeView.currentIndex === index ? 32 : 8
                        height: 4
                        radius: 2
                        color:  swipeView.currentIndex === index ? katuGreen : katuBorder
                        Behavior on width { NumberAnimation { duration: 200; easing.type: Easing.OutCubic } }
                        Behavior on color { ColorAnimation { duration: 200 } }
                    }
                }
            }
        }
    }

    // Auto-avanço a cada 7 segundos
    Timer {
        interval: 7000
        running: true
        repeat: true
        onTriggered: {
            var next = swipeView.currentIndex + 1
            swipeView.currentIndex = next < swipeView.count ? next : 0
        }
    }
}
