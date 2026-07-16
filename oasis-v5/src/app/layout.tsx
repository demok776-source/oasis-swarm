import type { Metadata } from "next";
// Self-hosted fonts (@fontsource) instead of next/font/google: next/font/google
// fetches font files from fonts.googleapis.com at *build* time, which breaks
// builds in network-restricted CI/offline environments. @fontsource ships the
// woff2 files in the npm package itself, so the build has zero external
// network dependency. Font-family names are unchanged ("Space Grotesk" /
// "JetBrains Mono"), so the --font-sans / --font-mono tokens in globals.css
// still resolve correctly — nothing else needs to change.
import "@fontsource/space-grotesk/latin.css";
import "@fontsource/jetbrains-mono/latin.css";
import "./globals.css";
import CustomCursor from "@/components/layout/CustomCursor";

export const metadata: Metadata = {
  title: "OASIS SYSTEM CORE v∞",
  description: "13-module autonomous ecosystem & multi-layer workstation optimizer.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        <div className="noise-overlay" />
        <CustomCursor />
        {children}
      </body>
    </html>
  );
}
