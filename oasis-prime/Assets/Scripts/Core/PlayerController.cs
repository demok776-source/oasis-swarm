using UnityEngine;

namespace OasisPrime.Core
{
    [RequireComponent(typeof(CharacterController))]
    public class PlayerController : MonoBehaviour
    {
        public float moveSpeed = 5f;
        public float mouseSensitivity = 2f;
        public Camera playerCamera;

        private CharacterController controller;
        private float verticalRotation = 0f;

        void Start()
        {
            controller = GetComponent<CharacterController>();
            Cursor.lockState = CursorLockMode.Locked;
        }

        void Update()
        {
            // Camera Look
            float mouseX = Input.GetAxis("Mouse X") * mouseSensitivity;
            float mouseY = Input.GetAxis("Mouse Y") * mouseSensitivity;

            verticalRotation -= mouseY;
            verticalRotation = Mathf.Clamp(verticalRotation, -90f, 90f);
            
            playerCamera.transform.localRotation = Quaternion.Euler(verticalRotation, 0f, 0f);
            transform.Rotate(Vector3.up * mouseX);

            // Movement
            float forward = Input.GetAxis("Vertical");
            float right = Input.GetAxis("Horizontal");

            Vector3 move = transform.right * right + transform.forward * forward;
            controller.Move(move * moveSpeed * Time.deltaTime);
            
            // Sync Position to Network Event Bus
            if (move.magnitude > 0.1f)
            {
                Network.NetworkSync.Instance.SendPlayerMoveEvent(transform.position);
            }
        }
    }
}
