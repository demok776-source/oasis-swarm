import Navbar from "@/components/layout/Navbar";
import Hero from "@/components/layout/Hero";
import Scene from "@/components/canvas/Scene";

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col relative bg-void">
      <Scene />
      <Navbar />
      <Hero />
    </main>
  );
}
