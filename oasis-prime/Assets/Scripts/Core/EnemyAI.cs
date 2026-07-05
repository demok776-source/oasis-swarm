using UnityEngine;
using UnityEngine.AI;

namespace OasisPrime.Core
{
    [RequireComponent(typeof(NavMeshAgent))]
    public class EnemyAI : MonoBehaviour
    {
        public Transform target;
        public float detectionRange = 20f;
        
        private NavMeshAgent agent;

        void Start()
        {
            agent = GetComponent<NavMeshAgent>();
            if (target == null)
            {
                target = GameObject.FindGameObjectWithTag("Player").transform;
            }
        }

        void Update()
        {
            if (target != null && Vector3.Distance(transform.position, target.position) <= detectionRange)
            {
                agent.SetDestination(target.position);
            }
        }
    }
}
