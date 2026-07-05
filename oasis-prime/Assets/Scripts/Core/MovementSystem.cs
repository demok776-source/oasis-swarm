using Unity.Burst;
using Unity.Entities;
using Unity.Transforms;
using Unity.Mathematics;

namespace Oasis.Prime.Core
{
    [BurstCompile]
    public partial struct MovementSystem : ISystem
    {
        [BurstCompile]
        public void OnCreate(ref SystemState state)
        {
            state.RequireForUpdate<MovementComponent>();
        }

        [BurstCompile]
        public void OnUpdate(ref SystemState state)
        {
            float dt = SystemAPI.Time.DeltaTime;

            foreach (var (transform, movement) in SystemAPI.Query<RefRW<LocalTransform>, RefRO<MovementComponent>>())
            {
                transform.ValueRW = transform.ValueRO.Translate(movement.ValueRO.Velocity * dt);
            }
        }
    }

    public struct MovementComponent : IComponentData
    {
        public float3 Velocity;
    }
}
