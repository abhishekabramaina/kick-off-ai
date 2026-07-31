import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Kickoff AI",
  description: "AI-Assisted Project Kickoff and Resourcing",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <nav>
          <Link href="/" className="logo">Kickoff AI</Link>
          <div>
            <Link href="/projects">Projects</Link>
            <Link href="/bench">Talent</Link>
          </div>
        </nav>
        <main className="container">
          {children}
        </main>
      </body>
    </html>
  );
}
