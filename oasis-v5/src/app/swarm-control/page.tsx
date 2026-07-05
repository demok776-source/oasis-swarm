"use client";
import { useRef, useMemo, useEffect, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Stars } from "@react-three/drei";
import * as THREE from "three";
import { motion } from "framer-motion";

function DroneSwarm() {
  const count = 5000;
  const mesh = useRef<THREE.InstancedMesh>(null);
  
  const dummy = useMemo(() => new THREE.Object3D(), []);
  
  // Generate random initial positions
  const particles = useMemo(() => {
    const temp = [];
    for (let i = 0; i < count; i++) {
      const t = Math.random() * 100;
      const factor = 20 + Math.random() * 100;
      const speed = 0.01 + Math.random() / 200;
      const xFactor = -50 + Math.random() * 100;
      const yFactor = -50 + Math.random() * 100;
      const zFactor = -50 + Math.random() * 100;
      temp.push({ t, factor, speed, xFactor, yFactor, zFactor, mx: 0, my: 0 });
    }
    return temp;
  }, [count]);

  const [offset, setOffset] = useState({ x: 0, y: 0, z: 0 });

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8765");
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "SWARM_FRAME") {
          setOffset({
            x: data.global_offset[0],
            y: data.global_offset[1],
            z: data.global_offset[2]
          });
        }
      } catch(e) {}
    };
    return () => ws.close();
  }, []);

  useFrame(() => {
    if (!mesh.current) return;
    particles.forEach((particle, i) => {
      let { t, factor, speed, xFactor, yFactor, zFactor } = particle;
      t = particle.t += speed / 2;
      const a = Math.cos(t) + Math.sin(t * 1) / 10;
      const b = Math.sin(t) + Math.cos(t * 2) / 10;
      const s = Math.cos(t);

      dummy.position.set(
        offset.x + (particle.mx / 10) * a + xFactor + Math.cos((t / 10) * factor) + (Math.sin(t * 1) * factor) / 10,
        offset.y + (particle.my / 10) * b + yFactor + Math.sin((t / 10) * factor) + (Math.cos(t * 2) * factor) / 10,
        offset.z + (particle.my / 10) * b + zFactor + Math.cos((t / 10) * factor) + (Math.sin(t * 3) * factor) / 10
      );
      dummy.scale.set(s, s, s);
      dummy.rotation.set(s * 5, s * 5, s * 5);
      dummy.updateMatrix();
      mesh.current!.setMatrixAt(i, dummy.matrix);
    });
    mesh.current.instanceMatrix.needsUpdate = true;
  });

  return (
    <instancedMesh ref={mesh} args={[undefined, undefined, count]}>
      <sphereGeometry args={[0.2, 8, 8]} />
      <meshStandardMaterial color="#00ffcc" toneMapped={false} emissive="#00ffcc" emissiveIntensity={2} />
    </instancedMesh>
  );
}

export default function SwarmControlPage() {
  return (
    <div className="pt-[100px] px-12 max-w-[1400px] mx-auto min-h-screen text-slate-300 relative">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-4 relative z-10 pointer-events-none">
        <h1 className="text-4xl font-bold tracking-tight text-white mb-2 font-mono">
          SWARM <span className="text-sx-cyan">CONTROL (WebGPU)</span>
        </h1>
        <p className="text-slate-500 font-mono text-xs uppercase tracking-widest">
          Live Volumetric Fleet Tracking - {5000} Active Agents
        </p>
      </motion.div>
      
      <div className="absolute inset-0 pt-[150px] pb-12 px-12 z-0">
        <div className="border border-sx-cyan/20 bg-black/80 w-full h-full rounded-lg overflow-hidden relative shadow-[0_0_50px_rgba(0,255,204,0.1)]">
          <Canvas camera={{ position: [0, 0, 150], fov: 75 }}>
            <ambientLight intensity={0.5} />
            <pointLight position={[10, 10, 10]} />
            <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
            <DroneSwarm />
            <OrbitControls autoRotate autoRotateSpeed={0.5} enablePan={false} />
          </Canvas>
          <div className="absolute top-4 right-4 font-mono text-xs text-sx-cyan animate-pulse bg-black/50 px-3 py-1 rounded border border-sx-cyan/30">
            [ KAFKA STREAM: ONLINE ]
          </div>
        </div>
      </div>
    </div>
  );
}
