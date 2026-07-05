using System;
using UnityEngine;
// Note: In a real project, we would use a WebSocket library like NativeWebSocket
// using NativeWebSocket;

namespace OasisPrime.Network
{
    public class NetworkSync : MonoBehaviour
    {
        public static NetworkSync Instance { get; private set; }
        
        public string websocketUrl = "ws://localhost:8080/sync/ws/unity_client_01";
        // private WebSocket websocket;

        void Awake()
        {
            if (Instance == null) { Instance = this; DontDestroyOnLoad(gameObject); }
            else { Destroy(gameObject); }
        }

        async void Start()
        {
            Debug.Log($"[OASIS PRIME] Initializing Neural Link to App-Tier at {websocketUrl}...");
            // websocket = new WebSocket(websocketUrl);
            // websocket.OnMessage += (bytes) => { Debug.Log("Received Event: " + System.Text.Encoding.UTF8.GetString(bytes)); };
            // await websocket.Connect();
        }

        public void SendPlayerMoveEvent(Vector3 position)
        {
            string payload = $"{{\"event\":\"player_move\", \"data\": {{\"x\": {position.x}, \"y\": {position.y}, \"z\": {position.z}}}}}";
            // if (websocket.State == WebSocketState.Open) { await websocket.SendText(payload); }
            Debug.Log($"[SYNC] Emitting payload: {payload}");
        }

        void Update()
        {
            // #if !UNITY_WEBGL || UNITY_EDITOR
            // websocket.DispatchMessageQueue();
            // #endif
        }

        private async void OnApplicationQuit()
        {
            // await websocket.Close();
        }
    }
}
