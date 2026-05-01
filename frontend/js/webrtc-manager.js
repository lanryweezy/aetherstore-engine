/**
 * WebRTC Manager for Aetherstore Engine
 * Handles establishing peer-to-peer audio connections for spatial voice chat.
 */

class WebRTCManager {
    constructor(userId, websocket) {
        this.userId = userId;
        this.ws = websocket;
        this.peers = new Map(); // other_user_id -> RTCPeerConnection
        this.localStream = null;

        // STUN servers help peers find each other across firewalls/NATs
        this.iceServers = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' }
            ]
        };

        // Event listener for when a new remote stream is fully connected
        this.onTrackCallback = null;
    }

    /**
     * Request microphone access and save the local stream
     */
    async enableMicrophone() {
        try {
            this.localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
            console.log("Microphone enabled.");
            return true;
        } catch (err) {
            console.error("Error accessing microphone:", err);
            return false;
        }
    }

    /**
     * Call this when a new user joins the room. We (the existing user) initiate the offer.
     */
    async initiateCall(targetUserId) {
        if (!this.localStream) return;

        const peerConnection = this.createPeerConnection(targetUserId);

        // Add our microphone tracks to the connection
        this.localStream.getTracks().forEach(track => {
            peerConnection.addTrack(track, this.localStream);
        });

        // Create the WebRTC offer
        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);

        // Send the offer via WebSocket signaling
        this.ws.send(JSON.stringify({
            type: "webrtc_offer",
            target_user_id: targetUserId,
            payload: offer
        }));
    }

    /**
     * Handle an incoming WebRTC Offer from a remote peer
     */
    async handleOffer(senderUserId, offerPayload) {
        if (!this.localStream) return; // If we don't have mic on, we can't join the call yet

        const peerConnection = this.createPeerConnection(senderUserId);

        // Add our tracks
        this.localStream.getTracks().forEach(track => {
            peerConnection.addTrack(track, this.localStream);
        });

        // Accept the offer
        await peerConnection.setRemoteDescription(new RTCSessionDescription(offerPayload));

        // Create an answer
        const answer = await peerConnection.createAnswer();
        await peerConnection.setLocalDescription(answer);

        // Send the answer back
        this.ws.send(JSON.stringify({
            type: "webrtc_answer",
            target_user_id: senderUserId,
            payload: answer
        }));
    }

    /**
     * Handle an incoming WebRTC Answer
     */
    async handleAnswer(senderUserId, answerPayload) {
        const peerConnection = this.peers.get(senderUserId);
        if (peerConnection) {
            await peerConnection.setRemoteDescription(new RTCSessionDescription(answerPayload));
        }
    }

    /**
     * Handle incoming ICE candidates (network routing info)
     */
    async handleIceCandidate(senderUserId, candidatePayload) {
        const peerConnection = this.peers.get(senderUserId);
        if (peerConnection) {
            try {
                await peerConnection.addIceCandidate(new RTCIceCandidate(candidatePayload));
            } catch (e) {
                console.error("Error adding received ice candidate", e);
            }
        }
    }

    /**
     * Helper to setup a standard RTCPeerConnection
     */
    createPeerConnection(targetUserId) {
        const peerConnection = new RTCPeerConnection(this.iceServers);
        this.peers.set(targetUserId, peerConnection);

        // When we discover our own ICE candidates, send them to the peer
        peerConnection.onicecandidate = (event) => {
            if (event.candidate) {
                this.ws.send(JSON.stringify({
                    type: "webrtc_ice_candidate",
                    target_user_id: targetUserId,
                    payload: event.candidate
                }));
            }
        };

        // When we successfully receive the other person's audio stream
        peerConnection.ontrack = (event) => {
            console.log(`Received audio stream from ${targetUserId}`);
            const remoteStream = event.streams[0];
            if (this.onTrackCallback) {
                this.onTrackCallback(targetUserId, remoteStream);
            }
        };

        // Handle disconnections
        peerConnection.oniceconnectionstatechange = () => {
            if (peerConnection.iceConnectionState === 'disconnected' || peerConnection.iceConnectionState === 'closed') {
                this.disconnectPeer(targetUserId);
            }
        };

        return peerConnection;
    }

    /**
     * Clean up a disconnected user
     */
    disconnectPeer(userId) {
        const pc = this.peers.get(userId);
        if (pc) {
            pc.close();
            this.peers.delete(userId);
            console.log(`Disconnected WebRTC peer: ${userId}`);
        }
    }

    /**
     * Clean up all connections if we leave the room
     */
    dispose() {
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
        }
        for (let [userId, pc] of this.peers.entries()) {
            pc.close();
        }
        this.peers.clear();
    }
}

// Export as a global for use in other scripts
if (typeof window !== 'undefined') {
    window.WebRTCManager = WebRTCManager;
}