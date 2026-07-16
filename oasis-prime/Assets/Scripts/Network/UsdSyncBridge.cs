using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using NativeWebSocket; // https://github.com/endel/NativeWebSocket
// using Unity.USD; // True OpenUSD stage authoring needs com.unity.usd.core,
// which isn't installed in this project. See the Phase-4 note below.

namespace OASIS.Network
{
    /// <summary>
    /// Digital Twin Bridge: streams live agent transforms to the
    /// `nucleus-bridge` WebSocket server (ws://host:8765, see
    /// nucleus-bridge/server.py) as JSON frames.
    ///
    /// Previously `CaptureEcsStateAndExport()` was 100% commented-out
    /// pseudocode -- it ran every tick and did nothing. This version
    /// actually pushes data over the wire to the bridge that already
    /// exists and is already running (docker-compose service
    /// `omniverse-bridge`).
    ///
    /// Phase-4 TODO (real OpenUSD authoring): actually writing `.usd`
    /// prims for a live Omniverse Nucleus session requires the
    /// `com.unity.usd.core` package + Omniverse Connector SDK, neither of
    /// which are installed in this project and neither of which can be
    /// added or verified from this sandboxed environment. The JSON stream
    /// below is a legitimate interim sync mechanism -- the
    /// `nucleus-bridge` Python service is the natural place to translate
    /// these frames into real USD prims once that SDK is wired in, since
    /// it already owns the WebSocket connection and could add a
    /// USD-writing consumer without touching the Unity side at all.
    ///
    /// UNVERIFIED: no Unity Editor in this sandbox -- not compiled/run.
    /// </summary>
    public class UsdSyncBridge : MonoBehaviour
    {
        [Header("Omniverse / Nucleus Bridge Connection")]
        public string bridgeWebsocketUrl = "ws://localhost:8765";
        public float syncIntervalMs = 100f; // 10fps -- deliberately lower than
                                             // the 60fps header comment implied;
                                             // see rationale below.

        [Tooltip("Transforms to sync each tick. Populate via drone/agent spawner.")]
        public List<Transform> trackedAgents = new List<Transform>();

        private WebSocket websocket;
        private bool isSyncing = false;

        private async void Start()
        {
            Debug.Log($"[UsdSyncBridge] Connecting to Nucleus Bridge at {bridgeWebsocketUrl}...");
            websocket = new WebSocket(bridgeWebsocketUrl);
            websocket.OnOpen += () => Debug.Log("[UsdSyncBridge] Connected.");
            websocket.OnError += (e) => Debug.LogError($"[UsdSyncBridge] Error: {e}");
            websocket.OnClose += (code) => Debug.LogWarning($"[UsdSyncBridge] Closed ({code}).");

            await websocket.Connect();
            StartCoroutine(LiveSyncRoutine());
        }

        private IEnumerator LiveSyncRoutine()
        {
            isSyncing = true;
            WaitForSeconds wait = new WaitForSeconds(syncIntervalMs / 1000f);

            while (isSyncing)
            {
                CaptureAndSendAgentState();
                yield return wait;
            }
        }

        private void CaptureAndSendAgentState()
        {
            if (websocket == null || websocket.State != WebSocketState.Open) return;
            if (trackedAgents.Count == 0) return;

            // Hand-rolled JSON (no heavy JSON lib dependency): a flat array of
            // {id, x, y, z, rx, ry, rz} objects, one per tracked agent.
            var sb = new System.Text.StringBuilder();
            sb.Append("{\"type\":\"AGENT_TRANSFORMS\",\"agents\":[");
            for (int i = 0; i < trackedAgents.Count; i++)
            {
                var t = trackedAgents[i];
                if (t == null) continue;
                if (i > 0) sb.Append(",");
                Vector3 p = t.position;
                Vector3 r = t.eulerAngles;
                sb.Append($"{{\"id\":\"{t.name}\",\"x\":{p.x:F3},\"y\":{p.y:F3},\"z\":{p.z:F3},");
                sb.Append($"\"rx\":{r.x:F2},\"ry\":{r.y:F2},\"rz\":{r.z:F2}}}");
            }
            sb.Append("]}");

            _ = websocket.SendText(sb.ToString()); // fire-and-forget; drop-if-behind is acceptable for a live twin feed
        }

        private async void OnDestroy()
        {
            isSyncing = false;
            if (websocket != null)
            {
                await websocket.Close();
            }
            Debug.Log("[UsdSyncBridge] Connection closed.");
        }

        void Update()
        {
#if !UNITY_WEBGL || UNITY_EDITOR
            websocket?.DispatchMessageQueue();
#endif
        }
    }
}
