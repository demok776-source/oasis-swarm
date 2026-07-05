"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

export default function CustomCursor() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isVisible, setIsVisible] = useState(false);
  
  useEffect(() => {
    const updateMousePosition = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
      if (!isVisible) setIsVisible(true);
    };
    
    window.addEventListener("mousemove", updateMousePosition);
    return () => window.removeEventListener("mousemove", updateMousePosition);
  }, [isVisible]);

  if (!isVisible) return null;

  return (
    <>
      <motion.div
        className="fixed top-0 left-0 w-[6px] h-[6px] bg-[#00a2e8] rounded-full pointer-events-none z-[9999]"
        style={{
          boxShadow: "0 0 10px #00a2e8, 0 0 20px #6366f1"
        }}
        animate={{
          x: mousePosition.x - 3,
          y: mousePosition.y - 3,
        }}
        transition={{ type: "tween", ease: "linear", duration: 0 }}
      />
      <motion.div
        className="fixed top-0 left-0 w-7 h-7 border border-[#00a2e8]/30 rounded-full pointer-events-none z-[9998]"
        animate={{
          x: mousePosition.x - 14,
          y: mousePosition.y - 14,
        }}
        transition={{ type: "spring", stiffness: 200, damping: 20, mass: 0.2 }}
      />
    </>
  );
}
