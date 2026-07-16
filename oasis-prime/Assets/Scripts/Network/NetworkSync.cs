using System;
using UnityEngine;
using NativeWebSocket; // https://github.com/endel/NativeWebSocket (UPM: com.endel.nativewebsocket)

namespace OasisPrime.Network
{
    /// <summary>
    /// Real-time link between OASIS PRIME (Unity) and the app-tier Sync Layer
    /// WebSocket endpoint (`/sync/ws`, see app-tier/src/routes/sync.py).
    ///
    /// Previously this class was a fully commented-out stub -- every
    /// NativeWebSocket call was disabled, so `SendPlayerMoveEvent` only ever
    /// logged to the console and never actually reached app-tier. This
    /// version wires up a real NativeWebSocket connection.
    ///
    /// IMPORTANT / UNVERIFIED: written without access to a Unity Editor or
    /// the NativeWebSocket package in this environment, so it has NOT been
    /// compiled or run. Add the package via Package Manager -> Add package
    /// from git URL -> https://github.com/endel/NativeWebSocket.git#upm
    /// before trusting this in a build.
    /// </summary>
    public class NetworkSync : MonoBehaviour
    {
        public static NetworkSync Instance { get; private set; }

        [Header("Connection")]
        // NOTE: previously had an extra "/unity_client_01" path segment that
        // doesn't match any FastAPI route -- the real endpoint is exactly
        // /sync/ws (router prefix "/sync" + @router.websocket("/ws")).
        public string websocketUrl = "ws://localhost:8081/sync/ws";
        public float reconnectDelaySeconds = 3f;

        private WebSocket websocket;
        private bool intentionalClose = false;

        void Awake()
        {
            if (Instance == null) { Instance = this; DontDestroyOnLoad(gameObject); }
            else { Destroy(gameObject); return; }
        }

        async void Start()
        {
            Application.runInBackground = true; // keep the socket alive when the window loses focus
            await ConnectAsync();
        }

        private async System.Threading.Tasks.Task ConnectAsync()
        {
            Debug.Log($"[OASIS PRIME] Connecting Neural Link to app-tier at {websocketUrl}...");
            websocket = new WebSocket(websocketUrl);

            websocket.OnOpen += () => Debug.Log("[OASIS PRIME] Sync Layer connection open.");
            websocket.OnError += (e) => Debug.LogError($"[OASIS PRIME] WebSocket error: {e}");
            websocket.OnMessage += HandleIncomingMessage;
            websocket.OnClose += async (code) =>
            {
                Debug.LogWarning($"[OASIS PRIME] Sync Layer connection closed (code {code}).");
                if (!intentionalClose)
                {
                    await System.Threading.Tasks.Task.Delay(TimeSpan.FromSeconds(reconnectDelaySeconds));
                    await ConnectAsync();
                }
            };

            await websocket.Connect();
        }

        private void HandleIncomingMessage(byte[] bytes)
        {
            string message = System.Text.Encoding.UTF8.GetString(bytes);
            Debug.Log($"[OASIS PRIME] Received Sync Layer event: {message}");
            // TODO: route parsed events (module/event/payload) to the
            // relevant in-game systems, e.g. JsonUtility.FromJson<SyncEvent>(message).
        }

        public async void SendPlayerMoveEvent(Vector3 position)
        {
            if (websocket == null || websocket.State != WebSocketState.Open)
            {
                Debug.LogWarning("[OASIS PRIME] Cannot send player_move: socket not open.");
                return;
            }
            string payload = $"{{\"event\":\"player_move\", \"data\": {{\"x\": {position.x}, \"y\": {position.y}, \"z\": {position.z}}}}}";
            await websocket.SendText(payload);
        }

        void Update()
        {
#if !UNITY_WEBGL || UNITY_EDITOR
            websocket?.DispatchMessageQueue();
#endif
        }

        private async void OnApplicationQuit()
        {
            intentionalClose = true;
            if (websocket != null)
            {
                await websocket.Close();
            }
        }
    }
}
