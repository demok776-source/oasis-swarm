using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

namespace Oasis.Prime.Network
{
    /// <summary>
    /// Connects OASIS PRIME and AEROSPACE modules directly to the FastAPI Sync Layer.
    /// Acts as an API Gateway: FastAPI routes high-velocity events (like DRONE_TELEMETRY_UPDATE)
    /// directly into the Apache Kafka stream `telemetry.aerospace`.
    /// </summary>
    public class TelemetrySyncSystem : MonoBehaviour
    {
        public string apiUrl = "http://127.0.0.1:8080/sync/publish";

        public void SendTelemetry(string module, string eventName, string payloadJson)
        {
            StartCoroutine(PostTelemetry(module, eventName, payloadJson));
        }

        private IEnumerator PostTelemetry(string module, string eventName, string payloadJson)
        {
            string json = $"{{\"module\":\"{module}\",\"event\":\"{eventName}\",\"payload\":{payloadJson}}}";
            
            using (UnityWebRequest www = UnityWebRequest.Post(apiUrl, json, "application/json"))
            {
                yield return www.SendWebRequest();

                if (www.result != UnityWebRequest.Result.Success)
                {
                    Debug.LogError($"[SYNC LAYER ERROR] {www.error}");
                }
                else
                {
                    Debug.Log($"[SYNC LAYER] Successfully published {eventName} to {module}");
                }
            }
        }
        
        // Simulating drone aerospace telemetry loop
        private void Start()
        {
            InvokeRepeating(nameof(SimulateDroneTelemetry), 1f, 5f);
        }
        
        private void SimulateDroneTelemetry()
        {
            string payload = $"{{\"altitude\": {Random.Range(100f, 500f):F2}, \"velocity\": {Random.Range(10f, 50f):F2}}}";
            SendTelemetry("AEROSPACE_DIV", "DRONE_TELEMETRY_UPDATE", payload);
        }
    }
}
