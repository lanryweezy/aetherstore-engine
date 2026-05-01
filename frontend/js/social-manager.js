/**
 * SocialManager
 * Connects WebSockets, WebRTC, and Babylon.js to create the fully functional
 * multiplayer 3D store experience with Spatial Audio.
 */

class SocialManager {
    constructor(roomId, userId, babylonEngine) {
        this.roomId = roomId;
        this.userId = userId;
        this.engine = babylonEngine;

        // Connect WebSocket
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host || 'localhost:8000';
        this.ws = new WebSocket(`${protocol}//${host}/ws/social/${roomId}/${userId}`);

        // Initialize WebRTC
        this.webrtc = null;
        if (typeof window.WebRTCManager !== 'undefined') {
            this.webrtc = new window.WebRTCManager(userId, this.ws);

            // Wire WebRTC Audio directly into Babylon.js!
            this.webrtc.onTrackCallback = (remoteUserId, stream) => {
                this.engine.attachSpatialAudioStream(remoteUserId, stream);
            };
        }

        this.setupWebSocket();
    }

    setupWebSocket() {
        this.ws.onopen = async () => {
            console.log(`Connected to social room ${this.roomId}`);

            if (this.webrtc) {
                const micEnabled = await this.webrtc.enableMicrophone();
                if (!micEnabled) {
                    console.warn("Microphone access denied. Spatial audio disabled.");
                }
            }
        };

        this.ws.onmessage = async (event) => {
            const data = JSON.parse(event.data);

            switch (data.type) {
                case 'presence':
                    if (data.status === 'joined' && data.user_id !== this.userId) {
                        console.log(`${data.user_id} joined the room!`);
                        // Spawn them in the 3D world
                        this.engine.updateRemoteAvatar(data.user_id, {
                            position: {x: 0, y: 0, z: 0},
                            rotation: {x: 0, y: 0, z: 0}
                        });

                        // We initiate a WebRTC call to the newcomer
                        if (this.webrtc) {
                            await this.webrtc.initiateCall(data.user_id);
                        }
                    } else if (data.status === 'left') {
                        console.log(`${data.user_id} left the room.`);
                        this.engine.removeRemoteAvatar(data.user_id);
                        if (this.webrtc) {
                            this.webrtc.disconnectPeer(data.user_id);
                        }
                    }
                    break;

                case 'transform':
                    if (data.user_id !== this.userId) {
                        this.engine.updateRemoteAvatar(data.user_id, data);
                    }
                    break;

                // WebRTC Signaling Events routed from the backend
                case 'webrtc_offer':
                    if (this.webrtc) await this.webrtc.handleOffer(data.user_id, data.payload);
                    break;
                case 'webrtc_answer':
                    if (this.webrtc) await this.webrtc.handleAnswer(data.user_id, data.payload);
                    break;
                case 'webrtc_ice_candidate':
                    if (this.webrtc) await this.webrtc.handleIceCandidate(data.user_id, data.payload);
                    break;
            }
        };
    }

    // Broadcast our own avatar's position to the room
    sendTransform(position, rotation, animationState = 'idle') {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'transform',
                position: position,
                rotation: rotation,
                animation_state: animationState
            }));
        }
    }
}

// Export
window.SocialManager = SocialManager;
